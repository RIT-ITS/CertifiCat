import acme.client
from certificat.settings.dynamic import ApplicationSettings
import inject
import pytest
from ..helpers import do_challenge, finalize_order
from ..conftest import NewOrderRet
from certificat.modules.acme import models as db
from acme import errors
from acmev2.models import OrderStatus
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
def test_finalize_local(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.type = "local"

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    finalized_order = finalize_order(acme_client, order)

    assert finalized_order.body.status.name == "valid"
    assert len(finalized_order.fullchain_pem) > 0


@pytest.mark.django_db
def test_finalize_preauthorized(acme_client, acme_newacct, acme_neworder):
    acme_acct = acme_newacct()
    account = db.Account.objects.get(name=acme_acct.response.uri.split("/")[-1])
    preauth_domain = "preauth.acme.edu"

    db.PreAuthorizedAccountIdentifier.objects.create(
        account=account,
        identifier_type=db.IdentifierType.dns,
        identifier_value=preauth_domain,
    )

    new_order: NewOrderRet = acme_neworder(
        new_acct=acme_acct, cn=preauth_domain, sans=[preauth_domain]
    )
    order = do_challenge(acme_client, new_order.response)
    finalized_order = finalize_order(acme_client, order)

    assert finalized_order.body.status.name == "valid"
    assert len(finalized_order.fullchain_pem) > 0
    assert "auth.Preauth" in db.TaggedEvent.objects.values_list(
        "event_type", flat=True
    ).filter(content_type=ContentType.objects.get_for_model(db.Authorization))


@pytest.mark.django_db
def test_finalize_preauthorized_and_http01(acme_client, acme_newacct, acme_neworder):
    acme_acct = acme_newacct()
    account = db.Account.objects.get(name=acme_acct.response.uri.split("/")[-1])
    preauth_domain = "preauth.acme.edu"

    db.PreAuthorizedAccountIdentifier.objects.create(
        account=account,
        identifier_type=db.IdentifierType.dns,
        identifier_value=preauth_domain,
    )

    new_order: NewOrderRet = acme_neworder(
        new_acct=acme_acct, cn=preauth_domain, sans=[preauth_domain, "acme.localhost"]
    )
    order = do_challenge(acme_client, new_order.response)
    finalized_order = finalize_order(acme_client, order)

    assert finalized_order.body.status.name == "valid"
    assert len(finalized_order.fullchain_pem) > 0
    assert "auth.Preauth" in db.TaggedEvent.objects.values_list(
        "event_type", flat=True
    ).filter(content_type=ContentType.objects.get_for_model(db.Authorization))
    assert len(finalized_order.body.identifiers) == 2


@pytest.mark.django_db
def test_finalize_fail_dispatch_task(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)
    order_name = order.uri.split("/")[-1]
    mocker.patch(
        "certificat.modules.tasks.finalize_order.finalize_order_task",
        side_effect=Exception(),
    )
    with pytest.raises(Exception):
        finalize_order(acme_client, order)

    db_order = db.Order.objects.get(name=order_name)
    assert db_order.status == OrderStatus.ready


@pytest.mark.django_db
def test_finalize_mock_sectigo_fail_enroll(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.FailingEnrollMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, order, timeout=0)

    order_name = order.uri.split("/")[-1]
    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    assert processing_state.state == db.SectigoOrderProcessingState.Choices.SUBMITTED
    assert db.OrderFinalizationError.objects.count() == 1


@pytest.mark.django_db
def test_finalize_mock_sectigo_fail_get(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.FailingGetMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, order, timeout=0)

    order_name = order.uri.split("/")[-1]
    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    assert processing_state.state == db.SectigoOrderProcessingState.Choices.ENROLLED
    assert db.OrderFinalizationError.objects.count() == 1


@pytest.mark.django_db
def test_finalize_mock_sectigo_fail_approve(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.FailingGetMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, order, timeout=0)

    order_name = order.uri.split("/")[-1]
    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    assert processing_state.state == db.SectigoOrderProcessingState.Choices.ENROLLED
    assert db.OrderFinalizationError.objects.count() == 1


@pytest.mark.django_db
def test_finalize_mock_sectigo_fail_collect(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.FailingCollectMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, order, timeout=0)

    order_name = order.uri.split("/")[-1]
    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    assert processing_state.state == db.SectigoOrderProcessingState.Choices.APPROVED
    assert db.OrderFinalizationError.objects.count() == 1


@pytest.mark.django_db
def test_finalize_mock_sectigo_slow_collect(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.SlowCollectMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, order, timeout=0)

    order_name = order.uri.split("/")[-1]
    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    # State should still be approved, the order was not successfully collected
    assert processing_state.state == db.SectigoOrderProcessingState.Choices.APPROVED
    # The error should not be recorded
    assert db.OrderFinalizationError.objects.count() == 0


@pytest.mark.django_db
def test_flaky_sectigo_api(
    acme_client: acme.client.ClientV2,
    acme_neworder,
    mocker,
):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer.module = (
        "certificat.tests.test_acme.finalizer_mocks.FailingEnrollMockSectigoFinalizer"
    )

    new_order: NewOrderRet = acme_neworder()

    orderr = do_challenge(acme_client, new_order.response)

    from certificat.modules.tasks.finalize_order import finalize_order_task

    with pytest.raises(errors.TimeoutError):
        # This always errors, so make it happen fast
        finalize_order(acme_client, orderr, timeout=0)

    order_name = orderr.uri.split("/")[-1]
    order = db.Order.objects.get(name=order_name)

    def resume_finalization(finalizer: str):
        settings.finalizer.module = finalizer
        order.status = OrderStatus.processing
        order.save()

        finalize_order_task(order.name)

    assert db.OrderFinalizationError.objects.count() == 1
    processing_state = db.SectigoOrderProcessingState.for_order(order)
    assert processing_state.state == db.SectigoOrderProcessingState.Choices.SUBMITTED

    # Now have it fail at every step and ensure we can safely resume finalization.
    # This simulates retrying the background task over and over again.
    resume_finalization(
        "certificat.tests.test_acme.finalizer_mocks.FailingApproveMockSectigoFinalizer"
    )
    resume_finalization(
        "certificat.tests.test_acme.finalizer_mocks.FailingGetMockSectigoFinalizer"
    )
    resume_finalization(
        "certificat.tests.test_acme.finalizer_mocks.FailingCollectMockSectigoFinalizer"
    )
    resume_finalization(
        "certificat.tests.test_acme.finalizer_mocks.MockSectigoFinalizer"
    )

    err = set([e.error for e in db.OrderFinalizationError.objects.all()])
    # Assert we have four unique errors, signifying the re-entrant task failed
    # in four different ways.
    assert len(err) == 4

    processing_state = db.SectigoOrderProcessingState.for_order(
        db.Order.objects.get(name=order_name)
    )

    # Even though it failed the cert was still collected after retries
    assert processing_state.state == db.SectigoOrderProcessingState.Choices.COLLECTED
    assert order.certificate is not None
