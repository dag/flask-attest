Flask-Attest
============

Test Flask applications with Attest, with an API inspired by Flask.

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
