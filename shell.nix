# Non-flake entry: `nix-shell` / `nix-shell --pure` (no flake.lock required).
# Flake users should prefer `nix develop` after `nix flake lock`.
let
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/50ab793786d9de88ee30ec4e4c24fb4236fc2674.tar.gz";
    sha256 = "2dad8b48aaa93d64db4302f89e5361417e4c8c6d9425814a4d5e87b857577af2";
  }) { };
in
pkgs.mkShell {
  packages = with pkgs; [
    python312
    python312Packages.jsonschema
    gnumake
    jq
  ];
  shellHook = ''
    export PYTHON="${pkgs.python312}/bin/python3"
  '';
}
