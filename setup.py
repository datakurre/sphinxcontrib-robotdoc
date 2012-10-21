from setuptools import setup, find_packages

setup(
    name="sphinxcontrib-robotdoc",
    version="0.3.4",
    description=("Sphinx extension to embed Robot Framework test cases "
                 "and and user keywords into Sphinx documents"),
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.txt").read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords="",
    author="Asko Soukka",
    author_email="asko.soukka@iki.fi",
    url="https://github.com/datakurre/sphinxcontrib-robotdoc/",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "robotframework>=2.7.1"
    ]
)
