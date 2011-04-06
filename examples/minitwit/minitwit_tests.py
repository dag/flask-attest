# -*- coding: utf-8 -*-
"""
    MiniTwit Tests
    ~~~~~~~~~~~~~~

    Tests the MiniTwit application.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import tempfile
import os

from flask.testing import FlaskClient
from flaskext.attest import request_context
from attest import Tests, assert_hook

import minitwit


class MiniTwitClient(FlaskClient):
    """Add some capabilities to the test client."""

    def register(self, username, password, password2=None, email=None):
        """Helper function to register a user"""
        if password2 is None:
            password2 = password
        if email is None:
            email = username + '@example.com'
        return self.post('/register', data={
            'username':     username,
            'password':     password,
            'password2':    password2,
            'email':        email,
        }, follow_redirects=True)

    def login(self, username, password):
        """Helper function to login"""
        return self.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def register_and_login(self, username, password):
        """Registers and logs in in one go"""
        self.register(username, password)
        return self.login(username, password)

    def logout(self):
        """Helper function to logout"""
        return self.get('/logout', follow_redirects=True)

    def add_message(self, text):
        """Records a message"""
        rv = self.post('/add_message', data={'text': text},
                       follow_redirects=True)
        if text:
            assert 'Your message was recorded' in rv.data
        return rv


@request_context
def testapp():
    minitwit.app.test_client_class = MiniTwitClient
    yield minitwit.app


app = Tests(contexts=[testapp])

@app.context
def tempdb():
    """Before each test, set up a blank database"""
    fd, minitwit.app.config['DATABASE'] = tempfile.mkstemp()
    minitwit.init_db()
    try:
        yield
    finally:
        os.close(fd)
        os.unlink(minitwit.app.config['DATABASE'])


@app.test
def register(client):
    """Make sure registering works"""
    rv = client.register('user1', 'default')
    assert 'You were successfully registered ' \
           'and can login now' in rv.data
    rv = client.register('user1', 'default')
    assert 'The username is already taken' in rv.data
    rv = client.register('', 'default')
    assert 'You have to enter a username' in rv.data
    rv = client.register('meh', '')
    assert 'You have to enter a password' in rv.data
    rv = client.register('meh', 'x', 'y')
    assert 'The two passwords do not match' in rv.data
    rv = client.register('meh', 'foo', email='broken')
    assert 'You have to enter a valid email address' in rv.data


@app.test
def login_logout(client):
    """Make sure logging in and logging out works"""
    rv = client.register_and_login('user1', 'default')
    assert 'You were logged in' in rv.data
    rv = client.logout()
    assert 'You were logged out' in rv.data
    rv = client.login('user1', 'wrongpassword')
    assert 'Invalid password' in rv.data
    rv = client.login('user2', 'wrongpassword')
    assert 'Invalid username' in rv.data


@app.test
def message_recording(client):
    """Check if adding messages works"""
    client.register_and_login('foo', 'default')
    client.add_message('test message 1')
    client.add_message('<test message 2>')
    rv = client.get('/')
    assert 'test message 1' in rv.data
    assert '&lt;test message 2&gt;' in rv.data


@app.test
def timelines(client):
    """Make sure that timelines work"""
    client.register_and_login('foo', 'default')
    client.add_message('the message by foo')
    client.logout()
    client.register_and_login('bar', 'default')
    client.add_message('the message by bar')
    rv = client.get('/public')
    assert 'the message by foo' in rv.data
    assert 'the message by bar' in rv.data

    # bar's timeline should just show bar's message
    rv = client.get('/')
    assert 'the message by foo' not in rv.data
    assert 'the message by bar' in rv.data

    # now let's follow foo
    rv = client.get('/foo/follow', follow_redirects=True)
    assert 'You are now following &#34;foo&#34;' in rv.data

    # we should now see foo's message
    rv = client.get('/')
    assert 'the message by foo' in rv.data
    assert 'the message by bar' in rv.data

    # but on the user's page we only want the user's message
    rv = client.get('/bar')
    assert 'the message by foo' not in rv.data
    assert 'the message by bar' in rv.data
    rv = client.get('/foo')
    assert 'the message by foo' in rv.data
    assert 'the message by bar' not in rv.data

    # now unfollow and check if that worked
    rv = client.get('/foo/unfollow', follow_redirects=True)
    assert 'You are no longer following &#34;foo&#34;' in rv.data
    rv = client.get('/')
    assert 'the message by foo' not in rv.data
    assert 'the message by bar' in rv.data


if __name__ == '__main__':
    app.main()
