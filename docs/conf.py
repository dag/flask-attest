import sys, os
sys.path.append(os.path.abspath('_themes'))

project = u'Flask-Attest'
copyright = u'2011, Dag Odenhall'
version = '0.1'
release = '0.1'

extensions = ['sphinx.ext.autodoc']

master_doc = 'index'

html_theme_path = ['_themes']
html_theme = 'flask_small'
html_theme_options = {
    'github_fork': 'dag/flask-attest'
}
