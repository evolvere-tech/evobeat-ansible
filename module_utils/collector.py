from ansible.module_utils.reachability_collector import reachability
from ansible.module_utils.aci_collector import aci
from pprint import pprint

# collector functions must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
def collect_data(config_data):

    if config_data["operation"] == 'reachability':
        result = reachability(config_data)
    elif config_data["operation"] == 'aci':
        result = aci(config_data)
    else:
        result = {'elastic_docs': [], 'debug_msgs': []}
    return result

if __name__ == "__main__":
    config_data = {'elastic_host': 'elastic.default.192.168.10.120.nip.io',
                   'elastic_index': 'aci-evobeat',
                   'elastic_username': 'evolvere',
                   'elastic_password': 'evolvere',
                   'interval': 30,
                   'hostname': 'UKGRNFAB1',
                   'hostip': '192.168.104.10',
                   'username': 'admin',
                   'password': 'f00tba11',
                   'operation': 'aci'}
    docs = collect_data(config_data)
    pprint(docs)