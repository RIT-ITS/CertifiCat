from django.core.management.base import BaseCommand, CommandError
from certificat.modules.tasks import ping


class Command(BaseCommand):
    help = "Pings huey to check that a consumer is running"

    def handle(self, *args, **options):
        expected_pong_reply = "pong"
        pong_reply = ping(expected_pong_reply)
        self.stdout.write("queueing ping")

        if expected_pong_reply != pong_reply(blocking=True):
            raise CommandError("huey pong failure")
        else:
            self.stdout.write(self.style.SUCCESS("huey pong success"))
