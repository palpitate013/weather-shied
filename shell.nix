{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "weather-shield-env";
  
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    git
    curl
    wget
    vim
    nano
  ];
  
  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
      python -m venv .venv
    fi
    source .venv/bin/activate
    
    # Install Python packages
    pip install -q flask flask-cors requests python-dotenv 2>/dev/null || true
    
    echo "🌦️  Weather Shield - Nix Shell Environment"
    echo "==========================================="
    echo ""
    echo "Environment loaded with:"
    echo "  • Python $(python --version 2>&1)"
    echo "  • Virtual environment: .venv"
    echo "  • Flask & Flask-CORS"
    echo "  • Requests"
    echo "  • Python-dotenv"
    echo ""
    echo "Quick start commands:"
    echo "  • python weather_monitor.py    (start monitor)"
    echo "  • python app.py                 (start dashboard)"
    echo "  • python test_config.py         (validate config)"
    echo ""
    echo "Access dashboard at: http://localhost:5000"
    echo ""
  '';
}
