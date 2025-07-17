__all__ = ["HUEY"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

HUEY = {
    "huey_class": "huey.PriorityRedisHuey",  # Huey implementation to use.
    "name": "huey",  # Use db name for huey.
    "immediate": False,
    "utc": False,
    "blocking": True,  # Perform blocking pop rather than poll Redis.
    "connection": {
        "host": dynamic_settings.redis.host,
        "password": dynamic_settings.redis.password,
        "port": dynamic_settings.redis.port,
        "health_check_interval": 10,
        "read_timeout": 1,
    },
    "consumer": {
        "workers": dynamic_settings.task_queue.workers,
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 3.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,
    },
}
