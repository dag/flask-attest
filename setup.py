from setuptools import setup

setup(
    name='Flask-Attest',
    version='0.1dev',
    description='Test Flask applications with Attest',
    long_description=open('README.rst').read(),
    url='https://github.com/dag/flask-attest',

    author='Dag Odenhall',
    author_email='dag.odenhall@gmail.com',
    license='Simplified BSD',

    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,

    install_requires=[
        'Flask>=0.6',
        'Attest>=0.5',
        'blinker>=1.1',
        'decorator',
    ],

    test_loader='attest:auto_reporter.test_loader',
    test_suite='tests.app',
    tests_require=['Flask-Genshi>=0.5.1'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Testing',
    ]
)
