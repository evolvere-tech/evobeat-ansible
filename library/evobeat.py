from ansible.module_utils.evobeatd import basebeat, collect_data
from ansible.module_utils.basic import *

# Define module args
module_args = {
    "name": {"required": True, "type": "str"},
    "mode": {"required": True, "type": "str"},
    "elastic_host": {"required": True, "type": "str"},
    "elastic_index": {"required": True, "type": "str"},
    "elastic_username": {"required": True, "type": "str"},
    "elastic_password": {"required": True, "type": "str"},
    "collector_module": {"required": True, "type": "str"},
    "elastic_port": {"required": False, "type": "int"},
    "elastic_schema": {"required": False, "type": "str"},
    "elastic_verify_certs": {"required": False, "type": "str"},
    "elastic_index_rotate": {"required": False, "type": "str"},
    "interval": {"required": False, "type": "str"},
    "hostname": {"required": True, "type": "str"},
    "hostip": {"required": True, "type": "str"},
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str"}
}

# Initialise the result dictionary
result = {
    "changed": False,
    "elastic_docs": [],
    "errors": [],
    "debug": []
} 

messages = []
errors = []

# Instantiate AnsibleModule
module = AnsibleModule(argument_spec=module_args)

# Mandatory parameters
mode = 'test'
name = 'test_collector'
config_data = {}
# Mandatory parameters
config_data['elastic_host'] = 'elastic.default.192.168.10.120.nip.io'
config_data['elastic_index'] = 'test-evobeat'
config_data['elastic_username'] = 'evolvere'
config_data['elastic_password'] = 'evolvere'
config_data['collector_module'] = 'test_collector'
# Optional parameters
config_data['elastic_port'] = 443                  # Defaults to 443
config_data['elastic_scheme'] = 'https'              # Options are 'https' (default) or 'http'
config_data['elastic_verify_certs'] = False        # Options are False (default) or True
config_data['elastic_index_rotate'] = 'daily'        # Options are 'daily' (default) or 'monthly'
config_data['interval'] = 30                       # Defaults to 30 seconds
config_data['log_file'] = 'stdout'                   # Defaults to logs/{name}.log
# Inventory parameters
config_data['hostname'] = 'test-host' # inventory_hostname
config_data['hostip'] = '192.168.10.10'   # ansible_host
config_data['username'] = 'ansible-user'    # ansible_user
config_data['password'] = 'ansible-password'  #ansible_password

beat = basebeat(name=name, mode='test', config_data=config_data)
elastic_docs = collect_data(config_data)

result["elastic_docs"] = elastic_docs
module.exit_json(**result)
