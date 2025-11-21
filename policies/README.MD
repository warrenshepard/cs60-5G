# Policies

AI Statement: used ChatGPT to help come up with the json format

The 5G Network "knows" which devices are allowed to connect because of some
subscriber database, which we simulate with a JSON file; 
maybe we could change this to something closer to a database at some point,
but it's easy to have it simply laid out like this. Regardless, 
we could add some simple script to "register" a new subscriber to the network

The policies.json file is pretty much a settings file for the entire 5G network.

## Devices
This section keeps track of which devices are allowed to connect to the 5G network, as well
as which slices they are allowed to connect on. In a real 5G network, this would be kept track
of in a **database** of subscribers, but since this is a simple project demonstrating the networking 
features of 5G, we decided it would be fine to keep track of these here instead of in a live database.
A 5G provider would likely base which bands each device/user is allowed to connect to based on the "tier" of
their subscription. 

## Slices
### eMBB
### URLLC

## Ports
This section just keeps track of which ports each service/network component runs on.  
I clustered these into three broad categories:

### Base station
This is just a relayer that connects the device to the core services.

### Core 5G Services
The core services in the 5G Network that handle registering and connecting to the service and the "policy logic", including:
- Access Management Function (AMF)
- Session Management Function (AMF)
- Policy
- Network Registry Function (NRF)

### User Plane Function (UPF)
This includes both the control and data planes.

### Application
The application layer which the user requests data from.
Typically there would be multiple application layers, but I just grouped them into one port for now for simplicity.
