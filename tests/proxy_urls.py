from django.urls import re_path
from django_nuxt.proxy import NuxtDevProxyView

urlpatterns = [
    re_path(r"^(?!\.).*$", NuxtDevProxyView.as_view(), name="nuxt_catch_all"),
]
