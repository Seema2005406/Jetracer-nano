import logging
import time
import pygame
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

# Setup logging
logging.basicConfig(level=logging.INFO)

print("\r++++++++++++++++++++++++++++++++++++\r")
print("Welcome to the PS4 Controller Interface\r")
print("+++++++++++++++++++++++++++++++++++++\r")

# Initialize Pygame for joystick handling
pygame.init()
pygame.joystick.init()

# Check for connected joysticks
num_joysticks = pygame.joystick.get_count()
if num_joysticks == 0:
    print("No joystick connected!")
    pygame.quit()
    exit()

# Initialize the first joystick (assumed to be the PS4 controller)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick initialized: {joystick.get_name()}")

# Control mappings for PS4 controller (adjust based on your configuration)
controls = {
    'steering_wheel': 1,  # Left stick X-axis
    'clutch': 2,          # L2 (Example mapping)
    'throttle': 5,        # R2 (Example mapping)
    'brake': 4,           # Right stick Y-axis
    'handbrake': 3,       # L1 Button
    'reverse': 2,         # Circle Button
    'enter': 1,           # Cross Button
    'exit': 0             # Triangle Button
}

# Global variables for PS4 controller values
digitalAuto_Steering = 0.0
digitalAuto_Clutch = 0.0
digitalAuto_Throttle = 0.0
digitalAuto_Brake = 0.0

# Global variables for button states
digitalAuto_Handbrake = 0
digitalAuto_Reverse = 0
digitalAuto_Enter = 0
digitalAuto_Exit = 0

def read_wheel_values():
    """Read values from the PS4 controller and update global variables."""
    pygame.event.pump()  # Update joystick state
    
    global digitalAuto_Steering, digitalAuto_Clutch, digitalAuto_Throttle, digitalAuto_Brake
    digitalAuto_Steering = joystick.get_axis(controls['steering_wheel'])  # Raw value
    digitalAuto_Clutch = joystick.get_axis(controls['clutch'])  # Raw value
    digitalAuto_Throttle = joystick.get_axis(controls['throttle'])  # Raw value
    digitalAuto_Brake = joystick.get_axis(controls['brake'])  # Raw value

    global digitalAuto_Handbrake, digitalAuto_Reverse, digitalAuto_Enter, digitalAuto_Exit
    digitalAuto_Handbrake = 1 if joystick.get_button(controls['handbrake']) else 0
    digitalAuto_Reverse = 1 if joystick.get_button(controls['reverse']) else 0
    digitalAuto_Enter = 1 if joystick.get_button(controls['enter']) else 0
    digitalAuto_Exit = 1 if joystick.get_button(controls['exit']) else 0

def main():
    kuksaDataBroker_IP = '20.79.188.178'
    kuksaDataBroker_Port = 55555

    with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
        while True:
            # Read PS4 controller values
            read_wheel_values()

            # Send values to KUKSA Data Broker
            client.set_current_values({
                'Vehicle.OBD.RelativeThrottlePosition': Datapoint(float(digitalAuto_Throttle)),
                'Vehicle.Powertrain.Transmission.ClutchEngagement': Datapoint(float(digitalAuto_Clutch)),
                'Vehicle.Chassis.Brake.PedalPosition': Datapoint(float(digitalAuto_Brake)),
                'Vehicle.Chassis.SteeringWheel.Angle': Datapoint(float(digitalAuto_Steering)),
                'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear': Datapoint(bool(digitalAuto_Handbrake)),
                'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear': Datapoint(bool(digitalAuto_Reverse)),
                'Vehicle.ADAS.CruiseControl.IsActive': Datapoint(bool(digitalAuto_Enter)),
                'Vehicle.ADAS.CruiseControl.IsEnabled': Datapoint(bool(digitalAuto_Exit)),
            })

            # Log the values being sent to KUKSA
            logging.info(f"KUKSA Signal - Throttle: {digitalAuto_Throttle}, Clutch: {digitalAuto_Clutch}, "
                         f"Brake: {digitalAuto_Brake}, Steering: {digitalAuto_Steering}, "
                         f"Handbrake: {digitalAuto_Handbrake}, Reverse: {digitalAuto_Reverse}, "
                         f"Enter: {digitalAuto_Enter}, Exit: {digitalAuto_Exit}")

            # Sleep to control the frequency of sending data
            time.sleep(0.1)  # Adjust this value as necessary

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error("Something went wrong, cannot start the process: %s", e)
