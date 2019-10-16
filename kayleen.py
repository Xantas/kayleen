import concurrent.futures
import enum
import queue
import threading
import time
import logging
from skills.skills_processor import SkillsProcessor


class KayleenStatus(enum.Enum):
    sleeping = 0
    working = 1
    initialising = 2
    killed = 3


class Kayleen:

    def __init__(self) -> None:
        self.status = KayleenStatus.sleeping
        self.skills = SkillsProcessor()

    def is_sleeping(self):
        return self.status is KayleenStatus.sleeping

    def want_to_kill(self):
        return self.status is KayleenStatus.killed

    def shut_down(self):
        logging.info("Znikam, pa ...")
        self.status = KayleenStatus.killed

    def wake_up(self):
        logging.info("Rozpoczynam wybudzanie Kaylen")
        self.status = KayleenStatus.initialising
        self.skills.start_up()
        self.status = KayleenStatus.working
        logging.info("Kaylen wybudzona")

    def go_to_sleep(self):
        logging.info("Rozpoczynam usypianie Kaylen")
        self.status = KayleenStatus.sleeping
        self.skills.shut_down()

    def test(self):
        try:
            self.pixels.wakeup()
            time.sleep(1)
            # pixels.think()
            # time.sleep(3)
            # pixels.speak()
            # time.sleep(3)
            # pixels.off()
            # time.sleep(3)
        except KeyboardInterrupt:
            self.goSleep()

        self.sayHello()
        self.goSleep()

    def say(self):
        print("Kaylen mowi czesc")
        # self.text2speech_processor.synthesize_text("Cześć, jestem Kayleen")

    def listenToMyVoice(self):
        print("Kaylen słucha itlumaczy na tekst")

    def heart_beat(self):
        pass


def main():
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    kayleen = Kayleen()
    kayleen.wake_up()

    while True:
        try:
            if not kayleen.want_to_kill():
                kayleen.heart_beat()
            else:
                kayleen.shut_down()
                break
        except KeyboardInterrupt:
            kayleen.shut_down()
            break




if __name__ == '__main__':
    main()
