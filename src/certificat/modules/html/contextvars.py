from contextvars import ContextVar

request_context: ContextVar = ContextVar("request", default=None)
