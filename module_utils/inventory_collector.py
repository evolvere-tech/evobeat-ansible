import os
import time
import netmiko
from pprint import pprint

# Collector must contain collect_data function.
# Function must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
    
def inventory(config_data):
    docs = []
    doc = {}
    msgs = []
    device_name = config_data["hostname"]
    device_ip = config_data["hostip"]
    doc['device_name'] = device_name
    doc['device_ip'] = device_ip
    docs.append(doc)
    return {'elastic_docs': docs, 'debug_msgs': msgs}
        
    
if __name__ == "__main__":
    config_data = {'elastic_host': 'elastic.default.192.168.10.120.nip.io',
                   'elastic_index': 'aci-evobeat',
                   'elastic_username': 'evolvere',
                   'elastic_password': 'evolvere',
                   'interval': 30,
                   'hostname': 'UKGRNFAB1',
                   'hostip': '192.168.104.10',
                   'operation': 'inventory'}
    docs = inventory(config_data)
    pprint(docs)
