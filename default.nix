with import <nixpkgs> {};
let dependencies = rec {
  _Pygments = buildPythonPackage {
    name = "Pygments-2.0.2";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pygments/Pygments-2.0.2.tar.gz";
      md5 = "238587a1370d62405edabd0794b3ec4a";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _robotframework = buildPythonPackage {
    name = "robotframework-2.9.2";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/r/robotframework/robotframework-2.9.2.tar.gz";
      md5 = "5b7ed3cd22130044fe80f3165f5e0f52";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _Sphinx = buildPythonPackage {
    name = "Sphinx-1.3.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/S/Sphinx/Sphinx-1.3.1.tar.gz";
      md5 = "8786a194acf9673464c5455b11fd4332";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      _six
      _Jinja2
      _Pygments
      _docutils
      _snowballstemmer
      _Babel
      _alabaster
      _sphinx_rtd_theme
      _robotframework
    ];
    doCheck = false;
  };
  _setuptools = buildPythonPackage {
    name = "setuptools-18.3.2";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/setuptools/setuptools-18.3.2.zip";
      md5 = "d19f07502eae269853d0b3ec88aa26cd";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _sphinx_rtd_theme = buildPythonPackage {
    name = "sphinx-rtd-theme-0.1.9";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/sphinx_rtd_theme/sphinx_rtd_theme-0.1.9.tar.gz";
      md5 = "86a25c8d47147c872e42dc84cc66f97b";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _alabaster = buildPythonPackage {
    name = "alabaster-0.7.6";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/alabaster/alabaster-0.7.6.tar.gz";
      md5 = "169cdce2a96b75bff8cb8a59d938673f";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _Babel = buildPythonPackage {
    name = "Babel-2.1.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/B/Babel/Babel-2.1.1.tar.gz";
      md5 = "cab63d158ceed3a809703711cfb8cbd5";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      _pytz
    ];
    doCheck = false;
  };
  _snowballstemmer = buildPythonPackage {
    name = "snowballstemmer-1.2.0";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/snowballstemmer/snowballstemmer-1.2.0.tar.gz";
      md5 = "51f2ef829db8129dd0f2354f0b209970";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _docutils = buildPythonPackage {
    name = "docutils-0.12";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/docutils/docutils-0.12.tar.gz";
      md5 = "4622263b62c5c771c03502afa3157768";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _Jinja2 = buildPythonPackage {
    name = "Jinja2-2.8";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/J/Jinja2/Jinja2-2.8.tar.gz";
      md5 = "edb51693fe22c53cee5403775c71a99e";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      _MarkupSafe
    ];
    doCheck = false;
  };
  _six = buildPythonPackage {
    name = "six-1.10.0";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz";
      md5 = "34eed507548117b2ab523ab14b2f8b55";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _pytz = buildPythonPackage {
    name = "pytz-2015.6";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytz/pytz-2015.6.zip";
      md5 = "5c49910a1836ff3682e2058e11da1a50";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
  _MarkupSafe = buildPythonPackage {
    name = "MarkupSafe-0.23";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/MarkupSafe/MarkupSafe-0.23.tar.gz";
      md5 = "f5ab3deee4c37cd6a922fb81e730da6e";
    };
    buildInputs = [
      
    ];
    propagatedBuildInputs = [
      
    ];
    doCheck = false;
  };
};
in with dependencies; stdenv.mkDerivation {
  name = "default";
  src = ./.;
  buildInputs = [
    _Pygments
    _Sphinx
    _robotframework
    _setuptools
  ];
  buildout = "${(pythonPackages.zc_buildout_nix.overrideDerivation (args: {
    propagatedBuildInputs = [
      _Pygments
        _Sphinx
        _robotframework
        _setuptools
    ];
  }))}/bin/buildout-nix";
  shellHook = ''
    export PYTHONPATH=`pwd`
    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
  '';
}
