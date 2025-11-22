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
    - Policy services
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

### Tests
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
All message types and an API which defines supported messages. See the README.md there for information on the purpose and structure of each message.

### ./policies
The policies (i.e. settings and buisness configurations) of the 5G netowrk. See the README.md there for more info.

### ./services
All the services in the core 5G network, as well as the base station (which we put in the services section becuase it does not have any hardware associated with it, so it acts in a similar manner as a service).

### ./tests
Includes unit tests and integration tests.



Random notes:

Office hours questions:

- ChatGPT for unit tests
- security/privacy stuff
    - TLS wrapper for basic encryption
    - with certs and PKI
- polar coding stuff (nice to have)
    - this would be on the radio layer
    - simulate by adding noise on the reciever
    - simulate VBSK or BPSK idk?
    - just want to see how well it handles noise
    - way better than QAM 1026

IDEA: add options for emergency requests/sessions

```
                                                       Device
                                                         |
                                                         |
                                                         |
                                                     Base station
                                                    /           \
                                                   /             \
                                                  /               \
                                                UPF               AMF
                                                 |                 |
                                                 |                 |
                                                 |                 |
                                            Application           SMF
```