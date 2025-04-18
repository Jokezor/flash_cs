# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    # List system dependencies needed for building or running Python packages
    buildInputs = [
    # Specify the Python interpreter version
    pkgs.python39

    # Add python packages that are hard for pip/uv to build,
    # or have complex system dependencies.
    # Nix will build/provide these.
    pkgs.python39Packages.onnxruntime

    # Add any other system libraries your project might need
    # e.g., pkgs.gcc, pkgs.cmake if something needs compiling
    ];

    # Optional: Set environment variables within the shell
    # shellHook = ''
    #   export MY_VAR="some_value"
    # '';
}