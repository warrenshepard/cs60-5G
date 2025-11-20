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


ChatGPTs recomendation for the project structure. I find it to be pretty good.

cs60-5g/
├─ README.md
├─ LICENSE
├─ run.sh                         # boots everything with your policies.json (matches spec)
├─ policies/
│  ├─ policies.json               # canonical config passed to run.sh
│  ├─ policies.example.json
│  └─ schemas/
│     ├─ policy.schema.json       # JSON Schema for policies.json
│     └─ messages.schema.json     # Envelope + message types
├─ common/
│  ├─ __init__.py
│  ├─ config.py                   # loads policies.json; per-service view
│  ├─ registry_client.py          # NRF lookups (name→host:port)
│  ├─ tcp.py                      # newline-delimited JSON over TCP
│  ├─ envelope.py                 # {header, body} shape + validation
│  └─ logging.py
├─ services/
│  ├─ device/                     # UE
│  │  ├─ __init__.py
│  │  ├─ main.py                  # sends RegistrationRequest, SessionRequest, UserData(up)
│  │  └─ storage.py               # mock “files”/buffers for up/down streams
│  ├─ base_station/               # relay only (control+data planes)
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  └─ router.py                # ports/messages → AMF/UPF wiring
│  ├─ amf/                        # Access & Mobility
│  │  ├─ __init__.py
│  │  ├─ main.py                  # AllowedSlices, Admit, CreateSession, *Accept
│  │  └─ state.py
│  ├─ smf/                        # Session Manager
│  │  ├─ __init__.py
│  │  ├─ main.py                  # GetProfile, RuleInstall, CreateSessionOk
│  │  └─ ip_pool.py               # mock IP allocation
│  ├─ upf/
│  │  ├─ __init__.py
│  │  ├─ control.py               # installs/updates rules; RuleInstallOk
│  │  ├─ data.py                  # queues; enforces rate/queue/delay; UserData(down)
│  │  └─ main.py
│  ├─ policy/                     # PCF + NSSF combined
│  │  ├─ __init__.py
│  │  ├─ main.py                  # AllowedSlicesOk, AdmitOk, Profile
│  │  └─ evaluator.py             # reads slice/device/policy dicts from policies.json
│  ├─ nrf/                        # Network Repository
│  │  ├─ __init__.py
│  │  ├─ main.py                  # Register, Lookup → Service(host,port)
│  │  └─ store.py
│  └─ application/                # file service + echo
│     ├─ __init__.py
│     ├─ main.py                  # FileRequest → stream FileChunk(...)
│     └─ storage/
│        └─ sample_data.bin
├─ messages/
│  ├─ types.md                    # brief, human-readable catalog of every message type
│  ├─ envelopes.md                # header/body fields, transaction IDs, timestamps
│  └─ examples/
│     ├─ registration_request.jsonl
│     ├─ session_request.jsonl
│     └─ userdata_up.jsonl
├─ scripts/
│  ├─ dev_kill_all.sh
│  ├─ dev_tail_all.sh
│  └─ generate_sample_policies.py
├─ tests/
│  ├─ unit/
│  │  ├─ test_envelope.py
│  │  ├─ test_policy_eval.py
│  │  ├─ test_rule_install.py
│  │  └─ ...
│  ├─ integration/
│  │  ├─ test_register_then_session.py   # “bottom→top” bring-up path
│  │  └─ test_data_plane_streams.py
│  └─ fixtures/
│     ├─ small_file.bin
│     └─ policies_min.json
└─ Makefile                       # make run | test | lint | format


                                                      **Device**  
                                                        |  
                                                        |  
                                                        |  
                                                  **Base station**  
                                                   /        \  
                                                  /          \  
                                                 /            \  
                                               **UPF**            **AMF**  
                                                |              |  
                                                |              |  
                                                |              |  
                                           **Application**        **SMF**  