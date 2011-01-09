from __future__ import absolute_import
from flask import Response
from functools import wraps
from attest import Tests


class ComparableResponse(Response):

    def __eq__(self, other):
        self.freeze()
        other.freeze()
        return all(getattr(self, name) == getattr(other, name)
                   for name in ('status_code', 'headers', 'data'))

    def __ne__(self, other):
        return not self == other


class AppTests(Tests):

    def __init__(self, appfactory, *args, **kwargs):
        Tests.__init__(self, *args, **kwargs)

        @self.context
        def request_context():
            app = appfactory()
            app.response_class, orig = ComparableResponse, app.response_class
            client = app.test_client()
            app.response_class = orig
            yield client


def get(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(client):
            response = client.get(*args, **kwargs)
            return func(response)
        return wrapper
    return decorator
