Flask-Attest
============

.. module:: flaskext.attest

An extension of Flask for automated testing using Attest.

Features:

* Flask-like API
* Handling of request contexts in tests
* Captures metadata about rendered templates
* Flexible library with few assumptions
* Write test conditions naturally with the :keyword:`assert` statement

Install from PyPI to get started quickly::

    easy_install Flask-Attest

For serious use it's usually better to list it as a test dependency,
though.


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
        yield create_app(__name__)

The :func:`request_context` decorator is similar to
:func:`~contextlib.contextmanager` and the decorated generator function
should simply yield a Flask application. If needed you can surround the
yield with code that should run before and after tests, and that need the
application instance.

The result is a new context manager that also enters a test request context
and connects signals for recording any rendering of templates. The context
manager returns a :meth:`~flask.Flask.test_client` and a list which is
mutated every time a template is rendered, appending a tuple of the
template name and context.

What this means for Attest is we can pass this context manager to test
collections and those tests will run in a test request context and receive
two arguments, `client` and `templates`::

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


File Layout for Test Suites
---------------------------

No particular layout is enforced. A common convention is to put the tests
in a `tests` package with a master collection in the package top-level.

.. rubric:: tests/__init__.py

::

    from attest import Tests
    all = Tests(['tests.views.frontend', 'tests.views.admin'])

Then you could have a `contexts` module to hold our ``@request_context``
and any other context managers we might find useful to reuse.

.. rubric:: tests/contexts.py

::

    from flaskext.attest import request_context
    from myapp import create_app

    TESTING = True

    @request_context
    def testapp():
        yield create_app(__name__)

The tests themselves we also put in modules under the tests package. In
this case we had listed `views` as a package with two test collections.

.. rubric:: tests/views.py

::

    from attest import Tests, assert_hook
    from .contexts import testapp

    frontend = Tests(contexts=[testapp])
    admin = Tests(contexts=[testapp])

Now you can run your suite:

.. code-block:: bash

    python -mattest tests.all  # -mattest.run on Python 2.6 and older


Captured Templates
------------------

If anything calls :func:`~flask.render_template` during a test, a tuple is
appended to the `templates` list that is passed to the test. Say we're
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


Customizing Test Contexts
-------------------------

Attest lets you register multiple contexts so it is easy to do things such
as setting up database fixtures::

    admin = Tests(contexts=[testapp])

    @admin.context
    def dbfixtures():
        data = setup_fixtures()
        yield data
        teardown_fixtures()

Tests in this `admin` collection would receive three arguments - `client`,
`templates` and `data`. The arguments are positional so the names have no
significance, and you only get as many arguments as you ask for. If however
you only want the last one, you still have to write a signature for three
arguments. You can work around this by using the `testapp` context manually
in your own context, and simply ignore what it returns::

    admin = Tests()

    @admin.context
    def dbfixtures():
        with testapp():
            data = setup_fixtures()
            yield data
            teardown_fixtures()

If you find yourself doing things like this a lot you can always write
normal context managers and pass references to them to ``Tests()``, like we
have been doing with `testapp`.


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
    Expects a `template` argument that should be the name of the rendered
    template, and a `context` argument that should be the context
    dictionary the template renders in.
