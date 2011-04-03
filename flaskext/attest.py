from __future__ import absolute_import
from __future__ import with_statement
from contextlib import contextmanager
from flask import (Response, request, template_rendered as jinja_rendered)
from flask.signals import Namespace
from flask.testing import FlaskClient
from decorator import decorator


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


def test_context(appfactory):

    @contextmanager
    def request_context():
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

    return request_context


@contextmanager
def app_context(app):
    with app.test_request_context():
        cls = getattr(app, 'test_client_class', FlaskClient)
        with cls(app, ComparableResponse) as client:
            yield client


def open(*args, **kwargs):
    @decorator
    def wrapper(func, client, *wrapperargs, **wrapperkwargs):
        response = client.open(*args, **kwargs)
        return func(response, *wrapperargs, **wrapperkwargs)
    return wrapper


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
