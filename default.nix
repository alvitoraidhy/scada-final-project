{
  pkgs ? import <nixpkgs> {}
}:
pkgs.mkShell {
  name="dev-environment";
  buildInputs = [
    # Node.js
    pkgs.nodejs_22

    # Formatters
    pkgs.nodePackages.prettier
  ];
  shellHook =
  ''
    echo "Node.js 22";
    echo "Start developing...";
  '';
}
