try:
    import RPi.GPIO as GPIO
except ImportError:
    from device import devicemock as GPIO

import kayleen

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

if __name__ == "__main__":
    kayleen.main()

# while True:
#     state = GPIO.input(BUTTON)
#     if state:
#         print("off")
#     else:
#         kayleen.wakeUp()
#         break
#     time.sleep(1)
