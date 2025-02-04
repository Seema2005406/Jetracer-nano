
# What is Kuksa Databroker?

# Overview

Kuksa DataBroker is an open-source data management middleware designed specifically for connected vehicles. It acts as a unified data exchange layer, enabling secure and standardized communication between vehicle sensors, actuators, and cloud-based applications.

# Features

Standardized Data Access: Implements Vehicle Signal Specification (VSS) for a consistent signal hierarchy.

Efficient Data Streaming: Supports real-time data collection and publishing from vehicle components.

Security & Access Control: Uses authentication and authorization mechanisms to manage access.

Multiple Protocol Support: Works with gRPC, MQTT, and WebSocket for flexible integration.

Cloud Connectivity: Enables seamless cloud integration for telematics and analytics use cases.

# Architecture

The core components of Kuksa DataBroker include:

Data Provider: Sources vehicle data (CAN bus, sensors, ECUs, etc.).

DataBroker Core: The central hub that normalizes and distributes data.

Data Clients: Applications or services subscribing to vehicle data.

Security Layer: Ensures role-based access and encryption.

## Folder G29 has all files for G29 config with PC - KUksa

## Folder Jetracer has all files for KUksa and jetson configuration

## Test_File_PS4 is test folder for PS4

# Please refer to readme file inside respective folder for more information
