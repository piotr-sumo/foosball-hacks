import sched
from time import sleep
from threading import Thread


def printer():
    print("I was called")


def thread_main():
    s = sched.scheduler()
    s.enter(2, 1, printer)
    s.run()


if __name__ == "__main__":
    t = Thread(target=thread_main, daemon=True)
    t.start()
    sleep(6)
    print("Done")
