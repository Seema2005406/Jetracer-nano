import time
import threading
import pygame
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

# Joystick Reader Thread Class
class JoystickReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.steering = 0
        self.gas = 0
        self.brake = 0
        self.clutch = 0
        self.handbrake = 0
        self.reverse = 0
        self.enter = 0
        self.exit = 0
        self.currentTimestamp = 0
        self.isRunning = True
        self.precisionDecimals = 3
        self.sleepTime = 0

    def pedalValuesNormalize(self, val):
        return round((1 - val) / 2, self.precisionDecimals)

    def steeringValuesNormalize(self, val):
        return round(val * 10, self.precisionDecimals)
        
    def run(self):
        pygame.init()
        pygame.joystick.init()

        # Initialize joystick (assuming G29 is the first joystick connected)
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
	#time.sleep(0.5)
        while self.isRunning:
            self.currentTimestamp = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            _steering = joystick.get_axis(0)  # Axis 0 for steering wheel
            _brake = joystick.get_axis(3)     # Axis 1 for brake
            _clutch = joystick.get_axis(1)    # Axis 2 for clutch
            _gas = joystick.get_axis(2)       # Axis 5 for throttle/gas

            # Update joystick values
            #self.steering = _steering * -1
            self.steering = self.steeringValuesNormalize(_steering * -1)
            self.brake = self.pedalValuesNormalize(_brake)
            self.clutch = self.pedalValuesNormalize(_clutch)
            self.gas = self.pedalValuesNormalize(_gas)

            # Button values (adjust indices based on button configuration)
            self.handbrake = 1 if joystick.get_button(4) else 0
            self.reverse = 1 if joystick.get_button(5) else 0
            self.enter = 1 if joystick.get_button(6) else 0
            self.exit = 1 if joystick.get_button(7) else 0

            time.sleep(self.sleepTime)

    def stop(self):
        self.isRunning = False

# KUKSA Client Thread to send data
class ConnectToKuksa(threading.Thread):
    def __init__(self, joystick_reader):
        super().__init__()
        self.joystick_reader = joystick_reader
        self.isRunning = True

    def run(self):
        kuksaDataBroker_IP = '20.79.188.178'
        kuksaDataBroker_Port = 55555

        with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
            while self.isRunning and self.joystick_reader.isRunning:
                # Send joystick values to KUKSA Data Broker
                client.set_current_values({
                    'Vehicle.OBD.RelativeThrottlePosition': Datapoint(float(self.joystick_reader.gas)),
                    'Vehicle.Powertrain.Transmission.ClutchEngagement': Datapoint(float(self.joystick_reader.clutch)),
                    'Vehicle.ADAS.CruiseControl.SpeedSet': Datapoint(float(self.joystick_reader.brake)),
                    'Vehicle.Speed': Datapoint(float(self.joystick_reader.steering)),
                    'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear': Datapoint(bool(self.joystick_reader.handbrake)),
                    'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear': Datapoint(bool(self.joystick_reader.reverse)),
                    'Vehicle.ADAS.CruiseControl.IsActive': Datapoint(bool(self.joystick_reader.enter)),
                    'Vehicle.ADAS.CruiseControl.IsEnabled': Datapoint(bool(self.joystick_reader.exit)),
                })

                # Print sent values for debugging
                print(f"KUKSA Signal - Throttle: {self.joystick_reader.gas}, Clutch: {self.joystick_reader.clutch}, "
                      f"Brake: {self.joystick_reader.brake}, Steering: {self.joystick_reader.steering}, "
                      f"Handbrake: {self.joystick_reader.handbrake}, Reverse: {self.joystick_reader.reverse}, "
                      f"Enter: {self.joystick_reader.enter}, Exit: {self.joystick_reader.exit}")
                time.sleep(0.5)

    def stop(self):
        self.isRunning = False

# Main logic to run the threads
if __name__ == '__main__':
    joystick_reader = JoystickReader()
    kuksa_client = ConnectToKuksa(joystick_reader)

    joystick_reader.start()
    kuksa_client.start()

    try:
        while joystick_reader.isRunning:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught. Stopping threads...")
        joystick_reader.stop()
        joystick_reader.join()
        kuksa_client.stop()
        kuksa_client.join()
        print("Threads have been stopped.")

