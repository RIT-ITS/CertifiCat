import json
from typing import Callable

from certificat.settings.dynamic import (
    ApplicationSettings,
    CertiNextFinalizerSettings,
)
import pytest
import acme
from ..helpers import do_challenge, finalize_order
from ..conftest import NewOrderRet
from acme import errors
from certificat.modules.acme import models as db
import pytest_responses  # noqa: F401
import responses


DUMMY_ROOT_CERT = """
MIIFYjCCBEqgAwIBAgIQd70NbNs2+RrqIQ/E8FjTDTANBgkqhkiG9w0BAQsFADBX
MQswCQYDVQQGEwJCRTEZMBcGA1UEChMQR2xvYmFsU2lnbiBudi1zYTEQMA4GA1UE
CxMHUm9vdCBDQTEbMBkGA1UEAxMSR2xvYmFsU2lnbiBSb290IENBMB4XDTIwMDYx
OTAwMDA0MloXDTI4MDEyODAwMDA0MlowRzELMAkGA1UEBhMCVVMxIjAgBgNVBAoT
GUdvb2dsZSBUcnVzdCBTZXJ2aWNlcyBMTEMxFDASBgNVBAMTC0dUUyBSb290IFIx
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAthECix7joXebO9y/lD63
ladAPKH9gvl9MgaCcfb2jH/76Nu8ai6Xl6OMS/kr9rH5zoQdsfnFl97vufKj6bwS
iV6nqlKr+CMny6SxnGPb15l+8Ape62im9MZaRw1NEDPjTrETo8gYbEvs/AmQ351k
KSUjB6G00j0uYODP0gmHu81I8E3CwnqIiru6z1kZ1q+PsAewnjHxgsHA3y6mbWwZ
DrXYfiYaRQM9sHmklCitD38m5agI/pboPGiUU+6DOogrFZYJsuB6jC511pzrp1Zk
j5ZPaK49l8KEj8C8QMALXL32h7M1bKwYUH+E4EzNktMg6TO8UpmvMrUpsyUqtEj5
cuHKZPfmghCN6J3Cioj6OGaK/GP5Afl4/Xtcd/p2h/rs37EOeZVXtL0m79YB0esW
CruOC7XFxYpVq9Os6pFLKcwZpDIlTirxZUTQAs6qzkm06p98g7BAe+dDq6dso499
iYH6TKX/1Y7DzkvgtdizjkXPdsDtQCv9Uw+wp9U7DbGKogPeMa3Md+pvez7W35Ei
Eua++tgy/BBjFFFy3l3WFpO9KWgz7zpm7AeKJt8T11dleCfeXkkUAKIAf5qoIbap
sZWwpbkNFhHax2xIPEDgfg1azVY80ZcFuctL7TlLnMQ/0lUTbiSw1nH69MG6zO0b
9f6BQdgAmD06yK56mDcYBZUCAwEAAaOCATgwggE0MA4GA1UdDwEB/wQEAwIBhjAP
BgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTkrysmcRorSCeFL1JmLO/wiRNxPjAf
BgNVHSMEGDAWgBRge2YaRQ2XyolQL30EzTSo//z9SzBgBggrBgEFBQcBAQRUMFIw
JQYIKwYBBQUHMAGGGWh0dHA6Ly9vY3NwLnBraS5nb29nL2dzcjEwKQYIKwYBBQUH
MAKGHWh0dHA6Ly9wa2kuZ29vZy9nc3IxL2dzcjEuY3J0MDIGA1UdHwQrMCkwJ6Al
oCOGIWh0dHA6Ly9jcmwucGtpLmdvb2cvZ3NyMS9nc3IxLmNybDA7BgNVHSAENDAy
MAgGBmeBDAECATAIBgZngQwBAgIwDQYLKwYBBAHWeQIFAwIwDQYLKwYBBAHWeQIF
AwMwDQYJKoZIhvcNAQELBQADggEBADSkHrEoo9C0dhemMXoh6dFSPsjbdBZBiLg9
NR3t5P+T4Vxfq7vqfM/b5A3Ri1fyJm9bvhdGaJQ3b2t6yMAYN/olUazsaL+yyEn9
WprKASOshIArAoyZl+tJaox118fessmXn1hIVw41oeQa1v1vg4Fv74zPl6/AhSrw
9U5pCZEt4Wi4wStz6dTZ/CLANx8LZh1J7QJVj2fhMtfTJr9w4z30Z209fOU0iOMy
+qduBmpvvYuR7hZL6Dupszfnw0Skfths18dG9ZKb59UhvmaSGZRVbNQpsg3BZlvi
d0lIKO2d1xozclOzgjXPYovJJIultzkMu34qQb9Sz/yilrbCgj8=
"""
DUMMY_CA_CERT = """
MIIFCzCCAvOgAwIBAgIQf/AFoHxM3tEArZ1mpRB7mDANBgkqhkiG9w0BAQsFADBH
MQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExM
QzEUMBIGA1UEAxMLR1RTIFJvb3QgUjEwHhcNMjMxMjEzMDkwMDAwWhcNMjkwMjIw
MTQwMDAwWjA7MQswCQYDVQQGEwJVUzEeMBwGA1UEChMVR29vZ2xlIFRydXN0IFNl
cnZpY2VzMQwwCgYDVQQDEwNXUjIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQCp/5x/RR5wqFOfytnlDd5GV1d9vI+aWqxG8YSau5HbyfsvAfuSCQAWXqAc
+MGr+XgvSszYhaLYWTwO0xj7sfUkDSbutltkdnwUxy96zqhMt/TZCPzfhyM1IKji
aeKMTj+xWfpgoh6zySBTGYLKNlNtYE3pAJH8do1cCA8Kwtzxc2vFE24KT3rC8gIc
LrRjg9ox9i11MLL7q8Ju26nADrn5Z9TDJVd06wW06Y613ijNzHoU5HEDy01hLmFX
xRmpC5iEGuh5KdmyjS//V2pm4M6rlagplmNwEmceOuHbsCFx13ye/aoXbv4r+zgX
FNFmp6+atXDMyGOBOozAKql2N87jAgMBAAGjgf4wgfswDgYDVR0PAQH/BAQDAgGG
MB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjASBgNVHRMBAf8ECDAGAQH/
AgEAMB0GA1UdDgQWBBTeGx7teRXUPjckwyG77DQ5bUKyMDAfBgNVHSMEGDAWgBTk
rysmcRorSCeFL1JmLO/wiRNxPjA0BggrBgEFBQcBAQQoMCYwJAYIKwYBBQUHMAKG
GGh0dHA6Ly9pLnBraS5nb29nL3IxLmNydDArBgNVHR8EJDAiMCCgHqAchhpodHRw
Oi8vYy5wa2kuZ29vZy9yL3IxLmNybDATBgNVHSAEDDAKMAgGBmeBDAECATANBgkq
hkiG9w0BAQsFAAOCAgEARXWL5R87RBOWGqtY8TXJbz3S0DNKhjO6V1FP7sQ02hYS
TL8Tnw3UVOlIecAwPJQl8hr0ujKUtjNyC4XuCRElNJThb0Lbgpt7fyqaqf9/qdLe
SiDLs/sDA7j4BwXaWZIvGEaYzq9yviQmsR4ATb0IrZNBRAq7x9UBhb+TV+PfdBJT
DhEl05vc3ssnbrPCuTNiOcLgNeFbpwkuGcuRKnZc8d/KI4RApW//mkHgte8y0YWu
ryUJ8GLFbsLIbjL9uNrizkqRSvOFVU6xddZIMy9vhNkSXJ/UcZhjJY1pXAprffJB
vei7j+Qi151lRehMCofa6WBmiA4fx+FOVsV2/7R6V2nyAiIJJkEd2nSi5SnzxJrl
Xdaqev3htytmOPvoKWa676ATL/hzfvDaQBEcXd2Ppvy+275W+DKcH0FBbX62xevG
iza3F4ydzxl6NJ8hk8R+dDXSqv1MbRT1ybB5W0k8878XSOjvmiYTDIfyc9acxVJr
Y/cykHipa+te1pOhv7wYPYtZ9orGBV5SGOJm4NrB3K1aJar0RfzxC3ikr7Dyc6Qw
qDTBU39CluVIQeuQRgwG3MuSxl7zRERDRilGoKb8uY45JzmxWuKxrfwT/478JuHU
/oTxUFqOl2stKnn7QGTq8z29W+GgBLCXSBxC9epaHM0myFH/FJlniXJfHeytWt0=
"""
DUMMY_END_ENTITY_CERT = """
MIIEWTCCA0GgAwIBAgIRAKrzz49yS/O3CbHIza9eLYswDQYJKoZIhvcNAQELBQAw
OzELMAkGA1UEBhMCVVMxHjAcBgNVBAoTFUdvb2dsZSBUcnVzdCBTZXJ2aWNlczEM
MAoGA1UEAxMDV1IyMB4XDTI2MDExOTA4MzkwNVoXDTI2MDQxMzA4MzkwNFowGTEX
MBUGA1UEAxMOd3d3Lmdvb2dsZS5jb20wWTATBgcqhkjOPQIBBggqhkjOPQMBBwNC
AATwW7hLQitcVC9Cc1aihgsmZWONEdEKskRDi0Yp0z3JveXh09IS7IzNStSQJUzp
Wa1ODcYExK1VgzoEaKMshx+Bo4ICQzCCAj8wDgYDVR0PAQH/BAQDAgeAMBMGA1Ud
JQQMMAoGCCsGAQUFBwMBMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYEFDp9MFYjfL3M
lYSdTuSAXVh63wxcMB8GA1UdIwQYMBaAFN4bHu15FdQ+NyTDIbvsNDltQrIwMFgG
CCsGAQUFBwEBBEwwSjAhBggrBgEFBQcwAYYVaHR0cDovL28ucGtpLmdvb2cvd3Iy
MCUGCCsGAQUFBzAChhlodHRwOi8vaS5wa2kuZ29vZy93cjIuY3J0MBkGA1UdEQQS
MBCCDnd3dy5nb29nbGUuY29tMBMGA1UdIAQMMAowCAYGZ4EMAQIBMDYGA1UdHwQv
MC0wK6ApoCeGJWh0dHA6Ly9jLnBraS5nb29nL3dyMi9HU3lUMU40UEJyZy5jcmww
ggEGBgorBgEEAdZ5AgQCBIH3BIH0APIAdwAOV5S8866pPjMbLJkHs/eQ35vCPXEy
Jd0hqSWsYcVOIQAAAZvVn1FPAAAEAwBIMEYCIQDejx5x1DA6e8uO/B06M91stniI
sAiApU/xBGyAtrdlcwIhAIT7jV5CpBIeS3nDwWRO4zwLOdVpFXS0ejXEcbhnHXPa
AHcAFoMtq/CpJQ8P8DqlRf/Iv8gj0IdL9gQpJ/jnHzMT9foAAAGb1Z9RaQAABAMA
SDBGAiEAj5usEOdnz2dpx2YTT0w28YAgGmkHy2N13lyrA3ds8K4CIQCjBJG/aH46
Cd3otRIIld+ONRwSYAPH9xpSd3IQtfVQ3DANBgkqhkiG9w0BAQsFAAOCAQEAhNlH
2CJVUNoDOIWlMDz46Phi7SoE6h8i6z5ZPl1udlKJqiaw2YpCdtnBb5SuEdDIkgLR
vfGjY6AX89DgpXV1ahL8zY2ZRPIuWDdcf0WH9cH+HADi6aymAcKhdB+Bv39tHVyI
ADZfXj1sC60EO9Ry9xA3/GqGuefHANOl1fc3qXTjWpBpxuJ6kVT0WC7PVnUOWE9I
29EkOonv+Qu5E36mPDuxEvfI9uePI0x6Bw62UPB9524CtP7Xba3Z7Jol5yh4RneF
9fP2+Xpes2WaUSfgU6Cp9KMtqQmdKAte1W0GLObl/lsW9uuWRRk+EJuloJT993ED
v6TLFuf4DS1B+8c0Yg==
"""


class TestCertiNextFinalizer:
    responses: responses
    acme_neworder: Callable
    acme_client: acme.client.ClientV2

    @pytest.fixture(autouse=True)
    def setup_class_members(self, responses: responses, acme_neworder, acme_client):
        ApplicationSettings.get().finalizer = CertiNextFinalizerSettings(
            api_base="http://certinext.localhost/api/",
            account_number="1234",
            auth_key="123456789",
            product_code="prod1",
            prevetted_org_number="819",
            prevetting_token="tok-12345",
            requestor_mobile_number="123-432-0481",
            requestor_email="email@localhost",
            poll_interval=0,
            poll_deadline=0,
        )

        self._mock_track_order_calls = 0

        self.responses = responses
        self.acme_neworder = acme_neworder
        self.acme_client = acme_client

    def _mock_generate_order_ssl(
        self, status_code=200, response_values={}, response_override: dict = None
    ):
        response = (
            json.dumps(response_override)
            if response_override
            else """{{
            "orderDetails": {{
                "requestNumber": "{requestNumber}",
                "orderNumber": "{orderNumber}",
                "trackingURL": "https://certinext.localhost/tracking"
            }},
            "meta": {{
                "ver": "1.0",
                "errorMessage": "{errorMessage}",
                "errorCode": "{errorCode}",
                "txn": "{txn}",
                "ts": "{ts}",
                "status": "{status}"
            }}
        }}""".format(
                **(
                    {
                        "requestNumber": "12345",
                        "orderNumber": "54321",
                        "errorMessage": "",
                        "errorCode": "",
                        "txn": "1234-5678",
                        "ts": "2024-04-04T11:36:55+05:30",
                        "status": "1",
                    }
                    | response_values
                )
            )
        )

        def generate_callback(request):
            return (status_code, {}, response)

        self.responses.add_callback(
            responses.POST,
            CertiNextFinalizerSettings.get().api_base + "GenerateOrderSSL",
            callback=generate_callback,
        )

    def _mock_track_order(
        self,
        status_code=200,
        response_values={},
        response_override: dict = None,
        on_called: Callable = None,
    ):
        response = (
            json.dumps(response_override)
            if response_override
            else """{{
            "orderDetails": {{
                "orderStatusId": "{orderStatusId}",
                "orderStatus": "{orderStatus}",
                "certificateStatusId": "{certificateStatusId}",
                "certificateStatus": "{certificateStatus}"
            }},
            "meta": {{
                "ver": "1.0",
                "errorMessage": "{errorMessage}",
                "errorCode": "{errorCode}",
                "txn": "{txn}",
                "ts": "{ts}",
                "status": "{status}"
            }}
        }}""".format(
                **(
                    {
                        "requestNumber": "12345",
                        "orderNumber": "54321",
                        "errorMessage": "",
                        "errorCode": "",
                        "txn": "1234-5678",
                        "ts": "2024-04-04T11:36:55+05:30",
                        "orderStatusId": "6",
                        "orderStatus": "Order fulfilled",
                        "certificateStatusId": "20",
                        "certificateStatus": "Certificate Generated",
                        "status": "1",
                    }
                    | response_values
                )
            )
        )

        def generate_callback(request):
            self._mock_track_order_calls += 1
            if on_called:
                on_called()

            return (status_code, {}, response)

        self.responses.add_callback(
            responses.POST,
            CertiNextFinalizerSettings.get().api_base + "TrackOrder",
            callback=generate_callback,
        )

    def _mock_get_certificate(
        self,
        status_code=200,
        response_values={},
        response_override: dict = None,
        on_called: Callable = None,
    ):
        response = (
            json.dumps(response_override)
            if response_override
            else """{{
            "certificateDetails": {{
                "rootCertificate": "{rootCertificate}",
                "caCertificate": "{caCertificate}",
                "endEntityCertificate": "{endEntityCertificate}"
            }},
            "meta": {{
                "ver": "1.0",
                "errorMessage": "{errorMessage}",
                "errorCode": "{errorCode}",
                "txn": "{txn}",
                "ts": "{ts}",
                "status": "{status}"
            }}
        }}""".format(
                **(
                    {
                        "rootCertificate": DUMMY_ROOT_CERT.replace("\n", ""),
                        "caCertificate": DUMMY_CA_CERT.replace("\n", ""),
                        "endEntityCertificate": DUMMY_END_ENTITY_CERT.replace("\n", ""),
                        "errorMessage": "",
                        "errorCode": "",
                        "txn": "1234-5678",
                        "ts": "2024-04-04T11:36:55+05:30",
                        "status": "1",
                    }
                    | response_values
                )
            )
        )

        def generate_callback(request):
            if on_called:
                on_called()

            return (status_code, {}, response)

        self.responses.add_callback(
            responses.POST,
            CertiNextFinalizerSettings.get().api_base + "GetCertificate",
            callback=generate_callback,
        )

    def _get_processed_order(self, expect_failure=False) -> db.Order:
        new_order: NewOrderRet = self.acme_neworder()
        order = do_challenge(self.acme_client, new_order.response)

        if expect_failure:
            with pytest.raises(errors.TimeoutError):
                # This always errors, so make it happen fast
                order = finalize_order(self.acme_client, order, timeout=0)
        else:
            order = finalize_order(self.acme_client, order, timeout=0)

        order_name = order.uri.split("/")[-1]
        return db.Order.objects.get(name=order_name)

    @pytest.mark.django_db
    def test_fail_generate_unauth(
        self,
    ):
        # 401s should record an error
        self._mock_generate_order_ssl(
            401, response_values={"errorMessage": "Unauthorized", "errorCode": "401"}
        )
        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.SUBMITTED
        )
        assert db.OrderFinalizationError.objects.count() == 1

    @pytest.mark.django_db
    def test_fail_generate_malformed(
        self,
    ):
        # Responses that don't validate against the schema should record an error
        self._mock_generate_order_ssl(
            status_code=200, response_override={"invalid": "yes"}
        )
        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.SUBMITTED
        )
        assert db.OrderFinalizationError.objects.count() == 1

    @pytest.mark.django_db
    def test_fail_canceled_order(
        self,
    ):
        # Responses that return a 4 should fail
        self._mock_generate_order_ssl()
        self._mock_track_order(
            response_values={"orderStatusId": "4", "orderStatus": "Order rejected"}
        )
        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.ORDERED
        )
        assert db.OrderFinalizationError.objects.count() == 1
        assert "Invalid state" in db.OrderFinalizationError.objects.first().error

    @pytest.mark.django_db
    def test_fail_deadline_exceeded(
        self,
    ):
        self._mock_generate_order_ssl()
        self._mock_track_order(
            response_values={"orderStatusId": "3", "orderStatus": "In progress"}
        )
        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.ORDERED
        )
        assert db.OrderFinalizationError.objects.count() == 1
        assert "deadline exceeded" in db.OrderFinalizationError.objects.first().error

    @pytest.mark.django_db
    @pytest.mark.skip
    def test_fail_collection(self):
        self._mock_generate_order_ssl()
        self._mock_track_order()
        self._mock_get_certificate(status_code=500)

        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.FULFILLED
        )
        assert db.OrderFinalizationError.objects.count() == 1
        assert "HTTP_500" in db.OrderFinalizationError.objects.first().error

    @pytest.mark.django_db
    def test_retry_collection(self):
        CertiNextFinalizerSettings.get().poll_deadline = 1
        self._mock_generate_order_ssl()
        # The first call returns a pending status and the next call returns
        # a passing status. This simulates polling and forces the polling
        # loop to run.
        self._mock_track_order(
            response_values={"orderStatusId": "1"},
            on_called=lambda: self._mock_track_order(),
        )
        self._mock_get_certificate()

        order = self._get_processed_order(expect_failure=True)

        processing_state = db.CertiNextOrderProcessingState.for_order(order)

        assert (
            processing_state.state == db.CertiNextOrderProcessingState.Choices.COLLECTED
        )
        assert db.OrderFinalizationError.objects.count() == 0
        assert self._mock_track_order_calls == 2
