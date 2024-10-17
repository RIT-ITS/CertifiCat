from .dynamic import app_settings

__all__ = ["HUEY"]

HUEY = {
    "huey_class": "huey.RedisHuey",  # Huey implementation to use.
    "name": "huey",  # Use db name for huey.
    "immediate": False,
    "connection": {
        "host": app_settings.redis.host,
        "password": app_settings.redis.password,
        "port": app_settings.redis.port,
    },
    "consumer": {
        "workers": 1,
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
}
