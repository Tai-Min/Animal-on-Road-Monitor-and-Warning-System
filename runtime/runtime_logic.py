from threading import Lock
from sign_driver.sign_driver import SignDriver
import time
import config

class RuntimeLogic:
    ANIMAL_SIGN_NONE = 0
    ANIMAL_SIGN_FARM = 1
    ANIMAL_SIGN_WILD = 2

    ANIMAL_SIGN_TIMEOUT = 600
    SPEED_SIGN_TIMEOUT = 600

    def __init__(self):
        self.fog_lock = Lock()
        self.fog_current = "SMALL"

        self.animal_lock = Lock()
        self.animal_stamp = 0
        self.animal_current = self.ANIMAL_SIGN_NONE
        self.animal_applied = self.ANIMAL_SIGN_NONE

        self.animal_farm_stamp = 0
        self.animal_wild_stamp = 0
        self.new_animal_detection = False

        self.speed_applied = SignDriver.SPEED_30
        self.speed_stamp = 0

    def __lookup_speed(self, fog, sign):
        if fog == "SMALL" and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM):
            return SignDriver.SPEED_90
        elif fog == "MEDIUM" and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM):
            return SignDriver.SPEED_70
        elif (fog == "HIGH" and (sign == self.ANIMAL_SIGN_NONE or sign == self.ANIMAL_SIGN_FARM)) or \
             (fog == "SMALL" and sign == self.ANIMAL_SIGN_WILD):
            return SignDriver.SPEED_50
        elif (fog == "HIGH" or fog == "MEDIUM") and sign == self.ANIMAL_SIGN_WILD:
            return SignDriver.SPEED_30
        return SignDriver.SPEED_30 # Fallback just in case

    def __is_wild_animal(self, animal):
        if animal in config.WILD_ANIMALS:
            return True
        return False

    def __get_driver_sign(self):
        with self.animal_lock:
            if self.animal_applied == self.ANIMAL_SIGN_NONE:
                return None
            if self.animal_applied == self.ANIMAL_SIGN_FARM:
                return SignDriver.SIGN_WILD_ANIMALS
            if self.animal_applied == self.ANIMAL_SIGN_WILD:
                return SignDriver.SIGN_WILD_ANIMALS
        return SignDriver.SIGN_WILD_ANIMALS # Fallback just in case

    def __reset_animal_current(self):
        self.animal_current = self.ANIMAL_SIGN_NONE
        self.animal_farm_stamp = 0
        self.animal_wild_stamp = 0

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
                    self.__reset_animal_current()

            # Timeout occured, apply lower sign
            if self.animal_applied > self.ANIMAL_SIGN_NONE and (now - self.animal_stamp > self.ANIMAL_SIGN_TIMEOUT):
                print("Timeout, applying lower warning")
                # Apply normal animal warning if there was detection within some timeframe
                if self.animal_applied == self.ANIMAL_SIGN_WILD and (now - self.animal_farm_stamp < self.ANIMAL_SIGN_TIMEOUT):
                    print("Farm animal warning applied")
                    self.animal_applied = self.ANIMAL_SIGN_FARM
                    self.__reset_animal_current()
                else:
                    print("No animal warning present")
                    self.animal_applied = self.ANIMAL_SIGN_NONE
                    self.__reset_animal_current()

    def __process_speed_sign(self):
        now = int(time.time())
        with self.fog_lock and self.animal_lock:
            speed = self.__lookup_speed(self.fog_current, self.animal_current)

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

    def fog_visibility_consumer(self, fog_density):
        with self.fog_lock:
            self.fog_current = fog_density
            

    def animal_classifier_consumer(self, classification):
        if classification[1] < 0.85:
            return
        
        now = int(time.time())
        with self.animal_lock:
            self.new_animal_detection = True
            if classification[0] == "empty":
                # Prevent override if any animal was observed in given timeframe
                if (now - self.animal_wild_stamp) < self.ANIMAL_SIGN_TIMEOUT or \
                    (now - self.animal_farm_stamp) < self.ANIMAL_SIGN_TIMEOUT:
                    return
                self.animal_current = self.ANIMAL_SIGN_NONE
            elif self.__is_wild_animal(classification[0]):
                self.animal_wild_stamp = int(time.time())
                self.animal_current = self.ANIMAL_SIGN_WILD
            else:
                # Prevent override if wild animal was observed in given timeframe
                if (now - self.animal_wild_stamp) < self.ANIMAL_SIGN_TIMEOUT:
                    return
                self.animal_farm_stamp = int(time.time())
                self.animal_current = self.ANIMAL_SIGN_FARM

    def loop_iteration(self):
            self.__process_animal_sign()
            self.__process_speed_sign()

            return [self.speed_applied, self.__get_driver_sign()]