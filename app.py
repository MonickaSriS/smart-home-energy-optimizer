from openenv_core import create_app
from environment import SmartHomeEnergyEnv
from models import Action as EnergyAction, Observation as EnergyObservation
import uvicorn


def main():
    app = create_app(
        SmartHomeEnergyEnv,
        EnergyAction,
        EnergyObservation
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()