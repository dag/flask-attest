from setuptools import setup

setup(
    name='Flask-Attest',
    version='0.1',

    packages=['flaskext'],
    namespace_packages=['flaskext'],

    install_requires=[
        'Flask>=0.6',
        'Attest>=0.5',
        'blinker>=1.1',
        'decorator',
    ],

    zip_safe=False,
)
