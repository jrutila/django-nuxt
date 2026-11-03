import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from django_nuxt.staticfiles import NuxtStaticFilesFinder


def _collected(finder):
    names = []
    for path, storage in finder.list(None):
        prefix = getattr(storage, "prefix", "") or ""
        relative = f"{prefix}/{path}" if prefix else path
        names.append(relative.replace("\\", "/"))
    return sorted(names)


class TestNuxtStaticFilesFinder(TestCase):
    def test_collects_every_generated_directory_and_skips_root_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "public"
            nuxt_public = root / "ui-public"
            (generated / "_nuxt").mkdir(parents=True)
            (generated / "_nuxt" / "app.js").write_text("js", encoding="utf-8")
            (generated / "_fonts").mkdir()
            (generated / "_fonts" / "Inter.woff2").write_bytes(b"woff")
            (generated / "images").mkdir()
            (generated / "images" / "logo.png").write_bytes(b"png")
            (generated / "200.html").write_text("<html></html>", encoding="utf-8")
            nuxt_public.mkdir()
            (nuxt_public / "robots.txt").write_text("robots", encoding="utf-8")

            with override_settings(
                DJANGO_NUXT_GENERATED_FOLDER=str(generated),
                DJANGO_NUXT_PUBLIC_FOLDER=str(nuxt_public),
            ):
                names = _collected(NuxtStaticFilesFinder())

        self.assertEqual(
            names,
            [
                "_fonts/Inter.woff2",
                "_nuxt/app.js",
                "images/logo.png",
                "robots.txt",
            ],
        )

    def test_missing_generated_folder_still_collects_public_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            nuxt_public = Path(tmp) / "ui-public"
            nuxt_public.mkdir()
            (nuxt_public / "robots.txt").write_text("robots", encoding="utf-8")
            missing = Path(tmp) / "missing-output"

            with override_settings(
                DJANGO_NUXT_GENERATED_FOLDER=str(missing),
                DJANGO_NUXT_PUBLIC_FOLDER=str(nuxt_public),
            ):
                names = _collected(NuxtStaticFilesFinder())

        self.assertEqual(names, ["robots.txt"])

    def test_static_directory_is_collected_without_that_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "public"
            nuxt_public = root / "ui-public"
            (generated / "static" / "_fonts").mkdir(parents=True)
            (generated / "static" / "_fonts" / "Inter.woff2").write_bytes(b"woff")
            (generated / "static" / "_nuxt").mkdir()
            (generated / "static" / "_nuxt" / "app.js").write_text("js", encoding="utf-8")
            (generated / "static" / "favicon.ico").write_bytes(b"ico")
            nuxt_public.mkdir()

            with override_settings(
                STATIC_URL="static/",
                DJANGO_NUXT_GENERATED_FOLDER=str(generated),
                DJANGO_NUXT_PUBLIC_FOLDER=str(nuxt_public),
            ):
                names = _collected(NuxtStaticFilesFinder())

        self.assertEqual(
            names,
            [
                "_fonts/Inter.woff2",
                "_nuxt/app.js",
                "favicon.ico",
            ],
        )

    def test_cdn_static_url_uses_the_first_path_segment(self):
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "public"
            nuxt_public = Path(tmp) / "ui-public"
            (generated / "static" / "_fonts").mkdir(parents=True)
            (generated / "static" / "_fonts" / "Inter.woff2").write_bytes(b"woff")
            nuxt_public.mkdir()

            with override_settings(
                STATIC_URL="https://cdn.example.com/static/",
                DJANGO_NUXT_GENERATED_FOLDER=str(generated),
                DJANGO_NUXT_PUBLIC_FOLDER=str(nuxt_public),
            ):
                names = _collected(NuxtStaticFilesFinder())

        self.assertEqual(names, ["_fonts/Inter.woff2"])
