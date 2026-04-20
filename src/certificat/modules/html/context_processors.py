from .nav import Navigation
import inject


def nav(request):
    return {"nav": Navigation(request)}


def settings(request):
    from certificat.settings.dynamic import ApplicationSettings

    return {"settings": inject.instance(ApplicationSettings)}


def version(request):
    from certificat import __version__

    return {"certificat_version": __version__}
