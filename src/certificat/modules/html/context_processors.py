from .nav import Navigation
import inject


def nav(request):
    return {"nav": Navigation(request)}


def settings(request):
    from certificat.settings.dynamic import ApplicationSettings

    return {"settings": inject.instance(ApplicationSettings)}


def version(request):
    from importlib.metadata import version

    try:
        certificat_version = version("certificat")
    except Exception:
        certificat_version = "0.0.1-dev1"

    return {"certificat_version": certificat_version}
