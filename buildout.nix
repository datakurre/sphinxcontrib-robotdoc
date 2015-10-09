with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "buildout";
  buildInputs = [
    (pythonPackages.zc_buildout_nix.overrideDerivation (args: { postInstall = ""; }))
  ];
  shellHook = ''
    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
  '';
}
