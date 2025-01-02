from certificat.modules.html.contextvars import request_context


def set_request_context(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        request_context.set(request)

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
