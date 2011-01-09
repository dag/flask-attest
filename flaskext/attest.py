from __future__ import absolute_import
from __future__ import with_statement
from flask import Response
from flask.testing import FlaskClient
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
        def client_context():
            app = appfactory()
            with app.test_request_context():
                with FlaskClient(app, ComparableResponse) as client:
                    yield client


def open(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(client):
            response = client.open(*args, **kwargs)
            return func(response)
        return wrapper
    return decorator


def get(*args, **kwargs):
    return open(*args, method='GET', **kwargs)

def post(*args, **kwargs):
    return open(*args, method='POST', **kwargs)

def head(*args, **kwargs):
    return open(*args, method='HEAD', **kwargs)

def put(*args, **kwargs):
    return open(*args, method='PUT', **kwargs)

def delete(*args, **kwargs):
    return open(*args, method='DELETE', **kwargs)
