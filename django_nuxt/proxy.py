import logging
import select
import socket
from urllib.parse import urlparse, urlunparse

import requests
from django.core.servers.basehttp import ServerHandler, WSGIRequestHandler
from django.http import HttpResponse, StreamingHttpResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests.adapters import HTTPAdapter

from django_nuxt.backends import render_nuxt_html
from django_nuxt.conf import get_nuxt_dev_server_url

logger = logging.getLogger(__name__)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

EXCLUDED_REQUEST_HEADERS = HOP_BY_HOP_HEADERS | {"content-length"}
EMPTY_BODY_STATUSES = {204, 304}

_wsgi_websocket_patched = False
_proxy_session = None


def get_proxy_session():
    """Shared HTTP client so Vite module requests reuse keep-alive connections."""
    global _proxy_session
    if _proxy_session is None:
        _proxy_session = requests.Session()
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
        _proxy_session.mount("http://", adapter)
        _proxy_session.mount("https://", adapter)
    return _proxy_session


def _rewrite_location(location, upstream_url, request):
    if not location:
        return location
    if not location.startswith("http://") and not location.startswith("https://"):
        return location
    upstream = urlparse(upstream_url)
    loc = urlparse(location)
    if loc.netloc != upstream.netloc:
        return location
    public = urlparse(request.build_absolute_uri("/"))
    return urlunparse((
        public.scheme,
        public.netloc,
        loc.path,
        loc.params,
        loc.query,
        loc.fragment,
    ))


def _devtools_listen_origin(upstream_url):
    parsed = urlparse(upstream_url) if upstream_url else None
    if not parsed or not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _forward_request_headers(request, upstream_url=None):
    headers = {}
    for name, value in request.headers.items():
        if name.lower() in EXCLUDED_REQUEST_HEADERS:
            continue
        headers[name] = value

    headers["X-Forwarded-Host"] = request.get_host()
    headers["X-Forwarded-Proto"] = request.scheme
    headers["X-Forwarded-Port"] = str(request.get_port())

    remote_addr = request.META.get("REMOTE_ADDR")
    existing_xff = request.headers.get("X-Forwarded-For")
    if existing_xff and remote_addr:
        headers["X-Forwarded-For"] = f"{existing_xff}, {remote_addr}"
    elif remote_addr:
        headers["X-Forwarded-For"] = remote_addr

    listen_origin = _devtools_listen_origin(upstream_url)
    if listen_origin and request.path.startswith("/__nuxt_devtools__"):
        for key in list(headers):
            if key.lower() == "origin":
                del headers[key]
        headers["Origin"] = listen_origin
    return headers


def _copy_response_headers(django_response, upstream_headers, upstream_url, request, skip=None):
    skip = {h.lower() for h in (skip or set())}
    skip |= HOP_BY_HOP_HEADERS
    skip.add("content-type")
    for name, value in upstream_headers.items():
        if name.lower() in skip:
            continue
        if name.lower() == "location":
            value = _rewrite_location(value, upstream_url, request)
        django_response[name] = value


def _stream_upstream(upstream):
    try:
        for chunk in upstream.iter_content(chunk_size=8192):
            if chunk:
                yield chunk
    finally:
        upstream.close()


def _maybe_exempt_devtools(request, response):
    if request.path.startswith("/__nuxt_devtools__"):
        response.xframe_options_exempt = True


def proxy_nuxt_request(request):
    """Reverse-proxy a Django request to the Nuxt development server."""
    upstream_url = get_nuxt_dev_server_url()
    if not upstream_url:
        return HttpResponse("Nuxt is not running", status=503)

    url = upstream_url.rstrip("/") + request.get_full_path()
    headers = _forward_request_headers(request, upstream_url)

    try:
        upstream = get_proxy_session().request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.body,
            stream=True,
            allow_redirects=False,
            timeout=(10, 60),
        )
    except requests.RequestException:
        return HttpResponse(f"Nuxt is not running on {upstream_url}", status=503)

    content_type = upstream.headers.get("Content-Type", "")
    if request.method == "HEAD" or upstream.status_code in EMPTY_BODY_STATUSES:
        try:
            response = HttpResponse(status=upstream.status_code, content_type=content_type or None)
            _copy_response_headers(
                response,
                upstream.headers,
                upstream_url,
                request,
                skip={"content-encoding", "content-length"},
            )
            _maybe_exempt_devtools(request, response)
            return response
        finally:
            upstream.close()

    if "text/html" in content_type and not request.path.startswith("/__nuxt_devtools__"):
        try:
            html = render_nuxt_html(upstream.text, request)
        finally:
            upstream.close()
        get_token(request)
        response = HttpResponse(html, status=upstream.status_code, content_type=content_type)
        _copy_response_headers(
            response,
            upstream.headers,
            upstream_url,
            request,
            skip={"content-encoding", "content-length"},
        )
        _maybe_exempt_devtools(request, response)
        return response

    response = StreamingHttpResponse(
        _stream_upstream(upstream),
        status=upstream.status_code,
        content_type=content_type or None,
    )
    _copy_response_headers(
        response,
        upstream.headers,
        upstream_url,
        request,
        skip={"content-encoding", "content-length"},
    )
    _maybe_exempt_devtools(request, response)
    return response


@method_decorator(csrf_exempt, name="dispatch")
class NuxtDevProxyView(View):
    """Reverse-proxy HTTP requests to the Nuxt development server."""

    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]

    def dispatch(self, request, *args, **kwargs):
        return proxy_nuxt_request(request)


def _upstream_address(upstream_url):
    parsed = urlparse(upstream_url)
    host = parsed.hostname or "127.0.0.1"
    if parsed.scheme == "https":
        port = parsed.port or 443
    else:
        port = parsed.port or 80
    return host, port


def _build_upstream_handshake(handler, upstream_url=None):
    parsed = urlparse(upstream_url) if upstream_url else None
    rewrite_devtools_origin = (
        parsed
        and parsed.netloc
        and handler.path.startswith("/__nuxt_devtools__")
    )
    nuxt_host = parsed.netloc if rewrite_devtools_origin else None
    nuxt_origin = _devtools_listen_origin(upstream_url) if rewrite_devtools_origin else None

    parts = [f"{handler.command} {handler.path} {handler.request_version}\r\n"]
    seen = set()
    for name, value in handler.headers.items():
        lower = name.lower()
        if rewrite_devtools_origin and lower == "host":
            value = nuxt_host
        if rewrite_devtools_origin and lower == "origin":
            value = nuxt_origin
        parts.append(f"{name}: {value}\r\n")
        seen.add(lower)
    host = handler.headers.get("Host", "")
    if host and "x-forwarded-host" not in seen:
        parts.append(f"X-Forwarded-Host: {host}\r\n")
    if "x-forwarded-proto" not in seen:
        parts.append("X-Forwarded-Proto: http\r\n")
    parts.append("\r\n")
    return "".join(parts).encode("iso-8859-1")


def tunnel_websocket(handler, upstream_url):
    host, port = _upstream_address(upstream_url)
    upstream = socket.create_connection((host, port), timeout=30)
    try:
        upstream.sendall(_build_upstream_handshake(handler, upstream_url))
        client = handler.connection
        sockets = [client, upstream]
        while True:
            readable, _, errored = select.select(sockets, [], sockets)
            if errored:
                break
            for sock in readable:
                other = upstream if sock is client else client
                try:
                    data = sock.recv(65536)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                    return
                if not data:
                    return
                try:
                    other.sendall(data)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                    return
    finally:
        try:
            upstream.close()
        except OSError:
            pass


def _handle_one_request_with_ws(self):
    self.raw_requestline = self.rfile.readline(65537)
    if len(self.raw_requestline) > 65536:
        self.requestline = ""
        self.request_version = ""
        self.command = ""
        self.send_error(414)
        return

    if not self.parse_request():
        return

    upgrade = self.headers.get("Upgrade", "")
    if upgrade.lower() == "websocket":
        upstream_url = get_nuxt_dev_server_url()
        if upstream_url:
            try:
                tunnel_websocket(self, upstream_url)
            except OSError:
                logger.exception("Nuxt WebSocket proxy failed")
            self.close_connection = True
            return

    handler = ServerHandler(
        self.rfile, self.wfile, self.get_stderr(), self.get_environ()
    )
    handler.request_handler = self
    handler.run(self.server.get_app())


def patch_wsgi_websocket_proxy():
    """Hijack Django runserver WebSocket upgrades and tunnel them to Nuxt."""
    global _wsgi_websocket_patched
    if _wsgi_websocket_patched:
        return
    WSGIRequestHandler.handle_one_request = _handle_one_request_with_ws
    _wsgi_websocket_patched = True
