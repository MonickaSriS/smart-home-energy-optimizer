from openenv.core import create_app  # updated import
from environment import SmartHomeEnergyEnv
from models import Action as EnergyAction, Observation as EnergyObservation
from dotenv import load_dotenv
load_dotenv()

app = create_app(
    SmartHomeEnergyEnv,
    EnergyAction,
    EnergyObservation
)