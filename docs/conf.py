import sys, os
sys.path.append(os.path.abspath('_themes'))

project = u'Flask-Attest'
copyright = u'2011, Dag Odenhall'
version = '0.1'
release = '0.1'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'http://flask.pocoo.org/docs/': None,
    'http://werkzeug.pocoo.org/docs/': None,
    'http://packages.python.org/Attest/': None,
}

master_doc = 'index'

html_theme_path = ['_themes']
html_theme = 'flask_small'
html_theme_options = {
    'github_fork': 'dag/flask-attest'
}
