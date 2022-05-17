import os
import time
import netmiko

# Collector must contain collect_data function.
# collect_data() must return a dictionary with keys elastic_docs and debug_msgs
# Values for both are lists.
def collect_data(config_data):
    
    def reachability(device_name, device_ip, user, pwd):
        docs = []
        doc = {}
        msgs = []
        doc['device_name'] = device_name
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
    
    if config_data["operation"] == 'reachability':
        result = reachability(config_data["hostname"], config_data["hostip"], config_data["username"], config_data["password"])
    else:
        result = {'elastic_docs': [], 'debug_msgs': []}
    
    return result