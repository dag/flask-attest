Flask-Attest
============

An extension of Flask for automated testing using Attest.

Features:

* Flask-like API
* Handling of request contexts in tests
* Captures metadata about rendered templates
* Flexible library with few assumptions
* Write test conditions naturally with the `assert` statement

::

    from flaskext.attest import request_context, get
    from myapp import app 
    from attest import Tests
    from flask import Response

    TESTING = True

    @request_context
    def testapp():
        app.config.from_object(__name__)
        return app

    frontend = Tests(context=[testapp])

    @frontend.test
    @get('/')
    def index(response):
        assert response == Response('Welcome!')
