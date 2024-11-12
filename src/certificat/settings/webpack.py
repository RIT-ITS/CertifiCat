import os

__all__ = ["WEBPACK_LOADER"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": True,
        "BUNDLE_DIR_NAME": "certificat.bundle/",  # must end with slash
        "STATS_FILE": os.path.join(
            BASE_DIR, "certificat/modules/html/static/webpack-stats.json"
        ),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}
