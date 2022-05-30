import netmiko
from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError
from pprint import pprint

# Collector must contain collect_data function.
# Function must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
    
def neighbour(config_data):
    docs = []
    msgs = []
    doc_type = 'neighbour'
    known_device_types = ['cisco_ios', 'cisco_nxos', 'arista_eos']
    device_name = config_data["hostname"]
    device_ip = config_data["hostip"]
    user = config_data["username"]
    pwd = config_data["password"]
    inventory_hosts = config_data["hostvars"].keys()
    
    netmiko_device_type = config_data["netmiko_device_type"]
    if netmiko_device_type not in known_device_types:
            msg = f"{device_name} unsupported device type: {netmiko_device_type}"
            msgs.append(msg)
            return {'elastic_docs': docs, 'debug_msgs': msgs}
        
    if netmiko_device_type == 'cisco_ios':
       neighbour_name_field = 'Device ID:'
       mgmt_address_flag = 'Management address(es):'
       lldp_neighbour_offset = 2
       lldp_neighbour_ip_offset = 2
       lldp_neighbour_address_field = 'Management Address'
    elif netmiko_device_type == 'cisco_nxos':
       neighbour_name_field = 'System Name:'
       mgmt_address_flag = 'Mgmt address(es):'
       lldp_neighbour_offset = 2
       lldp_neighbour_ip_offset = 2
       lldp_neighbour_address_field = 'Management Address'
    elif netmiko_device_type == 'arista_eos':
       neighbour_name_field = 'System Name:'
       mgmt_address_flag = 'Port ID     : "Management1"'
       lldp_neighbour_offset = 3
       lldp_neighbour_ip_offset = 3
       lldp_neighbour_address_field = 'Management Address        :'

    # show cdp neighors
    # Here we need to track 'Mgmt address(es):' to select correct neighbour IP address.
    # Mgmt address(es):
    #     IPv4 Address: 10.9.100.214
    device_shell = netmiko.ConnectHandler(device_type=netmiko_device_type, ip=device_ip, username=user, password=pwd)
    prompt = device_shell.find_prompt()
    cmd = 'show cdp neighbors detail | no-more'
    output = device_shell.send_command_expect(cmd, expect_string=prompt)
    for line in output.split('\n'):
        if '------' in line:
            doc = {}
            doc['doc_type'] = doc_type
            doc['device_name'] = device_name
            doc['device_ip'] = device_ip
            doc['protocol'] = 'cdp'
            mgmt_interface = False
        if neighbour_name_field in line:
            doc['neighbour'] = line.split()[2].strip('"')
        if mgmt_address_flag in line:
            # Set flag because next 'IPv4 Address:' will be neighbour address.
            mgmt_interface = True
        if 'IPv4 Address:' in line and mgmt_interface:
            doc['neighbour_ip'] = line.split()[2]
            docs.append(doc)
    # show lldp neighors
    # Here we want neighbours where local port is not management.
    device_shell = netmiko.ConnectHandler(device_type=netmiko_device_type, ip=device_ip, username=user, password=pwd)
    prompt = device_shell.find_prompt()
    cmd = 'show lldp neighbors detail | no-more'
    output = device_shell.send_command_expect(cmd, expect_string=prompt)
    for line in output.split('\n'):
        if 'Chassis' in line:
            doc = {}
            doc['doc_type'] = doc_type
            doc['device_name'] = device_name
            doc['device_ip'] = device_ip
            doc['protocol'] = 'lldp'
            mgmt_interface = False
        if neighbour_name_field in line:
            doc['neighbour'] = line.split()[lldp_neighbour_offset].strip('"')
            if doc["neighbour"] in inventory_hosts:
                doc["in_inventory"] = True
            else:
                doc["in_inventory"] = False
        if mgmt_address_flag in line:
            mgmt_interface = True
        if lldp_neighbour_address_field in line and not mgmt_interface:
            doc['neighbour_ip'] = line.split()[lldp_neighbour_ip_offset]
            docs.append(doc)
    device_shell.disconnect()
    return {'elastic_docs': docs, 'debug_msgs': msgs}
        
    
if __name__ == "__main__":
    config_data = {'elastic_host': 'elastic.default.192.168.10.120.nip.io',
                   'elastic_index': 'evobeat-neighbours',
                   'elastic_username': 'evolvere',
                   'elastic_password': 'evolvere',
                   'interval': 30,
                   'hostname': 'evo-eos02',
                   'hostip': '192.168.10.189',
                   'username': 'admin',
                   'password': 'admin',
                   'netmiko_device_type': 'arista_eos',
                   'operation': 'neighbour'}
    docs = neighbour(config_data)
    pprint(docs)
