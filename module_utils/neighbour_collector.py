import netmiko
from pprint import pprint

# Collector must contain collect_data function.
# Function must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
    
def neighbour(config_data):
    docs = []
    msgs = []
    device_name = config_data["hostname"]
    device_ip = config_data["hostip"]
    user = config_data["username"]
    pwd = config_data["password"]
    netmiko_device_type = config_data["device_type"]
    if netmiko_device_type == 'cisco_ios':
       neighbour_name_field = 'Device ID:'
       mgmt_address_flag = 'Management address(es):'
    elif netmiko_device_type == 'cisco_nxos':
       neighbour_name_field = 'System Name:'

    # show cdp neighors
    # Here we need to track 'Mgmt address(es):' to select correct neighbour IP address.
    # Mgmt address(es):
    #     IPv4 Address: 10.9.100.214
    device_shell = netmiko.ConnectHandler(device_type='cisco_nxos', ip=device_ip, username=user, password=pwd)
    prompt = device_shell.find_prompt()
    cmd = 'show cdp neighbors detail | no-more'
    output = device_shell.send_command_expect(cmd, expect_string=prompt)
    for line in output.split('\n'):
        if '------' in line:
            doc = {}
            doc['device_name'] = device_name
            doc['device_ip'] = device_ip
            doc['protocol'] = 'cdp'
            mgmt_interface = False
        if neighbour_name_field in line:
            doc['neighbour'] = line.split()[2]
        if 'Mgmt address(es):' in line:
            mgmt_interface = True
        if 'IPv4 Address:' in line and mgmt_interface:
            doc['neighbour_ip'] = line.split()[2]
            docs.append(doc)
    # show lldp neighors
    # Here we want neighbours where local mort is not management.
    device_shell = netmiko.ConnectHandler(device_type='cisco_nxos', ip=device_ip, username=user, password=pwd)
    prompt = device_shell.find_prompt()
    cmd = 'show lldp neighbors detail | no-more'
    output = device_shell.send_command_expect(cmd, expect_string=prompt)
    for line in output.split('\n'):
        if 'Chassis id:' in line:
            doc = {}
            doc['device_name'] = device_name
            doc['device_ip'] = device_ip
            doc['protocol'] = 'lldp'
            mgmt_interface = False
        if 'System Name:' in line:
            doc['neighbour'] = line.split()[2]
        if 'Local Port id: mgmt' in line:
            mgmt_interface = True
        if 'Management Address:' in line and not mgmt_interface:
            doc['neighbour_ip'] = line.split()[2]
            docs.append(doc)
    device_shell.disconnect()
    return {'elastic_docs': docs, 'debug_msgs': msgs}
        
    
if __name__ == "__main__":
    config_data = {'elastic_host': 'elastic.default.192.168.10.120.nip.io',
                   'elastic_index': 'aci-evobeat',
                   'elastic_username': 'evolvere',
                   'elastic_password': 'evolvere',
                   'interval': 30,
                   'hostname': 'evo-nxos01',
                   'hostip': '10.9.100.213',
                   'username': 'admin',
                   'password': 'admin',
                   'operation': 'neighbour'}
    docs = neighbour(config_data)
    pprint(docs)
