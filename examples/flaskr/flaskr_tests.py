# -*- coding: utf-8 -*-
"""
    Flaskr Tests
    ~~~~~~~~~~~~

    Tests the Flaskr application.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import tempfile
import os

from flask.testing import FlaskClient
from flaskext.attest import request_context, get
from attest import Tests, assert_hook

import flaskr


class FlaskrClient(FlaskClient):
    """Add some capabilities to the test client."""

    def login(self, username, password):
        return self.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.get('/logout', follow_redirects=True)


@request_context
def testapp():
    flaskr.app.test_client_class = FlaskrClient
    yield flaskr.app


app = Tests(contexts=[testapp])

@app.context
def tempdb():
    """Before each test, set up a blank database"""
    fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flaskr.init_db()
    try:
        yield
    finally:
        os.close(fd)
        os.unlink(flaskr.app.config['DATABASE'])


@app.test
@get('/')
def empty_db(rv):
    """Start with a blank database."""
    assert 'No entries here so far' in rv.data


@app.test
def login_logout(client):
    """Make sure login and logout works"""
    rv = client.login(flaskr.app.config['USERNAME'],
                      flaskr.app.config['PASSWORD'])
    assert 'You were logged in' in rv.data
    rv = client.logout()
    assert 'You were logged out' in rv.data
    rv = client.login(flaskr.app.config['USERNAME'] + 'x',
                      flaskr.app.config['PASSWORD'])
    assert 'Invalid username' in rv.data
    rv = client.login(flaskr.app.config['USERNAME'],
                      flaskr.app.config['PASSWORD'] + 'x')
    assert 'Invalid password' in rv.data


@app.test
def messages(client):
    """Test that messages work"""
    client.login(flaskr.app.config['USERNAME'],
                 flaskr.app.config['PASSWORD'])
    rv = client.post('/add', data=dict(
        title='<Hello>',
        text='<strong>HTML</strong> allowed here'
    ), follow_redirects=True)
    assert 'No entries here so far' not in rv.data
    assert '&lt;Hello&gt;' in rv.data
    assert '<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    app.main()
