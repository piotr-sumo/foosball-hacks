from time import sleep
from random import randint, choice
from threading import Thread


# Device.pin_factory = MockFactory()


class GameEvent:
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


class GameGenerator:
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
        Thread(target=self.play, args=(self,), daemon=True)
