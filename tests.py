from __future__ import with_statement
from flask import Module, request, Flask, Response
from flaskext.attest import AppTests, get, post, delete
from attest import Assert

DEBUG = True
TESTING = True


db = {}
mod = Module(__name__, name='tests')

@mod.route('/', methods=('GET', 'POST', 'DELETE'))
def index():
    case = lambda x: request.method == x
    if case('GET'):
        return db['index']
    elif case('POST'):
        db['index'] = request.form['message']
    elif case('DELETE'):
        del db['index']
    return 'Success!'

@mod.route('/error')
def error():
    1/0
    return 'Oh noes!'


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.register_module(mod)
    return app


app = AppTests(create_app)

@app.test
@post('/', data={'message': 'Hello, World!'})
def post_to_index(response):
    Assert(response) == Response('Success!')
    Assert(db['index']) == 'Hello, World!'

@app.test
@get('/')
def get_index(response):
    Assert(response) == Response('Hello, World!')
    Assert(response) != Response('Hello, World!', status=404)

@app.test
@delete('/')
def delete_index(response):
    Assert(response) == Response('Success!')
    Assert('index').not_in(db)

@app.test
@get('/404')
def request_persists(response):
    Assert(request.path) == '/404'

@app.test
def test_request_context(client):
    Assert(request.path) == '/'
    client.get('/404')
    Assert(request.path) == '/404'

@app.test
def trigger_error(client):
    with Assert.raises(ZeroDivisionError):
        client.get('/error')
    client.application.debug = False
    response = client.get('/error')
    Assert(response.status_code) == 500
    client.application.debug = True


if __name__ == '__main__':
    app.main()
