import logging
import time
from kuksa_client.grpc import VSSClient  # Ensure this is the correct import based on your environment
from threading import Lock

# Data class to hold vehicle data
class SharedData:
    def __init__(self):
        self.throttle = 0.0
        self.clutch = 0.0
        self.brake = 0.0
        self.speed = 0.0
        self.handbrake_active = False
        self.reverse_active = False
        self.cruise_control_active = False
        self.cruise_control_enabled = False
        self.lock = Lock()

# KUKSA Subscriber class
class KUKSASubscriber:
    def __init__(self, kuksaDataBroker_IP, kuksaDataBroker_Port):
        self.kuksaDataBroker_IP = kuksaDataBroker_IP
        self.kuksaDataBroker_Port = kuksaDataBroker_Port
        self.shared_data = SharedData()

        # Configure logging
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self):
        try:
            with VSSClient(self.kuksaDataBroker_IP, self.kuksaDataBroker_Port) as client:
                client.subscribe_current_values([
                    'Vehicle.OBD.RelativeThrottlePosition',
                    'Vehicle.Powertrain.Transmission.ClutchEngagement',
                    'Vehicle.ADAS.CruiseControl.SpeedSet',
                    'Vehicle.Speed',
                    'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear',
                    'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear',
                    'Vehicle.ADAS.CruiseControl.IsActive',
                    'Vehicle.ADAS.CruiseControl.IsEnabled',
                ])

                while True:
                    updates = client.get_current_values([
                        'Vehicle.OBD.RelativeThrottlePosition',
                        'Vehicle.Powertrain.Transmission.ClutchEngagement',
                        'Vehicle.ADAS.CruiseControl.SpeedSet',
                        'Vehicle.Speed',
                        'Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear',
                        'Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear',
                        'Vehicle.ADAS.CruiseControl.IsActive',
                        'Vehicle.ADAS.CruiseControl.IsEnabled',
                    ])

                    if updates:
                        with self.shared_data.lock:
                            # Access .value from Datapoint objects
                            self.shared_data.throttle = updates.get('Vehicle.OBD.RelativeThrottlePosition', 0.0).value
                            self.shared_data.clutch = updates.get('Vehicle.Powertrain.Transmission.ClutchEngagement', 0.0).value
                            self.shared_data.brake = updates.get('Vehicle.ADAS.CruiseControl.SpeedSet', 0.0).value
                            self.shared_data.speed = updates.get('Vehicle.Speed', 0.0).value
                            self.shared_data.handbrake_active = updates.get('Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear', False).value
                            self.shared_data.reverse_active = updates.get('Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear', False).value
                            self.shared_data.cruise_control_active = updates.get('Vehicle.ADAS.CruiseControl.IsActive', False).value
                            self.shared_data.cruise_control_enabled = updates.get('Vehicle.ADAS.CruiseControl.IsEnabled', False).value

                        # Print values with labels
                        print(f"Throttle: {self.shared_data.throttle}")
                        print(f"Clutch: {self.shared_data.clutch}")
                        print(f"Brake: {self.shared_data.brake}")
                        print(f"Speed: {self.shared_data.speed}")
                        print(f"Handbrake Active: {int(self.shared_data.handbrake_active)}")  # Convert boolean to int for printing
                        print(f"Reverse Active: {int(self.shared_data.reverse_active)}")    # Convert boolean to int for printing
                        print(f"Cruise Control Active: {int(self.shared_data.cruise_control_active)}")  # Convert boolean to int for printing
                        print(f"Cruise Control Enabled: {int(self.shared_data.cruise_control_enabled)}")  # Convert boolean to int for printing
                        print("-----------------------------------------------------------------")
                    time.sleep(0.5)  # Adjust sleep as necessary

        except Exception as e:
            logging.error(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Replace with your KUKSA Data Broker's IP and Port
    KUKSA_IP = "20.79.188.178"  # KUKSA Data Broker IP
    KUKSA_PORT = 55555           # KUKSA Data Broker Port

    subscriber = KUKSASubscriber(KUKSA_IP, KUKSA_PORT)
    subscriber.run()

