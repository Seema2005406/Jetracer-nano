import os
import time
import logging
from jetracer.nvidia_racecar import NvidiaRacecar
from kuksa_client.grpc import VSSClient

# Get the KUKSA data broker IP and port from environment variables
KUKSA_DATA_BROKER_IP = '20.79.188.178'  # Replace with your KUKSA server IP
KUKSA_DATA_BROKER_PORT = 55555  # Default port for KUKSA

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize NvidiaRacecar
car = NvidiaRacecar()

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def map_kuksa_to_racecar(updates):
    """Map the KUKSA signal values to the NvidiaRacecar control."""
    # Extract the KUKSA signal values
    throttle = updates['Vehicle.OBD.RelativeThrottlePosition'].value
    clutch = updates['Vehicle.Powertrain.Transmission.ClutchEngagement'].value
    brake = updates['Vehicle.Chassis.Brake.PedalPosition'].value
    steering = updates['Vehicle.Speed'].value
    handbrake = updates['Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear'].value
    reverse = updates['Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear'].value
    enter = updates['Vehicle.ADAS.CruiseControl.IsActive'].value
    exit = updates['Vehicle.ADAS.CruiseControl.IsEnabled'].value
    throttle = clamp(throttle, -1.0, 1.0)

    # Ensure vehicle doesn't move at startup (initialize to safe values)
    if throttle == -1.0 and steering == 0.0 and reverse == 0:
        logger.info("Vehicle initialized with safe values.")
        car.throttle = 0.0  # Neutral throttle to prevent movement
        car.steering = 0.0  # Neutral steering
        car.reverse = 0      # Ensure reverse is not active
        return
    # Map steering
    car.steering = steering   # Adjust gain if necessary
    car.throttle = throttle
    # Map throttle (forward/reverse)
    if reverse == 1:
        car.throttle = -throttle  # Negative throttle for reverse
    else:
        car.throttle = throttle   # Positive throttle for normal

    # Apply brake logic: simulate braking by reducing throttle
    if brake > 0:
        car.throttle = max(0, car.throttle - brake)  # Reduce throttle as brake is applied

    # Handbrake: Set throttle to 0 if handbrake is active
    if handbrake == 1:
        car.throttle = 0

    # Log the current state for debugging
    logging.info(f"Throttle: {car.throttle}, Steering: {car.steering}, Handbrake: {handbrake}, Rever$

def main():
    with VSSClient(KUKSA_DATA_BROKER_IP, KUKSA_DATA_BROKER_PORT) as client:
        # Subscribe to the signals published by the G29 controller script
        client.subscribe_current_values([
            'Vehicle.OBD.RelativeThrottlePosition',
            'Vehicle.Powertrain.Transmission.ClutchEngagement',
            'Vehicle.Chassis.Brake.PedalPosition',
            'Vehicle.Speed',
            'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear',
            'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear',
            'Vehicle.ADAS.CruiseControl.IsActive',
            'Vehicle.ADAS.CruiseControl.IsEnabled',
        ])

        print("Subscribed to KUKSA signals...")

        while True:
            # Get the current values for the subscribed signals
            updates = client.get_current_values([
                'Vehicle.OBD.RelativeThrottlePosition',
                'Vehicle.Powertrain.Transmission.ClutchEngagement',
                'Vehicle.Chassis.Brake.PedalPosition',
                'Vehicle.Speed',
                'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear',
                'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear',
                'Vehicle.ADAS.CruiseControl.IsActive',
                'Vehicle.ADAS.CruiseControl.IsEnabled',
                
            ])

            # Map the KUKSA signals to the racecar control
            map_kuksa_to_racecar(updates)

            # Print the current values
            print("Current Values:")
            print(f"Throttle: {updates['Vehicle.OBD.RelativeThrottlePosition'].value}")
            print(f"Clutch: {updates['Vehicle.Powertrain.Transmission.ClutchEngagement'].value}")
            print(f"Brake: {updates['Vehicle.Chassis.Brake.PedalPosition'].value}")
            print(f"Steering: {updates['Vehicle.Speed'].value}")
            print(f"Handbrake Active: {updates['Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear'$
            print(f"Reverse Active: {updates['Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear'].v$
            print(f"Enter Active: {updates['Vehicle.ADAS.CruiseControl.IsActive'].value}")
            print(f"Exit Active: {updates['Vehicle.ADAS.CruiseControl.IsEnabled'].value}")
            print("----------------------------")

            time.sleep(0.1)  # Adjust the delay for a smooth control loop

if __name__ == '__main__':
    main()




