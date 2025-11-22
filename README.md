# CS60 Final Project: Mock 5G Network
Authors: Warren Shepard '26 and Nand Patel '27.

Our final project is a mock 5G Network. As we don't have any hardware (nor the necessary licenses to use the frequences we would need or the means to purchase such licenses), we just implement the software component of a 5G network, with a focus on the computer networking components. **Our main goals are to:**
1. learn and show how a 5G network broadly works from the software/computer networking perspective
1. hilight the components of the network that we think are cool (there would be no way to include everything)

A 5G Network has three primary components:
1. The device: a (subscribed) device which connects to the network.
1. Base station: a cell tower that the device connects to.
1. Core 5G Services: the core services in a 5G network, including:
    - Access Management Function (AMF)
    - Session Management Function (SMF)
    - User Plane Function (UPF)
    - Policy services (combined into one policy service for simplicity)
    - Network Registry Function (NRF)

For simplicity, all messages sent between services, the base station, and the device are sent in json format over TCP. As soon as they are recieved, they are converted to dictionaries for easy readability. In reality, data plane UFP messages would be sent as IP packets. We chose not to do that since the scope of our project was already very big and we wanted to keep things simple and stick to our goal of learning/showing how a 5G network works and hilighting some components that we think are cool.

Other things that are not included in the project include:
- Polar encoding/decoding to account for the noisy channel between the cell tower and the device on the radio layer.
- Enhanced security and privacy measures including:
    - certificates of trust between each service

## Usage
Note that everything should be run from the base directory.
Everything was tested on mac-os.

To run all services (including the base station), run
```bash
chmod +x ./run.sh
./run.sh
```

After the services are live, you can interact with the network from the device side by running
```bash
python device.py
```
Instructions on how to use the user interface will be given. This allows you to interact with the process of registering a device, registering a session, then using that session to 

### Tests
IMPORTANT: before running any of the integrated tests, make sure that the network is live. You can do this by running `./run.sh` (see above). This is becuase the integrated tests assume that the network is live. If you don't run the network first, those tests will fail!

To run all tests, run
```bash
pytest
```

To run a specific test file, run
```bash
pytest path/to/file
```

Note that the file `./pytest.ini` is to configure pytest (specifically so that the imports work correctly).

## Repository Structure

### ./common
Common functions used by multiple components of the repository. This includes:

### ./messages
All message types and an API which defines supported messages. The messages are almost exactly as described in our implementation spec (maybe with slightly different names).

### ./policies
The policies (i.e. settings and buisness configurations) of the 5G netowrk. See the README.md there for more info (also pasted below)

### ./services
All the services in the core 5G network, as well as the base station (which we put in the services section becuase it does not have any hardware associated with it, so it acts in a similar manner as a service). See more about each service in our initial requirements/implementation spec (has not changed since then).

One thing to hilight is that the role of the application layer is to a basic file request service. In a real network, application layers would be more sperated from the network (since they are made by 3rd parties) and would have way more functionality.

### ./tests
Includes unit tests and integration tests.

The primary tests for the network are located at `./tests/integrated/network_test.py`

## Network Topology
```
                     Device(s)
                         |
                         |                 Everything (but device) - - - NRF
                         |
                   Base station
                   /           \
"data" branch     /             \   "buisness logic" branch
                 /               \
          UPF Data/Control       AMF - - - Policy
                |          \      |      /
                |            \    |    /
                |              \  |  /
            Application          SMF 
```

## Security
We did not have much time to implement secuirity features (although we would have loved to!) since the scope of our project is already super big (about 3000 lines of code with more than a few services all interconnected). However, one feature that we did implement is ensuring that files have a safe path in our file provider (application) service so that users cannot request to access something outside of the designated "bin" of files using a path like `../../../passwords`. This hilights that the 5G network is just a messanger, and cannot filter out messages or requests with bad intentions! It is merely a way to get messages from point A to point B.


# Policies
(pasted from `./policies.README.md`).

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
### eMBB (Enhanced Mobile Broadband)
high speed, high capacity (i.e. high throughput and high latency).

### URLLC (Ultra-Reliable Low Latency Communications)
Very very low latency with incredible reliability.

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

Note that the `safe` option in for the application turns security features on the application layer on/off (where setting it to `true` would turn them on).