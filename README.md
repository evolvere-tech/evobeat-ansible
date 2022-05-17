# README #

Elasticsearch data collector for infrastructure.

### Overview ###
* evobeat provides common methods to collect data from devices and POST documents to elastic-search.
* functions are in the collector module.

### Deployment ###
#### Dependencies
* Python 3.6
* Python Virtualenv
#### Clone and install
    git clone repository
    create virtualenv:
    ```
    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    ```
#### Collector functions
As infrastructure has bespoke APIs (or no API at all), evobeat requires collector modules to retrieve data.
Collector functions must be stored in ```module_utils/collectors.py``` .

#### Ansible module
Collector functions are run using the ```evobeat``` module.
Confguration files are used to provide configuration data to evobeat. They must be stored in the ```configs``` directory.
A sample configuration file ```test_collector.yaml``` is provided.

### Running evobeat

```
ansible-playbook -i hosts test_play.yml
```
