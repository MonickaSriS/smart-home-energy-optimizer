from openenv_core import create_app
from environment import SmartHomeEnergyEnv, EnergyAction, EnergyObservation


def main():
    app = create_app(
        SmartHomeEnergyEnv,
        EnergyAction,
        EnergyObservation
    )
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()