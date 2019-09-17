from time import sleep
from random import randint, choice
from threading import Thread
import gpiozero
import gpiozero.pins.mock
from sensors import Sensors

from game_generator import GameGenerator


class MyExampleListener:

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


if __name__ == "__main__":
    gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()
    s = Sensors()
    gg = GameGenerator(s.goal_box_red_button, s.goal_box_blue_button, 6000, 6000, 10000, 1300, 2000, 3, 3)
    listener = MyExampleListener()
    s.attach(listener)
    gg.start()

    sleep(1000000)

