# NixOS module for Weather Shield
# Usage in configuration.nix:
#   imports = [ ./weather-shield/module.nix ];
#   services.weather-shield.enable = true;
#   services.weather-shield.config = {
#     api_key = "your-api-key";
#     latitude = 40.7128;
#     longitude = -74.0060;
#   };

{ config, pkgs, lib, ... }:

with lib;

let
  cfg = config.services.weather-shield;
  weather-shield = pkgs.callPackage ./default.nix { };
  configFile = pkgs.writeText "weather-shield-config.json" (builtins.toJSON cfg.config);
in
{
  options.services.weather-shield = {
    enable = mkEnableOption "Weather Shield service";

    config = mkOption {
      type = types.attrs;
      default = {
        api_key = "";
        latitude = 0.0;
        longitude = 0.0;
        units = "metric";
        check_interval = 300;
        forecast_minutes = 30;
        ntfy_topic = null;
        computers = [
          {
            id = "computer-1";
            name = "Main Computer";
            enabled = true;
          }
        ];
      };
      description = "Weather Shield configuration";
    };

    openFirewall = mkEnableOption "open port 5000 in firewall" // { default = false; };

    port = mkOption {
      type = types.port;
      default = 5000;
      description = "Port to run Weather Shield on";
    };

    user = mkOption {
      type = types.str;
      default = "weather-shield";
      description = "User to run Weather Shield as";
    };

    group = mkOption {
      type = types.str;
      default = "weather-shield";
      description = "Group to run Weather Shield as";
    };
  };

  config = mkIf cfg.enable {
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
      home = "/var/lib/weather-shield";
      createHome = true;
    };

    users.groups.${cfg.group} = { };

    systemd.services.weather-shield = {
      description = "Weather Shield - Real-time Weather Monitoring";
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];

      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = "/var/lib/weather-shield";
        ExecStart = "${weather-shield}/bin/weather-shield";
        Restart = "on-failure";
        RestartSec = 10;

        # Security hardening
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [ "/var/lib/weather-shield" ];
        StateDirectory = "weather-shield";
        StateDirectoryMode = "0750";
      };

      environment = {
        WEATHER_SHIELD_CONFIG = configFile;
      };
    };

    networking.firewall = mkIf cfg.openFirewall {
      allowedTCPPorts = [ cfg.port ];
    };
  };
}
