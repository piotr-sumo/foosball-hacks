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

    def still_blue_ball(self):
        for listener in self.listeners:
            listener.still_blue_ball()








# Temporary testing stuff:

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

from time import sleep
from random import randint, choice
from threading import Thread
import gpiozero
import gpiozero.pins.mock

#gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()

class GameEvent():
    def __init__(self, description):
        self.description = description

    def fire(self):
        print(self.description)

class BallPickupEvent(GameEvent):
    def __init__(self, button):
        super().__init__(f'Ball picked up from {button.pin}')
        self.button = button

    def fire(self):
        self.button.pin.drive_high()
        super().fire()

class BallDropEvent(GameEvent):
    def __init__(self, button):
        super().__init__(f'Ball dropped in {button.pin}')
        self.button = button

    def fire(self):
        self.button.pin.drive_low()
        super().fire()

class WaitEvent(GameEvent):
    def __init__(self, sleep_ms):
        super().__init__(f'Waiting for the next event for {sleep_ms}')
        self.sleep_ms = sleep_ms

    def fire(self):
        super().fire()
        sleep(self.sleep_ms / 1000)


class GameGenerator():
    # crate buttons with pin_factory=gpiozer.pins.mock.MockFactory()
    def __init__(self,
        red_button,
        blue_button,
        start_wait_ms,
        goal_interval_min_ms,
        goal_interval_max_ms,
        pickup_interval_min_ms,
        pickup_interval_max_ms,
        red_score,
        blue_score):

        self.red_button = red_button
        self.blue_button = blue_button

        self.start_button = choice([red_button, blue_button])
        self.game_log = [
            WaitEvent(start_wait_ms),
            BallPickupEvent(self.start_button)
        ]

        while red_score > 0 or blue_score > 0:
            goal_interval_ms = randint(goal_interval_min_ms, goal_interval_max_ms)
            pickup_interval_ms = randint(pickup_interval_min_ms, pickup_interval_max_ms)
            next_button = None
            should_pickup = True
            if red_score > 0 and blue_score > 0:
                next_button = choice([red_button, blue_button])
                if next_button is red_button:
                    blue_score -= 1
                else:
                    red_score -= 1
            elif red_score > 0:
                next_button = blue_button
                red_score -= 1
                should_pickup = red_score != 0
            else:
                next_button = red_button
                blue_score -= 1
                should_pickup = blue_score != 0
            self.game_log += [
                WaitEvent(goal_interval_ms),
                BallDropEvent(next_button),
                WaitEvent(pickup_interval_ms)
            ]
            if should_pickup:
                self.game_log += [BallPickupEvent(next_button)]

    def play(self):
        self.blue_button.pin.drive_high()
        self.red_button.pin.drive_high()

        self.start_button.pin.drive_low()
        for game_event in self.game_log:
            game_event.fire()

    def start(self):
        Thread(target=self.play, daemon=True).start()



if __name__ == "__main__":
    s = Sensors()
    #gg = GameGenerator(s.goal_box_red_button, s.goal_box_blue_button, 6000, 6000, 10000, 1300, 2000, 3, 3)
    l = MyExampleListener()
    s.attach(l)
    #gg.start()

    sleep(10000)


