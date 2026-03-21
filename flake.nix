{
  description = "Weather Shield - Real-time Weather Monitoring and Computer Control";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in {
        packages.weather-shield = pkgs.python312Packages.buildPythonApplication {
          pname = "weather-shield";
          version = "1.0.0";
          src = ./.;
          
          propagatedBuildInputs = with pkgs.python312Packages; [
            flask
            flask-cors
            requests
            gunicorn
          ];

          postInstall = ''
            mkdir -p $out/etc/weather-shield
            cp config.json $out/etc/weather-shield/config.json.example
            mkdir -p $out/share/weather-shield
            cp -r templates static $out/share/weather-shield/
          '';

          meta = with pkgs.lib; {
            description = "Real-time weather monitoring and computer control system";
            longDescription = ''
              Weather Shield monitors weather conditions and automatically 
              controls computer power states based on weather patterns.
              Features include real-time monitoring, web-based dashboard,
              multi-computer support, and ntfy.sh notifications.
            '';
            homepage = "https://github.com/palpitate013/weather-shield";
            license = licenses.mit;
            maintainers = [ ];
            platforms = platforms.unix;
          };
        };

        packages.default = self.packages.${system}.weather-shield;

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            python312Packages.pip
            python312Packages.venv
            python312Packages.flask
            python312Packages.flask-cors
            python312Packages.requests
          ];
        };
      }
    );
}
