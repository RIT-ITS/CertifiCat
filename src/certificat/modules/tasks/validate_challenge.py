import logging

from huey.contrib.djhuey import HUEY
from huey.api import RetryTask
from acmev2.models import ChallengeStatus
import inject
from acmev2.services.services import (
    IAccountService,
    IOrderService,
    IAuthorizationService,
    IChallengeService,
)

logger = logging.getLogger(__name__)


def validate_challenge_task(challenge_name: str, task=None):
    """Validates an HTTP challenge for a pending authorization. It will
    retry the challenge a number of times and set the authorization as
    invalid if it does not pass.

    If the task fails with an exception outside of normal it will be retried
    as well.

    Args:
        challenge_name (str): The string name of the challenge
    """
    lock_key = f"chall-{challenge_name}"
    log_prefix = "challenge " + challenge_name

    if HUEY.is_locked(lock_key):
        logger.info(f"{log_prefix}: exiting task, lock not acquired for {lock_key}")
        return

    with HUEY.lock_task(lock_key):
        chall_service = inject.instance(IChallengeService)
        auth_service = inject.instance(IAuthorizationService)
        order_service = inject.instance(IOrderService)
        account_service = inject.instance(IAccountService)

        challenge = chall_service.get(challenge_name)
        if challenge.status != ChallengeStatus.processing:
            logger.info(
                f"{log_prefix}: cannot validate challenge if status != processing"
            )

        logger.info(
            f"{log_prefix}: beginning validation, retries available: {task.retries} "
        )

        passed = False
        event_payload = {}

        try:
            authz = auth_service.get(challenge.authz_id)
            order = order_service.get(authz.order_id)
            acct = account_service.get(order.account_id)

            chall = chall_service.validate(acct.jwk, order, authz, challenge)
            passed = chall.status == ChallengeStatus.valid
        except Exception as exc:
            logger.info(f"{log_prefix}: exception evaluating challenge - {exc}")
            event_payload["exception"] = str(exc)

        if passed:
            return True
        else:
            pass
            # ChallengeEvent.record(
            #    ChallengeEventType.FAILED_VERIFICATION,
            #    challenge,
            #    payload=event_payload,
            # )

        if task.retries == 0 or HUEY.immediate:
            # If it did not pass, set the challenge to invalid. The consumer will have
            # to handle resubmission.
            logger.info(
                f"{log_prefix}: retries exceeded, marking challenge and auth invalid"
            )
            chall = chall_service.invalidate(order, authz, chall)
            # ChallengeEvent.record(ChallengeEventType.RETRIES_EXCEEDED, challenge)
            # challenge.status = Status.objects.get(name="invalid")
            # challenge.save()

            # challenge.authorization.status = challenge.status
            # challenge.authorization.save()
        else:
            task.retries -= 1
            raise RetryTask("Challenges unsuccessful")
