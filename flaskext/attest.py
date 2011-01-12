from __future__ import absolute_import
from __future__ import with_statement
from contextlib import contextmanager
from flask import (Response, request, template_rendered as jinja_rendered)
from flask.signals import Namespace
from flask.testing import FlaskClient
from functools import wraps
from attest import Tests


signals = Namespace()
template_rendered = signals.signal('template-rendered')


class ComparableResponse(Response):

    def __eq__(self, other):
        self.freeze()
        other.freeze()
        other.headers[:] = other.get_wsgi_headers(request.environ)
        return all(getattr(self, name) == getattr(other, name)
                   for name in ('status_code', 'headers', 'data'))

    def __ne__(self, other):
        return not self == other


class AppTests(Tests):

    capture_templates = False

    def __init__(self, appfactory, *args, **kwargs):
        Tests.__init__(self, *args, **kwargs)

        @self.context
        def request_context():
            app = appfactory()

            @jinja_rendered.connect_via(app)
            def signal_jinja(sender, template, context):
                template_rendered.send(self, template=template.name,
                                       context=context)

            with app_context(app) as client:
                yield client

        @self.context
        def capture_templates():
            templates = []

            if self.capture_templates:
                def capture(sender, template, context):
                    templates.append((template, context))

                with template_rendered.connected_to(capture):
                    yield templates
            else:
                yield


@contextmanager
def app_context(app):
    with app.test_request_context():
        cls = getattr(app, 'test_client_class', FlaskClient)
        with cls(app, ComparableResponse) as client:
            yield client


def open(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(client, *wrapperargs, **wrapperkwargs):
            response = client.open(*args, **kwargs)
            return func(response, *wrapperargs, **wrapperkwargs)
        return wrapper
    return decorator


def get(*args, **kwargs):
    kwargs['method'] = 'GET'
    return open(*args, **kwargs)

def post(*args, **kwargs):
    kwargs['method'] = 'POST'
    return open(*args, **kwargs)

def head(*args, **kwargs):
    kwargs['method'] = 'HEAD'
    return open(*args, **kwargs)

def put(*args, **kwargs):
    kwargs['method'] = 'PUT'
    return open(*args, **kwargs)

def delete(*args, **kwargs):
    kwargs['method'] = 'DELETE'
    return open(*args, **kwargs)
