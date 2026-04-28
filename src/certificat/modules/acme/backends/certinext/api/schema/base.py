from pydantic import BaseModel


class RequestMeta(BaseModel):
    ver: str = "1.0"
    ts: str
    txn: str
    accountNumber: str
    authKey: str


class ResponseMeta(BaseModel):
    # Should always be 1
    ver: str
    # May only exist on error
    errorMessage: str = ""
    # May only exist on error
    errorCode: str = ""
    # Transaction from passed-in request
    txn: str
    # Timestamp in ISO 8601 format
    ts: str
    # 1 - success, 2 - failure
    status: str
