from os.path import dirname, join
from django import template
from django.conf import settings
from django.utils.html import format_html
from django.templatetags.static import static
import json
from django.utils.safestring import mark_safe
from functools import lru_cache

register = template.Library()
STATIC_FOLDER = join(dirname(__file__), "../static/certificat.vite/")
MANIFEST_FILE = join(STATIC_FOLDER, "manifest.json")


@register.simple_tag
def vite_dev_style(resource: str):
    # Using dev styles avoids the initial flash of unstyled content that you get
    # from loading styles through javascript
    if settings.DEBUG:
        return format_html(
            '<link rel="stylesheet" href="//{}:{}/{}" type="text/css">',
            settings.VITE_HOST,
            settings.VITE_PORT,
            resource,
        )

    return ""


@register.simple_tag
def vite_hmr_client():
    if settings.DEBUG:
        return format_html(
            '<script type="module" src="//{}:{}/@vite/client"></script>',
            settings.VITE_HOST,
            settings.VITE_PORT,
        )

    return ""


@register.simple_tag
@lru_cache()
def vite_resource(resource: str):
    if settings.DEBUG:
        return format_html(
            '<script type="module" src="//{}:{}/{}"></script>',
            settings.VITE_HOST,
            settings.VITE_PORT,
            resource,
        )
    else:
        manifest = json.load(open(MANIFEST_FILE, "r"))
        entry = manifest[resource]

        assets = []
        assets.append(
            format_html(
                '<script type="module" src="{}"></script>',
                static("certificat.vite/" + entry["file"]),
            )
        )

        for vendor_import in entry.get("imports", []):
            vendor_entry = manifest[vendor_import]
            assets.append(
                format_html(
                    '<script type="module" src="{}"></script>',
                    static("certificat.vite/" + vendor_entry["file"]),
                )
            )

        for css_resource in entry.get("css", []):
            assets.append(
                format_html(
                    '<link rel="stylesheet" href="{}">',
                    static("certificat.vite/" + css_resource),
                )
            )

        return mark_safe("".join(assets))
