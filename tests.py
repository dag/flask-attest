from flask import Module, Flask
from flaskext.attest import AppTests, get
from attest import Assert

TESTING = True


db = {}
mod = Module(__name__, name='tests')

@mod.route('/')
def index():
    return db['index']


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.register_module(mod)
    return app


app = AppTests(create_app)

@app.context
def setup_db():
    db['index'] = 'Hello, World!'
    try:
        yield
    finally:
        del db['index']

@app.test
@get('/')
def index_data(response):
    Assert(response.data) == 'Hello, World!'


if __name__ == '__main__':
    app.main()
