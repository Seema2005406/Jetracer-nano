# JetRacer KUKSA Controller

This project implements a controller for a JetRacer using the KUKSA data broker signals to drive the Nvidia Racecar. The controller subscribes to various vehicle signals and translates them into actions for the JetRacer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Code Structure](#Code Structure)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Docker** installed on your machine.
- A **JetRacer** vehicle equipped with Nvidia hardware.
- Access to a KUKSA data broker server.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Seema2005406/Jetracer-nano.git
   cd Jetracer-nano
```
Build the Docker image:

```bash
docker build -t jetracer-kuksa-controller .
```

Run the Docker container:

```bash
    docker run jetracer-kuksa-controller
```

    

## Usage

The controller will start by subscribing to relevant vehicle signals from the KUKSA data broker. It translates these signals into control inputs for the JetRacer. The current values of the vehicle's state will be printed in the console.
Available Signals:

    Vehicle.OBD.RelativeThrottlePosition
    Vehicle.Powertrain.Transmission.ClutchEngagement
    Vehicle.Chassis.Brake.PedalPosition
    Vehicle.Speed
    Vehicle.Chassis.Axle.Row1.Wheel.Right.Brake.PadWear
    Vehicle.Chassis.Axle.Row2.Wheel.Left.Brake.PadWear
    Vehicle.ADAS.CruiseControl.IsActive
    Vehicle.ADAS.CruiseControl.IsEnabled

### Configuration

You can configure the KUKSA data broker IP and port by setting environment variables:

    KUKSA_DATA_BROKER_IP: The IP address of your KUKSA data broker (default: 20.79.188.178).
    KUKSA_DATA_BROKER_PORT: The port for the KUKSA data broker (default: 55555).

### Code Structure

    Dockerfile: Contains instructions for building the Docker image.
    car_controller.py: The main application that handles vehicle control logic based on KUKSA signals.
