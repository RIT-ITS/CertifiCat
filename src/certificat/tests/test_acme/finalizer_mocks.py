import datetime
from certificat.modules.acme.backends import ErrorResponse
from certificat.modules.acme.backends.sectigo import (
    ApproveResponse,
    CollectResponse,
    EnrollResponse,
    GetResponse,
    SectigoFinalizer,
    SectigoBackend,
)

bundle = """-----BEGIN CERTIFICATE-----
MIIEMjCCAxqgAwIBAgIBATANBgkqhkiG9w0BAQUFADB7MQswCQYDVQQGEwJHQjEb
MBkGA1UECAwSR3JlYXRlciBNYW5jaGVzdGVyMRAwDgYDVQQHDAdTYWxmb3JkMRow
GAYDVQQKDBFDb21vZG8gQ0EgTGltaXRlZDEhMB8GA1UEAwwYQUFBIENlcnRpZmlj
YXRlIFNlcnZpY2VzMB4XDTA0MDEwMTAwMDAwMFoXDTI4MTIzMTIzNTk1OVowezEL
MAkGA1UEBhMCR0IxGzAZBgNVBAgMEkdyZWF0ZXIgTWFuY2hlc3RlcjEQMA4GA1UE
BwwHU2FsZm9yZDEaMBgGA1UECgwRQ29tb2RvIENBIExpbWl0ZWQxITAfBgNVBAMM
GEFBQSBDZXJ0aWZpY2F0ZSBTZXJ2aWNlczCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBAL5AnfRu4ep2hxxNRUSOvkbIgwadwSr+GB+O5AL686tdUIoWMQua
BtDFcCLNSS1UY8y2bmhGC1Pqy0wkwLxyTurxFa70VJoSCsN6sjNg4tqJVfMiWPPe
3M/vg4aijJRPn2jymJBGhCfHdr/jzDUsi14HZGWCwEiwqJH5YZ92IFCokcdmtet4
YgNW8IoaE+oxox6gmf049vYnMlhvB/VruPsUK6+3qszWY19zjNoFmag4qMsXeDZR
rOme9Hg6jc8P2ULimAyrL58OAd7vn5lJ8S3frHRNG5i1R8XlKdH5kBjHYpy+g8cm
ez6KJcfA3Z3mNWgQIJ2P2N7Sw4ScDV7oL8kCAwEAAaOBwDCBvTAdBgNVHQ4EFgQU
oBEKIz6W8Qfs4q8p74Klf9AwpLQwDgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB/wQF
MAMBAf8wewYDVR0fBHQwcjA4oDagNIYyaHR0cDovL2NybC5jb21vZG9jYS5jb20v
QUFBQ2VydGlmaWNhdGVTZXJ2aWNlcy5jcmwwNqA0oDKGMGh0dHA6Ly9jcmwuY29t
b2RvLm5ldC9BQUFDZXJ0aWZpY2F0ZVNlcnZpY2VzLmNybDANBgkqhkiG9w0BAQUF
AAOCAQEACFb8AvCb6P+k+tZ7xkSAzk/ExfYAWMymtrwUSWgEdujm7l3sAg9g1o1Q
GE8mTgHj5rCl7r+8dFRBv/38ErjHT1r0iWAFf2C3BUrz9vHCv8S5dIa2LX1rzNLz
Rt0vxuBqw8M0Ayx9lt1awg6nCpnBBYurDC/zXDrPbDdVCYfeU0BsWO/8tqtlbgT2
G9w84FoVxp7Z8VlIMCFlA2zs6SFz7JsDoeA3raAVGI/6ugLOpyypEBMs1OUIJqsi
l2D4kF501KKaU73yqWjgom7C12yxow+ev+to51byrvLjKzg6CYG1a4XXvi3tPxq3
smPi9WIsgtRqAEFQ8TmDn5XpNpaYbg==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFgTCCBGmgAwIBAgIQOXJEOvkit1HX02wQ3TE1lTANBgkqhkiG9w0BAQwFADB7
MQswCQYDVQQGEwJHQjEbMBkGA1UECAwSR3JlYXRlciBNYW5jaGVzdGVyMRAwDgYD
VQQHDAdTYWxmb3JkMRowGAYDVQQKDBFDb21vZG8gQ0EgTGltaXRlZDEhMB8GA1UE
AwwYQUFBIENlcnRpZmljYXRlIFNlcnZpY2VzMB4XDTE5MDMxMjAwMDAwMFoXDTI4
MTIzMTIzNTk1OVowgYgxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpOZXcgSmVyc2V5
MRQwEgYDVQQHEwtKZXJzZXkgQ2l0eTEeMBwGA1UEChMVVGhlIFVTRVJUUlVTVCBO
ZXR3b3JrMS4wLAYDVQQDEyVVU0VSVHJ1c3QgUlNBIENlcnRpZmljYXRpb24gQXV0
aG9yaXR5MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAgBJlFzYOw9sI
s9CsVw127c0n00ytUINh4qogTQktZAnczomfzD2p7PbPwdzx07HWezcoEStH2jnG
vDoZtF+mvX2do2NCtnbyqTsrkfjib9DsFiCQCT7i6HTJGLSR1GJk23+jBvGIGGqQ
Ijy8/hPwhxR79uQfjtTkUcYRZ0YIUcuGFFQ/vDP+fmyc/xadGL1RjjWmp2bIcmfb
IWax1Jt4A8BQOujM8Ny8nkz+rwWWNR9XWrf/zvk9tyy29lTdyOcSOk2uTIq3XJq0
tyA9yn8iNK5+O2hmAUTnAU5GU5szYPeUvlM3kHND8zLDU+/bqv50TmnHa4xgk97E
xwzf4TKuzJM7UXiVZ4vuPVb+DNBpDxsP8yUmazNt925H+nND5X4OpWaxKXwyhGNV
icQNwZNUMBkTrNN9N6frXTpsNVzbQdcS2qlJC9/YgIoJk2KOtWbPJYjNhLixP6Q5
D9kCnusSTJV882sFqV4Wg8y4Z+LoE53MW4LTTLPtW//e5XOsIzstAL81VXQJSdhJ
WBp/kjbmUZIO8yZ9HE0XvMnsQybQv0FfQKlERPSZ51eHnlAfV1SoPv10Yy+xUGUJ
5lhCLkMaTLTwJUdZ+gQek9QmRkpQgbLevni3/GcV4clXhB4PY9bpYrrWX1Uu6lzG
KAgEJTm4Diup8kyXHAc/DVL17e8vgg8CAwEAAaOB8jCB7zAfBgNVHSMEGDAWgBSg
EQojPpbxB+zirynvgqV/0DCktDAdBgNVHQ4EFgQUU3m/WqorSs9UgOHYm8Cd8rID
ZsswDgYDVR0PAQH/BAQDAgGGMA8GA1UdEwEB/wQFMAMBAf8wEQYDVR0gBAowCDAG
BgRVHSAAMEMGA1UdHwQ8MDowOKA2oDSGMmh0dHA6Ly9jcmwuY29tb2RvY2EuY29t
L0FBQUNlcnRpZmljYXRlU2VydmljZXMuY3JsMDQGCCsGAQUFBwEBBCgwJjAkBggr
BgEFBQcwAYYYaHR0cDovL29jc3AuY29tb2RvY2EuY29tMA0GCSqGSIb3DQEBDAUA
A4IBAQAYh1HcdCE9nIrgJ7cz0C7M7PDmy14R3iJvm3WOnnL+5Nb+qh+cli3vA0p+
rvSNb3I8QzvAP+u431yqqcau8vzY7qN7Q/aGNnwU4M309z/+3ri0ivCRlv79Q2R+
/czSAaF9ffgZGclCKxO/WIu6pKJmBHaIkU4MiRTOok3JMrO66BQavHHxW/BBC5gA
CiIDEOUMsfnNkjcZ7Tvx5Dq2+UUTJnWvu6rvP3t3O9LEApE9GQDTF1w52z97GA1F
zZOFli9d31kWTz9RvdVFGD/tSo7oBmF0Ixa1DVBzJ0RHfxBdiSprhTEUxOipakyA
vGp4z7h/jnZymQyd/teRCBaho1+V
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIG3zCCBUegAwIBAgIQcO/ZthLLW7G3ONEfsTi3ADANBgkqhkiG9w0BAQwFADBE
MQswCQYDVQQGEwJVUzESMBAGA1UEChMJSW50ZXJuZXQyMSEwHwYDVQQDExhJbkNv
bW1vbiBSU0EgU2VydmVyIENBIDIwHhcNMjQwMTA5MDAwMDAwWhcNMjUwMTA4MjM1
OTU5WjBrMQswCQYDVQQGEwJVUzERMA8GA1UECBMITmV3IFlvcmsxKjAoBgNVBAoT
IVJvY2hlc3RlciBJbnN0aXR1dGUgb2YgVGVjaG5vbG9neTEdMBsGA1UEAxMUYWNt
ZS10ZXN0aW5nLnJpdC5lZHUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
AQDoZKg6yRoE218gSSOY39upee06fnbJpEaeh2yzlSr3yXVseEgIlej7kYgIeqRp
TX2yH5Hq6iJa256ZPr9E8lcJ+MWo/NZhZb1aAmMqcwmtCjhW/7xo18WB8gc/hm07
2OtbmQ5hhh8AAPuPn0NfxqxyGEyWXwqjjR5CHQrbvQpGTq3L14NohAvVAxQAHctt
XRdS3VfxlyYbkroM/5DJHCvdJdASRUeGbh+zctTQRwnFqWSb8OJTInazwrwp1+AK
ji27L6isVs13G12/++WyvQv5pLD7g48SQ/qhqTYnBPmrieuVsTi+hoVgLH9VDEne
SnbPhCKqQ+SE7mVhsGs/NqCfAgMBAAGjggMkMIIDIDAfBgNVHSMEGDAWgBTvTACS
pvt2Ll6V4slfhxsZ1U3i2TAdBgNVHQ4EFgQU40nFOq3EQnxu8lQeugiTJI07dOUw
DgYDVR0PAQH/BAQDAgWgMAwGA1UdEwEB/wQCMAAwHQYDVR0lBBYwFAYIKwYBBQUH
AwEGCCsGAQUFBwMCMEkGA1UdIARCMEAwNAYLKwYBBAGyMQECAmcwJTAjBggrBgEF
BQcCARYXaHR0cHM6Ly9zZWN0aWdvLmNvbS9DUFMwCAYGZ4EMAQICMEAGA1UdHwQ5
MDcwNaAzoDGGL2h0dHA6Ly9jcmwuc2VjdGlnby5jb20vSW5Db21tb25SU0FTZXJ2
ZXJDQTIuY3JsMHAGCCsGAQUFBwEBBGQwYjA7BggrBgEFBQcwAoYvaHR0cDovL2Ny
dC5zZWN0aWdvLmNvbS9JbkNvbW1vblJTQVNlcnZlckNBMi5jcnQwIwYIKwYBBQUH
MAGGF2h0dHA6Ly9vY3NwLnNlY3RpZ28uY29tMIIBfwYKKwYBBAHWeQIEAgSCAW8E
ggFrAWkAdgDPEVbu1S58r/OHW9lpLpvpGnFnSrAX7KwB0lt3zsw7CAAAAYzve7wy
AAAEAwBHMEUCIAH6Ifo+8lS7C+juHi+7LWfMUpiJ2cJYlkWKUxXJtpyZAiEA8YjT
fJrNdmbNqNjQN99UxlDQrs129HU7LMDV6/mlBvUAdwCi4wrkRe+9rZt+OO1HZ3dT
14JbhJTXK14bLMS5UKRH5wAAAYzve7xOAAAEAwBIMEYCIQDaUp7EP8FgzTtDJhWh
iE1H6yW/T7WRraOtBqB88WxNUQIhAPqobUi4425o+DPqHvjWke3StsbHcF6ZGaHF
RkBVhScwAHYATnWjJ1yaEMM4W2zU3z9S6x3w4I4bjWnAsfpksWKaOd8AAAGM73u7
3gAABAMARzBFAiA+p1KdlRPkZp0mFAoNcYNJDjj4Ixkv1jdZhum0dQn2wwIhAI6b
xkWnFdYonZy9xOs/zGvhwV9cbI9H+dyl44xYEmqlMB8GA1UdEQQYMBaCFGFjbWUt
dGVzdGluZy5yaXQuZWR1MA0GCSqGSIb3DQEBDAUAA4IBgQA0GZRWpBZi5fhH/9AH
YiyOYdqL+el1cISIwJTycAEwddwZtn4dzhLwIW8o0PHlNhhw/sZ73k5ppMKPguY5
CG1xYjVNIqK4TJkdB9Oa44Q3ZVpIz+SznWJG9wNOwIoG3NM+8kwOGugTipkgp0MY
1vomSohIHyxEBTXdzAZs6VGe89xXvCsZWA7HZE1Scu2BwRp92EsQaLtKlX2fgfdC
UevVvB/KdgbSHApp6qsZ195NGo5bJp0pf/iRzNsPiU8cJZZt1x5os3mQTlF2WJY5
MZnLR9QFwanvnYm9nSCdIsKiyDygU4UopTw06nyXjKnaHZnXq7NvuHHNkancrAMJ
uPr3T1Cna3xDRr7MPLAi9ELraDclDJZuLMdGKK56oMNDH+eLFpYDhNehEjNWMl2S
iLsXtR7ljc0CI8oiSqkIhqfcAT72MwWp7aAXMwSEijCjDvY4rEGIHPOPjtx7LLfa
rS57Byz7QJ+qRLynH4KtrLbRoqv2xw1yohe5xJ1UfrvVRyM=
-----END CERTIFICATE-----"""


class MockSectigoBackend(SectigoBackend):
    def __init__(self):
        self.poll_deadline = 1

    def enroll(self, order, csr) -> EnrollResponse:
        return EnrollResponse(200, ssl_id="12345")

    get_calls = 0

    def get(self, ssl_id: str) -> GetResponse:
        if self.get_calls == 0:
            self.get_calls += 1
            return GetResponse(200, cert_status="requested")

        return GetResponse(
            200, cert_status="approved", approved=datetime.datetime.now()
        )

    def approve(self, ssl_id: str, message: str) -> ApproveResponse:
        return ApproveResponse(200)

    def collect(self, ssl_id: str) -> CollectResponse:
        return CollectResponse(200, bundle=bundle)


class FlakySectigoBackend(MockSectigoBackend):
    # first call always fails
    def enroll(self, order, csr):
        import pdb

        pdb.set_trace()
        setattr(self, "enroll", super().enroll)
        return FailingEnrollMockSectigoBackend().enroll(order, csr)

        return super().enroll(order, csr)


class FailingEnrollMockSectigoBackend(MockSectigoBackend):
    def enroll(self, order, pem_csr) -> EnrollResponse:
        return EnrollResponse(500, ErrorResponse(1337, "Failure enrolling"))


class FailingApproveMockSectigoBackend(MockSectigoBackend):
    def approve(self, ssl_id, message) -> ApproveResponse:
        return ApproveResponse(500, ErrorResponse(2337, "Failure approving"))


class FailingGetMockSectigoBackend(MockSectigoBackend):
    def get(self, ssl_id) -> GetResponse:
        return GetResponse(500, ErrorResponse(3337, "Failure getting"))


class FailingCollectMockSectigoBackend(MockSectigoBackend):
    def collect(self, ssl_id) -> CollectResponse:
        return CollectResponse(500, ErrorResponse(4337, "Failure collecting"))


class MockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = MockSectigoBackend()


class FailingEnrollMockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = FailingEnrollMockSectigoBackend()


class FailingGetMockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = FailingGetMockSectigoBackend()


class FailingApproveMockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = FailingApproveMockSectigoBackend()


class FailingCollectMockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = FailingCollectMockSectigoBackend()


class FlakyMockSectigoFinalizer(SectigoFinalizer):
    def __init__(self):
        self.backend = FlakySectigoBackend()
