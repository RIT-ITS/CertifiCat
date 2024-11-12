from .contextvars import request_context


def global_request_middleware(get_response):
    def middleware(request):
        request_context.set(request)
        response = get_response(request)

        return response

    return middleware
