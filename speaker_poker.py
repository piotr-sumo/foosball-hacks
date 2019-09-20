import os
from threading import Thread
from time import sleep
import argparse
import signal


SHOULD_RUN = True


def signal_handler(signum, frame):
    print("Handler fired, please wait till the player thread wakes up")
    if signum == signal.SIGINT:
        global SHOULD_RUN
        SHOULD_RUN = False


def play_file(filename):
    os.system(f"omxplayer -o local {filename} >/dev/null &")


def player(filename, interval):
    while SHOULD_RUN:
        print("Playing and then sleeping")
        play_file(filename)
        sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play some music so that the speaker will not turn off')
    parser.add_argument('music_file', help='music file to be played')
    parser.add_argument('interval', type=int, help='the interval IN MINUTES between playing the music file')

    args = parser.parse_args()
    print("Args", args.music_file, args.interval)
    print("Interrupt the program in order to quit")
    interval_seconds = args.interval * 60
    player_thread = Thread(target=player, args=(args.music_file, interval_seconds))
    player_thread.start()
    signal.signal(signal.SIGINT, signal_handler)
    player_thread.join()
