from openenv.core import create_app  # updated import
from environment import SmartHomeEnergyEnv
from models import Action as EnergyAction, Observation as EnergyObservation


app = create_app(
    SmartHomeEnergyEnv,
    EnergyAction,
    EnergyObservation
)