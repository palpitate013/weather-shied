{ lib
, python3
, fetchFromGitHub
, flask
, flask-cors
, requests
}:

python3.pkgs.buildPythonApplication {
  pname = "weather-shield";
  version = "1.0.0";
  
  src = ../.;
  
  propagatedBuildInputs = [
    flask
    flask-cors
    requests
  ];

  postInstall = ''
    mkdir -p $out/etc/weather-shield
    cp config.json $out/etc/weather-shield/config.json.example
    mkdir -p $out/share/weather-shield
    cp -r templates static $out/share/weather-shield/
  '';

  meta = with lib; {
    description = "Real-time weather monitoring and computer control system";
    longDescription = ''
      Weather Shield monitors weather conditions and automatically 
      controls computer power states based on weather patterns.
      
      Features:
      - Real-time weather monitoring via OpenWeather API
      - Web-based dashboard for system status and control
      - Multi-computer support with individual tracking
      - Automatic shutdown on bad weather
      - Automatic boot when weather improves
      - Manual power control independent of weather
      - ntfy.sh notifications for alerts and status changes
      - REST API for programmatic access
    '';
    homepage = "https://github.com/palpitate013/weather-shield";
    license = licenses.mit;
    maintainers = [ ];
    platforms = platforms.unix;
    mainProgram = "weather-shield";
  };
}
