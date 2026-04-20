from importlib.metadata import version

try:
    __version__ = version("certificat")
except Exception:
    # This should only happen in development
    __version__ = "Unknown"
