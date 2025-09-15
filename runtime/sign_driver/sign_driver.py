from pymodbus.client import ModbusSerialClient

class SignDriver:
    SIGN_ANIMALS = 2
    SIGN_WILD_ANIMALS = 3
    SIGN_SPEED = 4
    SIGN_STOP = 5

    SPEED_30 = 30
    SPEED_50 = 50
    SPEED_70 = 70
    SPEED_90 = 90

    NUM_SIGNS = 2
    SIGN_IDX_WARNING = 0
    SIGN_IDX_SPEED = 1

    def __init__(self, port, modbus_id):
        self.client = ModbusSerialClient(port)
        self.ID = modbus_id
        self.client.connect()

        self.signs = []

        for i in range(self.NUM_SIGNS):
            self.signs.append({"on" : i, "type": i, "speed": i + self.NUM_SIGNS})

    def __is_valid_speed(self, speed):
        speeds = [self.SPEED_30, self.SPEED_50, self.SPEED_70, self.SPEED_90]

        if speed in speeds:
            return True
        return False

    def sign_warning_off(self):
        self.client.write_coil(self.signs[self.SIGN_IDX_WARNING]["on"], 0, device_id=self.ID)


    def sign_warning_animals(self):
        self.client.write_register(self.signs[self.SIGN_IDX_WARNING]["type"],
                                   self.SIGN_ANIMALS, device_id=self.ID)
        self.client.write_coil(self.signs[self.SIGN_IDX_WARNING]["on"], 1, device_id=self.ID)

    def sign_warning_wild_animals(self):
        self.client.write_register(self.signs[self.SIGN_IDX_WARNING]["type"],
                                   self.SIGN_WILD_ANIMALS, device_id=self.ID)
        self.client.write_coil(self.signs[self.SIGN_IDX_WARNING]["on"], 1, device_id=self.ID)

    def sign_speed_stop_off(self):
        self.client.write_coil(self.signs[self.SIGN_IDX_SPEED]["on"], 0, device_id=self.ID)

    def sign_speed(self, speed):
        if not self.__is_valid_speed(speed):
            return
        
        self.client.write_register(self.signs[self.SIGN_IDX_SPEED]["type"],
                                   self.SIGN_SPEED, device_id=self.ID)
        self.client.write_register(self.signs[self.SIGN_IDX_SPEED]["speed"],
                                   speed, device_id=self.ID)
        self.client.write_coil(self.signs[self.SIGN_IDX_SPEED]["on"], 1, device_id=self.ID)
        
    def sign_stop(self):
        self.client.write_register(self.signs[self.SIGN_IDX_SPEED]["type"],
                                   self.SIGN_STOP, device_id=self.ID)
        self.client.write_coil(self.signs[self.SIGN_IDX_SPEED]["on"], 1, device_id=self.ID)


if __name__ == "__main__":
    import time
    
    driver = SignDriver("COM9", 1)

    while True:
        driver.sign_warning_off()
        driver.sign_speed_stop_off()
        time.sleep(1)
        driver.sign_warning_animals()

        speeds = [driver.SPEED_30, driver.SPEED_50, driver.SPEED_70, driver.SPEED_90]
        for i in range(4):
            driver.sign_speed(speeds[i])
            time.sleep(1)
            
        driver.sign_warning_wild_animals()
        driver.sign_stop()
        time.sleep(1)