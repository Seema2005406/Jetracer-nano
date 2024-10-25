import logging
import time
import threading
import pygame
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

print("\r++++++++++++++++++++++++++++++++++++\r")
print("Welcome to the G29 Controller\r")
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

# Initialize the first joystick (assumed to be the G29)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick initialized: {joystick.get_name()}")

# Control mappings
controls = {
    'steering_wheel': 0,
    'clutch': 1,
    'throttle': 2,
    'brake': 3,
    'handbrake': 4,
    'reverse': 5,
    'enter': 6,
    'exit': 7
}

# Global variables for G29 values
digitalAuto_Throttle = 0.0
digitalAuto_Clutch = 0.0
digitalAuto_Brake = 0.0
digitalAuto_Steering = 0.0

# Global variables for button states
digitalAuto_Handbrake = 0  # 1 if pressed, 0 if not pressed
digitalAuto_Reverse = 0     # 1 if pressed, 0 if not pressed
digitalAuto_Enter = 0       # 1 if pressed, 0 if not pressed
digitalAuto_Exit = 0        # 1 if pressed, 0 if not pressed

# Function to read values from the joystick
def read_wheel_values():
    pygame.event.pump()  # Update joystick state
    
    # Read axis values for controls
    steering_value = joystick.get_axis(controls['steering_wheel'])
    clutch_value = joystick.get_axis(controls['clutch'])
    throttle_value = joystick.get_axis(controls['throttle'])
    brake_value = joystick.get_axis(controls['brake'])

    # Update global variables with raw values (no normalization)
    global digitalAuto_Steering, digitalAuto_Clutch, digitalAuto_Throttle, digitalAuto_Brake
    digitalAuto_Steering = steering_value * 5  # Raw value
    digitalAuto_Clutch = abs(clutch_value - 0.999969482421875) # Raw value
    digitalAuto_Throttle = abs((throttle_value - 0.999969482421875)*0.2) # Raw value
    digitalAuto_Brake = abs(brake_value - 0.999969482421875) # Raw value

    # Read button states
    global digitalAuto_Handbrake, digitalAuto_Reverse, digitalAuto_Enter, digitalAuto_Exit
    digitalAuto_Handbrake = 1 if joystick.get_button(controls['handbrake']) else 0
    digitalAuto_Reverse = 1 if joystick.get_button(controls['reverse']) else 0
    digitalAuto_Enter = 1 if joystick.get_button(controls['enter']) else 0
    digitalAuto_Exit = 1 if joystick.get_button(controls['exit']) else 0

def thread_ConnectToKuksa():
    global digitalAuto_Throttle, digitalAuto_Clutch, digitalAuto_Brake, digitalAuto_Steering
    global digitalAuto_Handbrake, digitalAuto_Reverse, digitalAuto_Enter, digitalAuto_Exit

    kuksaDataBroker_IP = '20.79.188.178'
    kuksaDataBroker_Port = 55555

    with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
        while True:
            # Send values to KUKSA without normalization
            client.set_current_values({
                'Vehicle.OBD.RelativeThrottlePosition': Datapoint(float(digitalAuto_Throttle)),
                'Vehicle.Powertrain.Transmission.ClutchEngagement': Datapoint(float(digitalAuto_Clutch)),
                'Vehicle.Chassis.Brake.PedalPosition': Datapoint(float(digitalAuto_Brake)),
                'Vehicle.Speed': Datapoint(float(digitalAuto_Steering)),
                'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear': Datapoint(bool(digitalAuto_Handbrake)),
                'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear': Datapoint(bool(digitalAuto_Reverse)),
                'Vehicle.ADAS.CruiseControl.IsActive': Datapoint(bool(digitalAuto_Enter)),
                'Vehicle.ADAS.CruiseControl.IsEnabled': Datapoint(bool(digitalAuto_Exit)),
            })

            # Print the values being sent to KUKSA
            print(f"KUKSA Signal - Throttle: {digitalAuto_Throttle}, Clutch: {digitalAuto_Clutch}, "
                  f"Brake: {digitalAuto_Brake}, Steering: {digitalAuto_Steering}, "
                  f"Handbrake: {digitalAuto_Handbrake}, Reverse: {digitalAuto_Reverse}, "
                  f"Enter: {digitalAuto_Enter}, Exit: {digitalAuto_Exit}")
            print("\n")  # Adding space for clarity

            time.sleep(0.5)  # Adjust as needed

if __name__ == '__main__':
    try:
        # Start reading joystick values
        reading_thread = threading.Thread(target=lambda: [read_wheel_values() for _ in iter(int, 1)])
        reading_thread.start()

        # Start KUKSA client thread
        kuksa_thread = threading.Thread(target=thread_ConnectToKuksa)
        kuksa_thread.start()

        # Wait threads to finish
        while True:
            time.sleep(0.5)  # Add a delay to prevent CPU overload in the main thread
            print(f"Current Values - Throttle: {digitalAuto_Throttle}, Clutch: {digitalAuto_Clutch}, "
                  f"Brake: {digitalAuto_Brake}, Steering: {digitalAuto_Steering}, "
                  f"Handbrake: {digitalAuto_Handbrake}, Reverse: {digitalAuto_Reverse}, "
                  f"Enter: {digitalAuto_Enter}, Exit: {digitalAuto_Exit}")
            print("\n")  # Adding space for clarity

    except Exception as e:
        print("Something went wrong, cannot start the process:", e)
