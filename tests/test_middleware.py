from unittest import mock

import middlewares
import exceptions


async def handler_func(request, *args, **kwargs):
    exc = request
    raise exc("Test exception")


async def handle_http_error(*args, **kwargs):
    return kwargs.get('status', None)


async def test_error_middleware_500():
    with mock.patch('middlewares.handle_http_error', handle_http_error):
        res = await middlewares.error_middleware(request=Exception, handler=handler_func)
    assert res == 500


async def test_error_middleware_400():
    with mock.patch('middlewares.handle_http_error', handle_http_error):
        res = await middlewares.error_middleware(request=exceptions.BadRequest, handler=handler_func)
    assert res == 400


async def test_error_middleware_404():
    with mock.patch('middlewares.handle_http_error', handle_http_error):
        res = await middlewares.error_middleware(request=exceptions.RecordNotFound, handler=handler_func)
    assert res == 404


async def test_error_middleware_403():
    with mock.patch('middlewares.handle_http_error', handle_http_error):
        res = await middlewares.error_middleware(request=exceptions.UserIsNotActivated, handler=handler_func)
    assert res == 403
