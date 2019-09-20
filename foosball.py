from sensors import Sensors
from sensors_and_state import MasterStateListener, MAX_SCORE_GAME_MODE
from sounds import ScoresStateListener
from state import State, create_sumo_listener
import logging

logging.basicConfig(format='%(asctime)s %(name)s %(message)s', level=logging.INFO)
logger = logging.getLogger("foosball")

if __name__ == "__main__":
    logger.info("Starting foosball")
    state = State()
    sensors = Sensors()

    game_manager = MasterStateListener(state, MAX_SCORE_GAME_MODE)
    sounds_listener = ScoresStateListener(state)
    sensors.attach(game_manager)
    state.attach(sounds_listener)
    sumo_listener = create_sumo_listener()
    if sumo_listener is not None:
        state.attach(sumo_listener)
    else:
        logger.info("Unable to create sumo listener")

    # let daemon threads keep the process alive
    logger.info("Setup done")
