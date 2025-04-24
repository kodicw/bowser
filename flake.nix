{
  description = "bowser python lib";

  # Nixpkgs / NixOS version to use.
  inputs.nixpkgs.url = "nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs }:
    let

      # to work with older version of flakes
      # lastModifiedDate = self.lastModifiedDate or self.lastModified or "19700101";

      # Generate a user-friendly version number.
      # version = builtins.substring 0 8 lastModifiedDate;

      # System types to support.
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];

      # Helper function to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'.
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Nixpkgs instantiated for supported system types.
      nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });

    in
    {

      packages = forAllSystems
        (system:
          let
            pkgs = nixpkgsFor.${system};
          in
          with pkgs.python3Packages;
          {
            bowser = buildPythonPackage
              rec {
                name = "pfbrowser";
                # src = ./.;
                src = fetchGithub {
                  owner = "kodicw";
                  repo = "bowser";
                  rev = "aea5bbdc48137717c8658889b6bfe5ad986b5e39";
                };
                propagatedBuildInputs = [ selenium ];
              };
          });
      defaultPackage = forAllSystems (system: self.packages.${system}.bowser);
    };
}
