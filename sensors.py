from gpiozero import Button
from time import sleep
import time
import threading

PIN_RED_BUTTON = 17
PIN_BLUE_BUTTON = 27

EXIT_TIMEOUT = 0.5
ENTER_TIMEOUT = 5
STILL_TIMEOUT = 60

SLEEP_TIME = 1 / 500


class SensorListener:
    # Interface for listener
    def enter_red_ball(self):
        raise NotImplementedError

    def enter_blue_ball(self):
        raise NotImplementedError

    def exit_red_ball(self):
        raise NotImplementedError

    def exit_blue_ball(self):
        raise NotImplementedError

    def still_red_ball(self):
        raise NotImplementedError

    def still_blue_ball(self):
        raise NotImplementedError


class PrintingListener(SensorListener):

    def enter_red_ball(self):
        print("enter_red_ball", type(self))

    def enter_blue_ball(self):
        print("enter_blue_ball", type(self))

    def exit_red_ball(self):
        print("exit_red_ball", type(self))

    def exit_blue_ball(self):
        print("exit_blue_ball", type(self))

    def still_red_ball(self):
        print("still_red_ball", type(self))

    def still_blue_ball(self):
        print("still_blue_ball", type(self))


class Sensors:
    def __init__(self):
        self.goal_box_red_button = Button(PIN_RED_BUTTON)
        self.goal_box_blue_button = Button(PIN_BLUE_BUTTON)

        self.present_ball_red = False
        self.present_ball_blue = False

        self.last_time_red = time.time()
        self.last_time_blue = time.time()

        self.listeners = set()

        self.poll_loop_thread = threading.Thread(target=self.poll_loop)
        self.poll_loop_thread.start()

    def attach(self, listener):
        self.listeners.add(listener)

    def detach(self, listener):
        self.listeners.discard(listener)

    def poll_loop(self):
        while True:
            if (self.present_ball_red and
                    self.goal_box_red_button.value == 0 and
                    self.since_last_time_red() > EXIT_TIMEOUT):
                self.present_ball_red = False
                self.last_time_red = time.time()
                self.exit_red_ball()

            elif (not self.present_ball_red and
                  self.goal_box_red_button.value == 1 and
                  self.since_last_time_red() > ENTER_TIMEOUT):
                self.present_ball_red = True
                self.last_time_red = time.time()
                self.enter_red_ball()

            elif (self.present_ball_red and
                  self.goal_box_red_button.value == 1 and
                  self.since_last_time_red() > STILL_TIMEOUT):
                self.last_time_red = time.time()
                self.still_red_ball()

            if (self.present_ball_blue and
                    self.goal_box_blue_button.value == 0 and
                    self.since_last_time_blue() > EXIT_TIMEOUT):
                self.present_ball_blue = False
                self.last_time_blue = time.time()
                self.exit_blue_ball()

            elif (not self.present_ball_blue and
                  self.goal_box_blue_button.value == 1 and
                  self.since_last_time_blue() > ENTER_TIMEOUT):
                self.present_ball_blue = True
                self.last_time_blue = time.time()
                self.enter_blue_ball()

            elif (self.present_ball_blue and
                  self.goal_box_blue_button.value == 1 and
                  self.since_last_time_blue() > STILL_TIMEOUT):
                self.last_time_blue = time.time()
                self.still_blue_ball()

            sleep(SLEEP_TIME)

    def since_last_time_red(self):
        return time.time() - self.last_time_red

    def since_last_time_blue(self):
        return time.time() - self.last_time_blue

    def enter_red_ball(self):
        for listener in self.listeners:
            listener.enter_red_ball()

    def enter_blue_ball(self):
        for listener in self.listeners:
            listener.enter_blue_ball()

    def still_blue_ball(self):
        for listener in self.listeners:
            listener.still_blue_ball()

    def exit_red_ball(self):
        for listener in self.listeners:
            listener.exit_red_ball()

    def exit_blue_ball(self):
        for listener in self.listeners:
            listener.exit_blue_ball()

    def still_red_ball(self):
        for listener in self.listeners:
            listener.still_blue_ball()
