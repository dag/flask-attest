from setuptools import setup

setup(
    name='Flask-Attest',
    version='0.1',

    packages=['flaskext'],
    namespace_packages=['flaskext'],

    install_requires=[
        'Flask>=0.6',
        'Attest>=0.4',
        'blinker>=1.1',
        #'lxml>=2.0',
    ],

    zip_safe=False,
)
