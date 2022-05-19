import os
import time
import netmiko
from pprint import pprint

# Collector must contain collect_data function.
# collect_data() must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
    
def reachability(config_data):
    docs = []
    doc = {}
    msgs = []
    device_name = config_data["hostname"]
    device_ip = config_data["hostip"]
    user = config_data["username"]
    pwd = config_data["password"]
    doc['device_name'] = device_name
    doc['username'] = config_data["username"]
    doc['ping'] = False
    doc['ssh'] = False
    ssh_attempts = 2
    msgs.append('DEBUG: Checking reachability for {0}'.format(device_name))
    cmd = 'ping -c 1 -W 1 {0}'.format(device_ip)
    ping_ok = os.system(cmd)
    if ping_ok != 0:
        msgs.append('DEBUG: Device {0} is not reachable.'.format(device_name))
    else:
        msgs.append('DEBUG: Device {0} is reachable.'.format(device_name))
        doc['ping'] = True
    while ssh_attempts > 0:
        try:
            device_shell = netmiko.ConnectHandler(device_type='cisco_ios',
                                                    ip=device_ip,
                                                    username=user, password=pwd,
                                                    verbose=True,
                                                    global_delay_factor=4, timeout=15)
            time.sleep(3)
            prompt = device_shell.find_prompt()
            msgs.append(f'DEBUG: Device {device_name} ssh session successful.')
            doc['ssh'] = True
            device_shell.disconnect()
            ssh_attempts = 0
        except Exception as error:
            ssh_attempts -= 1
            if ssh_attempts == 0:
                if 'Authentication failure' in str(error):
                    msgs.append(f'DEBUG: Device {device_name} authentication failure.')
                else:
                    msgs.append(f'DEBUG: Device {device_name}, {str(error)}.')
                docs.append(doc)
                return {'elastic_docs': docs, 'debug_msgs': msgs}

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
                   'username': 'admin',
                   'password': 'f00tba11',
                   'operation': 'aci'}
    docs = reachability(config_data)
    pprint(docs)