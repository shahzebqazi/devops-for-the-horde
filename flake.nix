{
  description = "devops-for-the-horde — Mac bootstrap hub + Mac→NixOS inventory + satellite install orchestration";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs =
    { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];
      forEachSystem = f: lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
    in
    {
      devShells = forEachSystem (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python312
            python312Packages.jsonschema
            gnumake
            jq
          ];
          shellHook = ''
            export PYTHON="${pkgs.python312}/bin/python3"
          '';
        };
      });

      packages = forEachSystem (pkgs: {
        default = pkgs.writeShellApplication {
          name = "horde-install-all";
          runtimeInputs = with pkgs; [
            bash
            coreutils
            git
            jq
          ];
          text = ''
            export DEVOPS_HORDE_ROOT="${self}"
            exec ${pkgs.bash}/bin/bash ${self}/nix/install-all.sh "$@"
          '';
        };
      });

      apps = forEachSystem (pkgs: {
        default = {
          type = "app";
          program = "${self.packages.${pkgs.stdenv.hostPlatform.system}.default}/bin/horde-install-all";
        };
      });
    };
}
