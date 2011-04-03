Flask-Attest
============

.. module:: flaskext.attest


Testing Requests
----------------

We first need to set up a context manager that our tests will run in.
Assuming we have an application factory that takes an argument for
:meth:`~flask.Config.from_object`, here's a basic setup::

    from flaskext.attest import request_context
    from myapp import create_app

    TESTING = True

    @request_context
    def testapp():
        return create_app(__name__)

The function decorated with :func:`request_context` should simply return a
Flask application. The decorated function is turned into a context manager
that creates the application, enters a test request context and connects
some templating signals. The context manager returns a
:meth:`~flask.Flask.test_client` and a list which is mutated every time a
template is rendered, appending a tuple of the template name and context.

What this means for Attest is we can pass this context manager to test
collections and those tests will run in a test request context and receive
two arguments, ``client`` and ``templates``::

    import json
    from attest import Tests

    api = Tests(contexts=[testapp])

    @api.test
    def should_do_json(client, templates):
        response = client.get('/api/')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        assert json.loads(response.data) == {'status': 'All systems go.'}

There's some sugar we can use to clean up this example. First, there's a
:func:`get` decorator which replaces the client argument with a response.
Second, Attest only passes as many arguments to tests as their signature is
asking for. We're not using the templates list here so we can simply
exclude it completely. Last, the responses returned by the test client can
be compared against other response objects, which will compare the status
code, the headers and the data. Our refactored test::

    from flaskext.attest import get
    from flask import jsonify

    @api.test
    @get('/api/')
    def should_do_json(response):
        assert response == jsonify(status='All systems go.')

This use of :func:`~flask.jsonify` works because it returns a response
object, and as a result we're doing all the same checks as in the first
version of our test, and possibly more because we're comparing all headers.
This also works with :func:`~flask.redirect`.


Captured Templates
------------------

If anything calls :func:`~flask.render_template` during a test, a tuple is
appended to the ``templates`` list that is passed to the test. Say we're
testing a view like this one::

    @app.route('/')
    def index():
        return render_template('index.html', title='Welcome to Awesome Ltd.')

The templates list should be empty until we issue ``client.get('/')``. If
we're using the :func:`get` decorator it'll already have happened before
our test code executes. After a request has been issued, the templates list
should look like this::

    [('index.html', {'title': 'Welcome to Awesome Ltd.'})]

The gist of it all is that you can write checks for how many templates were
rendered, exactly which templates were rendered and in what order, and with
what context.

.. note::

    This works out-of-the-box for Flask's built in support for Jinja2, and
    with the Flask-Genshi extension. For other toolkits, see
    :data:`template_rendered` for how to extend the capturing.


API Reference
-------------

.. autofunction:: request_context

.. autofunction:: open

.. autofunction:: get

.. autofunction:: post

.. autofunction:: put

.. autofunction:: delete

.. autofunction:: head

.. autoclass:: TestResponse

.. data:: template_rendered

    Signal that fills the templates list for tests. Emit this to support
    templating toolkits other than Jinja and Genshi (via Flask-Genshi).
    Expects a ``template`` argument that should be the name of the rendered
    template, and a ``context`` argument that should be the context
    dictionary the template renders in.
