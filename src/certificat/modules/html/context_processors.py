from .nav import Navigation


def nav(request):
    return {"nav": Navigation(request)}
