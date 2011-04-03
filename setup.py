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

    test_loader='attest:auto_reporter.test_loader',
    test_suite='tests.app',
    tests_require=[
        'Attest>=0.5',
        'Flask-Genshi>=0.5.1'
    ],

    zip_safe=False,
)
