from __future__ import with_statement
from flask import (Module, request, redirect, Flask, Response, jsonify,
                   render_template_string)
from flaskext.attest import test_context, get, post, put, delete
from flaskext.genshi import Genshi, generate_template
from attest import Tests, raises, assert_hook

DEBUG = True
TESTING = True


db = {}
mod = Module(__name__, name='tests')

@mod.route('/', methods=('GET', 'POST', 'PUT', 'DELETE'))
def index():
    case = lambda x: request.method == x
    if case('GET'):
        return db['index']
    elif case('POST') or case('PUT'):
        db['index'] = request.form['message']
    elif case('DELETE'):
        del db['index']
    return 'Success!'

@mod.route('/error')
def error():
    1/0
    return 'Oh noes!'

@mod.route('/elsewhere')
def elsewhere():
    return redirect('/otherplace')

@mod.route('/json')
def json():
    return jsonify(status='Success!')

@mod.route('/hello/<name>')
def hello(name):
    return render_template_string('Hello {{name.capitalize()}}!', name=name)


@test_context
def testapp():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.register_module(mod)
    Genshi(app)
    return app


app = Tests(contexts=[testapp])

@app.test
@post('/', data={'message': 'Hello, World!'})
def post_to_index(response, templates):
    assert (request.method) == 'POST'
    assert (response) == Response('Success!')
    assert (db['index']) == 'Hello, World!'

@app.test
@put('/', data={'message': 'Hello, World!'})
def put_to_index(response, templates):
    assert (request.method) == 'PUT'
    assert (response) == Response('Success!')
    assert (db['index']) == 'Hello, World!'

@app.test
@get('/')
def get_index(response, templates):
    assert (request.method) == 'GET'
    assert (response) == Response('Hello, World!')
    assert (response) != Response('Hello, World!', status=404)

@app.test
@delete('/')
def delete_index(response, templates):
    assert (request.method) == 'DELETE'
    assert (response) == Response('Success!')
    assert ('index') not in (db)

@app.test
@get('/404')
def request_persists(response, templates):
    assert (request.path) == '/404'

@app.test
def test_request_context(client, templates):
    assert (request.path) == '/'
    client.get('/404')
    assert (request.path) == '/404'

@app.test
def trigger_error(client, templates):
    with raises(ZeroDivisionError):
        client.get('/error')
    client.application.debug = False
    response = client.get('/error')
    assert (response.status_code) == 500
    client.application.debug = True

@app.test
@get('/elsewhere')
def redirection(response, templates):
    assert (response) == redirect('/otherplace')
    assert (response) != redirect('/wrongplace')

@app.test
@get('/json')
def json_response(response, templates):
    assert (response) == jsonify(status='Success!')

@app.test
@get('/hello/world')
def capture_templates(response, templates):
    assert (response) == Response('Hello World!')
    assert (len(templates)) == 1
    assert (templates[0][0]) is (None)
    assert (templates[0][1]['name']) == 'world'

@app.test
def genshi_templates(client, templates):
    generate_template(string='Hello ${name.capitalize}!', method='text',
                      context=dict(name='world'))
    assert (len(templates)) == 1
    assert (templates[0][0]) is (None)
    assert (templates[0][1]['name']) == 'world'


if __name__ == '__main__':
    app.main()
