from __future__ import absolute_import
from __future__ import with_statement
from contextlib import contextmanager
from flask import (Response, request, template_rendered as jinja_rendered)
from flask.signals import Namespace
from flask.testing import FlaskClient
from decorator import decorator


def request_context(appfactory):
    """Decorator that creates a test context out of a function that returns
    a Flask application."""

    @contextmanager
    def test_request_context():
        app = appfactory()
        templates = []

        def capture(sender, template, context):
            templates.append((template, context))

        @jinja_rendered.connect_via(app)
        def signal_jinja(sender, template, context):
            template_rendered.send(None, template=template.name,
                                   context=context)

        try:
            from flaskext.genshi import template_generated
        except ImportError:
            pass
        else:
            @template_generated.connect_via(app)
            def signal_genshi(sender, template, context):
                template_rendered.send(None, template=template.filename,
                                       context=context)

        with app_context(app) as client:
            with template_rendered.connected_to(capture):
                yield client, templates

    return test_request_context


@contextmanager
def app_context(app):
    with app.test_request_context():
        cls = getattr(app, 'test_client_class', None) or FlaskClient
        with cls(app, TestResponse) as client:
            yield client


def open(*args, **kwargs):
    """Wraps a test with a call to :meth:`~werkzeug.test.Client.open` on
    the test client, passing the response instead of the client to the
    test."""
    @decorator
    def wrapper(func, client, *wrapperargs, **wrapperkwargs):
        response = client.open(*args, **kwargs)
        return func(response, *wrapperargs, **wrapperkwargs)
    return wrapper


def get(*args, **kwargs):
    """Decorates a test to issue a GET request to the application. This is
    sugar for ``@open(method='GET')``. Arguments are the same as to
    :class:`~werkzeug.test.EnvironBuilder`.

    Typical usage::

        @frontend.test
        @get('/')
        def index(response):
            assert 'Welcome!' in response.data

    """
    kwargs['method'] = 'GET'
    return open(*args, **kwargs)

def post(*args, **kwargs):
    """Issue a POST request, like :func:`get`."""
    kwargs['method'] = 'POST'
    return open(*args, **kwargs)

def put(*args, **kwargs):
    """Issue a PUT request, like :func:`get`."""
    kwargs['method'] = 'PUT'
    return open(*args, **kwargs)

def delete(*args, **kwargs):
    """Issue a DELETE request, like :func:`get`."""
    kwargs['method'] = 'DELETE'
    return open(*args, **kwargs)

def head(*args, **kwargs):
    """Issue a HEAD request, like :func:`get`."""
    kwargs['method'] = 'HEAD'
    return open(*args, **kwargs)


class TestResponse(Response):
    """A :class:`~flask.Response` adapted to testing, this is returned by
    the test client. The added feature is that it can be compared against
    other response objects."""

    def __eq__(self, other):
        self.freeze()
        other.freeze()
        other.headers[:] = other.get_wsgi_headers(request.environ)
        return all(getattr(self, name) == getattr(other, name)
                   for name in ('status_code', 'headers', 'data'))

    def __ne__(self, other):
        return not self == other


signals = Namespace()
template_rendered = signals.signal('template-rendered')
