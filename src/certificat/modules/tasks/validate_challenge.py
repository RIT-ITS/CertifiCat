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
from certificat.modules.acme import models as db
from django.db.models import Subquery

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

        chall = chall_service.get(challenge_name)
        if chall.status != ChallengeStatus.processing:
            logger.info(
                f"{log_prefix}: cannot validate challenge if status != processing"
            )
            return

        logger.info(
            f"{log_prefix}: beginning validation, retries available: {task.retries} "
        )

        passed = False

        try:
            authz = auth_service.get(chall.authz_id)
            order = order_service.get(authz.order_id)
            acct = account_service.get(order.account_id)

            chall = chall_service.validate(acct.jwk, order, authz, chall)
            passed = chall.status == ChallengeStatus.valid
            if not passed:
                db.ChallengeError.objects.create(
                    challenge_id=Subquery(
                        db.Challenge.objects.filter(name=chall.id).values("id")[:1]
                    ),
                    error="Challenge not validated",
                )
        except Exception as exc:
            logger.info(f"{log_prefix}: exception evaluating challenge - {exc}")
            db.ChallengeError.objects.create(
                challenge_id=Subquery(
                    db.Challenge.objects.filter(name=chall.id).values("id")[:1]
                ),
                error=str(exc),
            )

        if passed:
            return True

        if task.retries == 0 or HUEY.immediate:
            # If it did not pass, set the challenge to invalid. The consumer will have
            # to handle resubmission.
            logger.info(
                f"{log_prefix}: retries exceeded, marking challenge and auth invalid"
            )
            chall = chall_service.invalidate(order, authz, chall)
        else:
            task.retries -= 1
            raise RetryTask("Challenges unsuccessful")
