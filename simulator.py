from time import sleep
from random import randint, choice
from threading import Thread
import gpiozero
import gpiozero.pins.mock
from sensors import Sensors, SensorListener
from sounds import ScoresStateListener

from game_generator import GameGenerator
from state import State


class PrintingListener(SensorListener):

    def enter_red_ball(self):
        print("enter_red_ball")

    def enter_blue_ball(self):
        print("enter_blue_ball")

    def exit_red_ball(self):
        print("exit_red_ball")

    def exit_blue_ball(self):
        print("exit_blue_ball")

    def still_red_ball(self):
        print("still_red_ball")

    def still_blue_ball(self):
        print("still_blue_ball")


class StateSimulatorListener(PrintingListener):
    def __init__(self, state):
        self.state = state

    def enter_red_ball(self):
        super().enter_red_ball()
        self.state.red_scores()

    def enter_blue_ball(self):
        super().enter_blue_ball()
        self.state.blue_scores()

if __name__ == "__main__":
    state = State()
    gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()
    s = Sensors()
    gg = GameGenerator(s.goal_box_red_button, s.goal_box_blue_button, 6000, 6000, 10000, 1300, 2000, 7, 7)
    listener = StateSimulatorListener(state)
    sounds_listener = ScoresStateListener(state)
    s.attach(listener)
    state.attach(sounds_listener)
    gg.start()

    sleep(12)
    print("Game score", state.get_current_score())
    print("Simulation has ended")
