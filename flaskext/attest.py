from __future__ import absolute_import
from functools import wraps
from attest import Tests


class AppTests(Tests):

    def __init__(self, appfactory, *args, **kwargs):
        Tests.__init__(self, *args, **kwargs)

        @self.context
        def request_context():
            app = appfactory()
            client = app.test_client()
            yield client


def get(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(client):
            return func(client.get(*args, **kwargs))
        return wrapper
    return decorator
