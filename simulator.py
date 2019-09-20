import logging

import gpiozero.pins.mock

from game_generator import GameGenerator
from sensors import Sensors
from sensors_and_state import MasterStateListener, MAX_SCORE_GAME_MODE
from sounds import ScoresStateListener
from state import State

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    state = State()
    gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()
    sensors = Sensors()
    gg = GameGenerator(sensors.goal_box_red_button, sensors.goal_box_blue_button, 6000, 6000, 10000, 1300, 2000, 2, 2)
    state_listener = MasterStateListener(state, MAX_SCORE_GAME_MODE)
    sounds_listener = ScoresStateListener(state)
    sensors.attach(state_listener)
    state.attach(sounds_listener)
    game = gg.start()
    game.join()

    logging.info("Game score %s", state.get_current_score())
    logging.info("Simulation has ended")
