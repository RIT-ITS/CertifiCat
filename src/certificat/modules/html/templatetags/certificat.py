from django import template
from django.core.paginator import Paginator
from textwrap import wrap
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat._oid import _OID_NAMES as OID_NAMES
from certificat.constants import EXTENSION_NAMES
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
import re
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.simple_tag
def get_elided_page_range(p, number, on_each_side=3, on_ends=2):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(
        number=number, on_each_side=on_each_side, on_ends=on_ends
    )


@register.filter(name="wrap")
def wrap_tag(value, width):
    return wrap(value, width)


@register.filter
def percentage(value):
    return f"{value:.0%}"


@register.filter("hex")
def as_hex(value: str | bytes):
    if isinstance(value, bytes):
        hex_val = value.hex()
    else:
        hex_val = hex(value)[2:]

    return ":".join(wrap(hex_val, 2))


@register.filter
def to_datetime(value: str):
    return parse_datetime(value)


@register.filter
def to_x509(value: str):
    return x509.load_pem_x509_certificates(value.encode())


@register.filter
def x509_version(version: x509.Version):
    return version.name


@register.filter
def render_x509_extension(extension: x509.Extension):
    try:
        template = get_template(
            f"certificat/x509.extensions/{extension.oid.dotted_string}.html"
        )
    except TemplateDoesNotExist:
        template = get_template("certificat/x509.extensions/notfound.html")

    return template.render({"extension": extension})


@register.filter
def x509_oid_to_name(oid: x509.ObjectIdentifier):
    if oid in EXTENSION_NAMES:
        return EXTENSION_NAMES[oid]

    return OID_NAMES.get(oid, f"Unknown extension ({oid.dotted_string})")


@register.filter
def x509_ext_vals(extension: x509.Extension):
    try:
        for val in extension.value:
            for v in val:
                yield v
    except TypeError:
        yield extension.value


@register.filter
def x509_key(cert: x509.Certificate):
    return cert.public_bytes(serialization.Encoding.PEM).decode()


@register.filter
def break_at_armor(value: str):
    return [line for line in re.split("(-----.+-----)", value) if len(line.strip()) > 0]
