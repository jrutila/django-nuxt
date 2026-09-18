from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase, override_settings
from grappa import should

from django_nuxt.conf import get_nuxt_dev_server_url
from django_nuxt.middleware import ASSET_MIDDLEWARE, install_asset_proxy_middleware
from django_nuxt.proxy import (
    _build_upstream_handshake,
    patch_wsgi_websocket_proxy,
    tunnel_websocket,
)
from django_nuxt.urls import NuxtCatchAllUrls, NuxtStaticUrls

NUXT_DEV_MIDDLEWARE = [
    ASSET_MIDDLEWARE,
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


def _html_upstream(body="<html><head></head><body>nuxt</body></html>", status=200, extra_headers=None):
    resp = MagicMock()
    resp.status_code = status
    headers = {"Content-Type": "text/html; charset=utf-8"}
    if extra_headers:
        headers.update(extra_headers)
    resp.headers = headers
    resp.text = body
    resp.content = body.encode()
    resp.close = MagicMock()
    return resp


def _binary_upstream(body=b"\x00\x01\x02", content_type="font/woff2", extra_headers=None, status=200):
    resp = MagicMock()
    resp.status_code = status
    headers = {"Content-Type": content_type}
    if extra_headers:
        headers.update(extra_headers)
    resp.headers = headers
    resp.content = body
    resp.iter_content = lambda chunk_size=8192: iter([body])
    resp.close = MagicMock()
    return resp


def _mock_session(mock_get_session, upstream):
    session = MagicMock()
    session.request.return_value = upstream
    mock_get_session.return_value = session
    return session


@override_settings(
    DJANGO_NUXT_SERVER_RUNNING="http://nuxt.test:3000",
    ROOT_URLCONF="tests.proxy_urls",
    MIDDLEWARE=NUXT_DEV_MIDDLEWARE,
)
class TestNuxtDevProxy(TestCase):
    @patch("django_nuxt.proxy.get_proxy_session")
    def test_html_is_proxied_without_redirect_and_injects_django_nuxt(self, mock_get_session):
        session = _mock_session(mock_get_session, _html_upstream())
        response = self.client.get("/some-page")
        response.status_code | should.be.equal.to(200)
        response.status_code | should.not_be.equal.to(302)
        str(response.content) | should.contain("window.django_nuxt")
        str(response.content) | should.contain("nuxt")
        session.request.call_args.kwargs["url"] | should.be.equal.to("http://nuxt.test:3000/some-page")
        session.request.call_args.kwargs["allow_redirects"] | should.be.equal.to(False)
        session.request.call_args.kwargs["method"] | should.be.equal.to("GET")

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_html_sets_csrf_cookie(self, mock_get_session):
        _mock_session(mock_get_session, _html_upstream())
        response = self.client.get("/")
        self.assertIn("csrftoken", response.cookies)

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_nuxt_modules_redirect_to_dev_server(self, mock_get_session):
        response = self.client.get("/_nuxt/app.js?vue=1")
        response.status_code | should.be.equal.to(302)
        response["Location"] | should.be.equal.to("http://nuxt.test:3000/_nuxt/app.js?vue=1")
        mock_get_session.assert_not_called()

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_fonts_redirect_to_dev_server(self, mock_get_session):
        response = self.client.get("/fonts/Inter.woff2")
        response.status_code | should.be.equal.to(302)
        response["Location"] | should.be.equal.to("http://nuxt.test:3000/fonts/Inter.woff2")
        mock_get_session.assert_not_called()

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_underscore_fonts_redirect_to_dev_server(self, mock_get_session):
        response = self.client.get("/_fonts/Inter.woff2")
        response.status_code | should.be.equal.to(302)
        response["Location"] | should.be.equal.to("http://nuxt.test:3000/_fonts/Inter.woff2")
        mock_get_session.assert_not_called()

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_devtools_does_not_set_csrf_cookie(self, mock_get_session):
        _mock_session(mock_get_session, _binary_upstream(b"js", "application/javascript"))
        response = self.client.get("/__nuxt_devtools__/client/app.js")
        self.assertNotIn("csrftoken", response.cookies)

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_devtools_html_is_not_injected(self, mock_get_session):
        _mock_session(
            mock_get_session,
            _binary_upstream(
                b"<html><head></head><body>devtools</body></html>",
                "text/html; charset=utf-8",
            ),
        )
        response = self.client.get("/__nuxt_devtools__/client/modules/payload")
        response.status_code | should.be.equal.to(200)
        body = b"".join(response.streaming_content)
        self.assertNotIn(b"window.django_nuxt", body)
        self.assertIn(b"devtools", body)

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_304_returns_empty_body_without_streaming(self, mock_get_session):
        upstream = MagicMock()
        upstream.status_code = 304
        upstream.headers = {"ETag": '"abc"', "Cache-Control": "no-cache"}
        upstream.iter_content = MagicMock(side_effect=AssertionError("should not stream 304"))
        upstream.close = MagicMock()
        session = _mock_session(mock_get_session, upstream)

        response = self.client.get("/__nuxt_devtools__/client/foo.js", HTTP_IF_NONE_MATCH='"abc"')
        response.status_code | should.be.equal.to(304)
        self.assertEqual(response.content, b"")
        self.assertFalse(response.streaming)
        upstream.iter_content.assert_not_called()
        response["ETag"] | should.be.equal.to('"abc"')
        session.request.call_args.kwargs["headers"]["If-None-Match"] | should.be.equal.to('"abc"')

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_forwards_host_as_x_forwarded_headers(self, mock_get_session):
        session = _mock_session(mock_get_session, _binary_upstream(b"js", "application/javascript"))
        self.client.get("/__nuxt_devtools__/client/x")
        headers = session.request.call_args.kwargs["headers"]
        headers["X-Forwarded-Host"] | should.be.equal.to("testserver")
        headers["X-Forwarded-Proto"] | should.be.equal.to("http")

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_rewrites_location_header_to_django_origin(self, mock_get_session):
        _mock_session(
            mock_get_session,
            _binary_upstream(
                b"",
                "text/plain",
                extra_headers={"Location": "http://nuxt.test:3000/other"},
                status=302,
            ),
        )
        response = self.client.get("/moved")
        response.status_code | should.be.equal.to(302)
        response["Location"] | should.be.equal.to("http://testserver/other")

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_returns_503_when_nuxt_is_down(self, mock_get_session):
        session = MagicMock()
        session.request.side_effect = requests.RequestException("down")
        mock_get_session.return_value = session
        response = self.client.get("/")
        response.status_code | should.be.equal.to(503)
        str(response.content) | should.contain("Nuxt is not running on http://nuxt.test:3000")

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_devtools_post_is_forwarded(self, mock_get_session):
        session = _mock_session(mock_get_session, _binary_upstream(b"{}", "application/json"))
        response = self.client.post("/__nuxt_devtools__/rpc", data={"a": "b"})
        response.status_code | should.be.equal.to(200)
        session.request.call_args.kwargs["method"] | should.be.equal.to("POST")

    @patch("django_nuxt.proxy.get_proxy_session")
    def test_devtools_rewrites_origin_to_nuxt(self, mock_get_session):
        session = _mock_session(mock_get_session, _binary_upstream(b"{}", "application/json"))
        self.client.get(
            "/__nuxt_devtools__/rpc",
            HTTP_ORIGIN="http://localhost:8000",
        )
        headers = session.request.call_args.kwargs["headers"]
        headers["Origin"] | should.be.equal.to("http://nuxt.test:3000")


class TestNuxtDevServerUrl(TestCase):
    @override_settings(DEBUG=True, DJANGO_NUXT_SERVER_RUNNING=None)
    def test_defaults_to_localhost_in_debug(self):
        get_nuxt_dev_server_url() | should.be.equal.to("http://localhost:3000")

    @override_settings(DEBUG=False, DJANGO_NUXT_SERVER_RUNNING=None)
    def test_disabled_when_not_debug_and_unset(self):
        get_nuxt_dev_server_url() | should.be.equal.to(None)

    @override_settings(DEBUG=False, DJANGO_NUXT_SERVER_RUNNING=True)
    def test_true_uses_default_url(self):
        get_nuxt_dev_server_url() | should.be.equal.to("http://localhost:3000")

    @override_settings(DEBUG=True, DJANGO_NUXT_SERVER_RUNNING=False)
    def test_false_disables_proxy(self):
        get_nuxt_dev_server_url() | should.be.equal.to(None)

    @override_settings(DJANGO_NUXT_SERVER_RUNNING="http://127.0.0.1:3010")
    def test_custom_url(self):
        get_nuxt_dev_server_url() | should.be.equal.to("http://127.0.0.1:3010")


class TestNuxtUrlHelpers(TestCase):
    @override_settings(DJANGO_NUXT_SERVER_RUNNING="http://localhost:3000")
    def test_static_urls_are_catch_all_proxy_in_dev(self):
        urls = NuxtStaticUrls()
        len(urls) | should.be.equal.to(1)
        urls[0].name | should.be.equal.to("nuxt_proxy")

    @override_settings(DJANGO_NUXT_SERVER_RUNNING="http://localhost:3000")
    def test_catch_all_urls_are_proxy_in_dev(self):
        urls = NuxtCatchAllUrls()
        len(urls) | should.be.equal.to(1)
        urls[0].name | should.be.equal.to("nuxt_catch_all")

    @override_settings(DEBUG=False, DJANGO_NUXT_SERVER_RUNNING=False)
    def test_catch_all_uses_template_view_without_dev_server(self):
        urls = NuxtCatchAllUrls()
        urls[-1].name | should.be.equal.to("nuxt_catch_all")
        urls[-1].callback.__name__ | should.be.equal.to("nuxt_proxy")


class TestAssetProxyMiddlewareInstall(TestCase):
    def test_install_prepends_once(self):
        with self.settings(MIDDLEWARE=["django.middleware.csrf.CsrfViewMiddleware"]):
            install_asset_proxy_middleware()
            from django.conf import settings
            settings.MIDDLEWARE[0] | should.be.equal.to(ASSET_MIDDLEWARE)
            install_asset_proxy_middleware()
            settings.MIDDLEWARE.count(ASSET_MIDDLEWARE) | should.be.equal.to(1)


class TestWebSocketTunnel(TestCase):
    def test_handshake_keeps_path_and_adds_forwarded_host(self):
        handler = MagicMock()
        handler.command = "GET"
        handler.path = "/__nuxt_devtools__/rpc"
        handler.request_version = "HTTP/1.1"
        handler.headers = {
            "Host": "localhost:8000",
            "Upgrade": "websocket",
            "Connection": "Upgrade",
        }
        raw = _build_upstream_handshake(handler)
        self.assertIn(b"GET /__nuxt_devtools__/rpc HTTP/1.1", raw)
        self.assertIn(b"Host: localhost:8000", raw)
        self.assertIn(b"X-Forwarded-Host: localhost:8000", raw)

    def test_devtools_handshake_rewrites_origin_to_nuxt(self):
        handler = MagicMock()
        handler.command = "GET"
        handler.path = "/__nuxt_devtools__/rpc"
        handler.request_version = "HTTP/1.1"
        handler.headers = {
            "Host": "localhost:8000",
            "Origin": "http://localhost:8000",
            "Upgrade": "websocket",
            "Connection": "Upgrade",
        }
        raw = _build_upstream_handshake(handler, "http://localhost:3000")
        self.assertIn(b"Host: localhost:3000", raw)
        self.assertIn(b"Origin: http://localhost:3000", raw)
        self.assertIn(b"X-Forwarded-Host: localhost:8000", raw)

    @patch("django_nuxt.proxy.select.select")
    @patch("django_nuxt.proxy.socket.create_connection")
    def test_tunnel_copies_client_bytes_to_nuxt(self, mock_create, mock_select):
        upstream = MagicMock()
        client = MagicMock()
        mock_create.return_value = upstream
        handler = MagicMock()
        handler.command = "GET"
        handler.path = "/_nuxt/"
        handler.request_version = "HTTP/1.1"
        handler.headers = {"Host": "localhost:8000", "Upgrade": "websocket"}
        handler.connection = client
        mock_select.side_effect = [([client], [], []), ([client], [], [])]
        client.recv.side_effect = [b"hello", b""]

        tunnel_websocket(handler, "http://localhost:3000")

        mock_create.assert_called_once_with(("localhost", 3000), timeout=30)
        upstream.sendall.call_count | should.be.equal.to(2)
        upstream.sendall.call_args_list[1].args[0] | should.be.equal.to(b"hello")
        upstream.close.assert_called()

    def test_patch_is_idempotent(self):
        patch_wsgi_websocket_proxy()
        patch_wsgi_websocket_proxy()
        from django.core.servers.basehttp import WSGIRequestHandler
        from django_nuxt.proxy import _handle_one_request_with_ws

        WSGIRequestHandler.handle_one_request | should.be.equal.to(_handle_one_request_with_ws)
