from sensors import Sensors
from sensors_and_state import MasterStateListener, MAX_SCORE_GAME_MODE
from sounds import ScoresStateListener
from state import State, create_sumo_listener

if __name__ == "__main__":
    print("Starting foosball")
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
        print("Unable to create sumo listener")

    # let daemon threads keep the process alive
    print("Setup done")
