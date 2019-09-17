from time import sleep
from unittest.mock import Mock
from game_generator import GameGenerator
import gpiozero.pins.mock
from gpiozero import Button
import gpiozero
from state import State

if __name__ == "__main__":
    state = State()
    gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()
    red_button = Button(17)
    blue_button = Button(27)
    gg = GameGenerator(red_button, blue_button, 600, 600, 1000, 130, 200, 3, 3)
    gg.start()

    sleep(30)
    print("Game score", state.get_current_score())
    print("Simulation has ended")
