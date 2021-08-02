# pi-bitdotio-air

A minimal air quality data logger. This can be refactored, and an alternate upload method using the REST API with Python requests added, to make a demo on using bit.io for data logging. The demo may be best with a simple dashboard connected to bit.io for live remote monitoring.

## Setup

- Add a .env with your own bit.io API key
- Update the YAML to point to your desired repo/table
- Create environment
    - `python3 -m venv venv`<br>
    - `source venv/bin/activate`<br>
    - `python3 -m pip install --upgrade pip -r requirements.txt`<br>


## Run
`python pi_bitdotio.py`