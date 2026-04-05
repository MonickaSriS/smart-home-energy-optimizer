from openenv_core import create_app
from environment import SmartHomeEnergyEnv


def main():
    app = create_app(SmartHomeEnergyEnv)
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()