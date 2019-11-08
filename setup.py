from setuptools import setup, find_packages

setup(
    name='sphinxcontrib-robotdoc',
    version='0.11.0',
    description=('Sphinx extension to embed Robot Framework test cases '
                 'and user keywords into Sphinx documents'),
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/datakurre/sphinxcontrib-robotdoc/',
    license='GPL',
    py_modules=['sphinxcontrib_robotdoc'],
    install_requires=[
        'setuptools',
        'sphinx',
        'pygments>=1.6rc1',
        'robotframework>=2.7.1'
    ]
)
