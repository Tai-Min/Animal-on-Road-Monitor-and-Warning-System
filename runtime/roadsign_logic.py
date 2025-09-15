from threading import Lock
from sign_driver.sign_driver import SignDriver
import time

class SignLogicDriver:
    FOG_SMALL = 0
    FOG_MEDIUM = 1
    FOG_HIGH = 2

    ANIMAL_SIGN_NONE = 0
    ANIMAL_SIGN_FARM = 1
    ANIMAL_SIGN_WILD = 2

    ANIMAL_SIGN_TIMEOUT = 600
    SPEED_SIGN_TIMEOUT = 600

    def __init__(self):
        self.fog_lock = Lock()
        #self.fog_stamp = 0
        self.fog_current = self.FOG_SMALL
        #self.fog_applied = self.FOG_SMALL

        self.animal_lock = Lock()
        self.animal_stamp = 0
        self.animal_current = self.ANIMAL_SIGN_NONE
        self.animal_applied = self.ANIMAL_SIGN_NONE

        self.animal_farm_stamp = 0
        self.animal_wild_stamp = 0
        self.new_animal_detection = False

        self.speed_applied = SignDriver.SPEED_30
        self.speed_stamp = 0

    def __get_speed(self, fog, sign):
        if fog == self.FOG_SMALL and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM):
            return SignDriver.SPEED_90
        elif fog == self.FOG_MEDIUM and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM):
            return SignDriver.SPEED_70
        elif (fog == self.FOG_HIGH and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM)) or \
             (fog == self.FOG_SMALL and sign == self.ANIMAL_SIGN_WILD):
            return SignDriver.SPEED_50
        elif (fog == self.FOG_HIGH or fog == self.FOG_MEDIUM) and sign == self.ANIMAL_SIGN_WILD:
            return SignDriver.SPEED_30

    def __is_wild_animal(self, animal):
        if animal in ['boar', 'deer', 'dog', 'horse', 'wolf']:
            return True
        return False

    def __process_animal_sign(self):
        now = int(time.time())

        with self.animal_lock:
            if self.new_animal_detection:
                self.new_animal_detection = False

                # Refresh timeout as new same detection occured
                if self.animal_current == self.animal_applied:
                    print("Same animal warning applied, refreshing timeout")
                    self.animal_stamp = int(time.time())

                # Instantly apply more important animal sign
                elif self.animal_current > self.animal_applied:
                    print("Bigger animal warning occured, applying instantly")
                    self.animal_stamp = int(time.time())
                    self.animal_applied = self.animal_current

            # Timeout occured, apply lower sign
            if self.animal_applied > self.ANIMAL_SIGN_NONE and (now - self.animal_stamp > self.ANIMAL_SIGN_TIMEOUT):
                print("Timeout, applying lower warning")
                # Apply normal animal warning if there was detection within some timeframe
                if self.animal_applied == self.ANIMAL_SIGN_WILD and (now - self.animal_farm_stamp < self.ANIMAL_SIGN_TIMEOUT):
                    print("Farm animal warning applied")
                    self.animal_applied = self.ANIMAL_SIGN_FARM
                else:
                    print("No animal warning present")
                    self.animal_applied = self.ANIMAL_SIGN_NONE

    def __process_speed_sign(self):
        now = int(time.time())
        with self.fog_lock and self.animal_lock:
            speed = self.__get_speed(self.fog_current, self.animal_current)

            # Refresh timeout as new same detection occured
            if speed == self.speed_applied:
                print("Same speed computed, refreshing timeout")
                self.speed_stamp = int(time.time())

            # Instantly apply slower speed limit
            elif speed < self.speed_applied:
                print("Lower speed computed, applying instantly")
                self.speed_stamp = int(time.time())
                self.speed_applied = speed

            # Timeout occured, apply lower sign
            if now - self.speed_stamp > self.SPEED_SIGN_TIMEOUT:
                print(f"Timeout, applying speed: {speed}")
                self.speed_applied = speed

    def __get_driver_sign(self):
        if self.animal_applied == self.ANIMAL_SIGN_NONE:
            return None
        if self.animal_applied == self.ANIMAL_SIGN_FARM:
            return SignDriver.SIGN_WILD_ANIMALS
        if self.animal_applied == self.ANIMAL_SIGN_WILD:
            return SignDriver.SIGN_WILD_ANIMALS

    def air_visibility_consumer(self, air_visibility):
        with self.fog_lock:
            if air_visibility == "HIGH":
                self.fog_current = self.FOG_HIGH
            elif air_visibility == "MEDIUM":
                self.fog_current = self.FOG_MEDIUM
            elif air_visibility == "SMALL":
                self.fog_current = self.FOG_SMALL

    def animal_classifier_consumer(self, classification):
        if classification[1] < 0.85:
            return
        
        with self.animal_lock:
            self.new_animal_detection = True
            if classification[0] == "empty":
                self.animal_current = self.ANIMAL_SIGN_NONE
            elif self.__is_wild_animal(classification[0]):
                self.animal_wild_stamp = int(time.time())
                self.animal_current = self.ANIMAL_SIGN_WILD
            else:
                self.animal_farm_stamp = int(time.time())
                self.animal_current = self.ANIMAL_SIGN_FARM

    def loop_iteration(self):
            self.__process_animal_sign()
            self.__process_speed_sign()

            return [self.speed_applied, self.__get_driver_sign()]