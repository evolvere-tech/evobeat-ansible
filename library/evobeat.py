# Copyright: (c) 2022, steve@evolvere-tech.co.uk
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: evobeat

short_description: Framework to simplify posting telemetry data to Elastic.

version_added: "1.0.0"

description: Add custom functions to module_utils/collector.py and run them using Ansible.

options:
    mode:
        description: Can be 'test' or 'run'. Use test mode to verify custom code without posting to elastic.
        required: true
        type: str
    
    elastic_host:
        description: Name or IP address of elastic cluster.
        required: true
        type: str
        
    elastic_index:
        description: Prefix for elastic index name where data will be posted.
        required: true
        type: str
        
    elastic_username:
        description: Username credential for elastic cluster.
        required: true
        type: str
        
author:
    - Steve Corp (@beertwanger)
'''

import os
from ansible.module_utils.evobeatd import basebeat
from ansible.module_utils.collector import collect_data
from ansible.module_utils.basic import *

# Define module args
module_args = {
    "mode": {"required": True, "type": "str"},
    "elastic_host": {"required": True, "type": "str"},
    "elastic_index": {"required": True, "type": "str"},
    "elastic_username": {"required": True, "type": "str"},
    "elastic_password": {"required": True, "type": "str"},
    "operation": {"required": True, "type": "str"},
    "elastic_port": {"required": False, "type": "int"},
    "elastic_scheme": {"required": False, "type": "str"},
    "elastic_verify_certs": {"required": False, "type": "bool"},
    "elastic_ca_cert": {"required": False, "type": "str"},
    "elastic_index_rotate": {"required": False, "type": "str"},
    "non_timeseries": {"required": False, "type": "bool"},
    "key_field": {"required": False, "type": "str"},
    "interval": {"required": False, "type": "int"},
    "debug": {"required": False, "type": "bool"},
    "hostname": {"required": True, "type": "str"},
    "hostip": {"required": True, "type": "str"},
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str"},
    "hostvars": {"required": False, "type": "dict"},
    "netmiko_device_type": {"required": False, "type": "str"}
}

# Initialise the result dictionary
result = {
    "changed": False,
    "elastic_docs": [],
    "errors": [],
    "messages": [],
    "debug": []
} 

errors = []

# Instantiate AnsibleModule
module = AnsibleModule(argument_spec=module_args)
config_data = {}
# Mandatory parameters
config_data["mode"] = module.params["mode"]
if config_data["mode"] not in ['test', 'run', 'collect', 'post']:
    errors.append('ERROR: mode must be "test", "run", "collect" or "post.')
config_data["elastic_host"] = module.params["elastic_host"]
config_data["elastic_index"] = module.params["elastic_index"] 
config_data["elastic_username"] = module.params["elastic_username"]
config_data["elastic_password"] = module.params["elastic_password"]
config_data["operation"] = module.params["operation"]
# Optional parameters
# elastic_port defaults to 443
config_data["elastic_port"] = 443
if module.params["elastic_port"]:
    if module.params["elastic_port"] in range(1, 49151):
        config_data["elastic_port"] = module.params["elastic_port"]
    else:
        errors.append('ERROR: elastic_port must be integer in range 1 - 49151.')
# elastic_scheme options are 'https' (default) or 'http'
config_data["elastic_scheme"] = 'https'
if module.params["elastic_scheme"]:
    if module.params["elastic_scheme"] in ['http', 'HTTP', 'https', 'HTTPS']:
        config_data["elastic_scheme"] = module.params["elastic_scheme"]
    else:
        errors.append('ERROR: elastic_scheme must be "http" or "https".')
# elastic_verify_certs options are False (default) or True
config_data["elastic_verify_certs"] = False
if module.params["elastic_verify_certs"]:
    config_data["elastic_verify_certs"] = module.params["elastic_verify_certs"]
# elastic_ca_cert defaults to ''
config_data["elastic_ca_cert"] = ''
if module.params["elastic_ca_cert"]:
    if os.path.exists(module.params["elastic_ca_cert"]):
        config_data["elastic_ca_cert"] = module.params["elastic_ca_cert"]
    else:
        errors.append(f'ERROR: ca cert file {module.params["elastic_ca_cert"]} not found.')
# elastic_index_rotate options are 'daily' (default) or 'monthly'
config_data["elastic_index_rotate"] = 'daily'
if module.params["elastic_index_rotate"]:
    if module.params["elastic_index_rotate"] in ['daily', 'monthly']:
        config_data["elastic_index_rotate"] = config_data["elastic_index_rotate"]
    else:
        errors.append('ERROR: elastic_index_rotate must be "daily" or "monthly".')
# non_timeseries defaults to False
config_data["non_timeseries"] = False
if module.params["non_timeseries"]:
    config_data["non_timeseries"] = module.params["non_timeseries"]
# key_field defaults to ''
config_data["key_field"] = ''
if module.params["key_field"]:
    config_data["key_field"] = module.params["key_field"]
# non_timeseries requires key_field
if config_data["non_timeseries"]:
    if not config_data["key_field"]:
        errors.append('ERROR: key_field required for non_timeseries data.')
# interval defaults to 30 seconds
config_data["interval"] = 30
if module.params["interval"]:
    if module.params["interval"] < 30:
        errors.append('ERROR: interval (seconds) must be >= 30')
    else:
        config_data["interval"] = module.params["interval"]
# debug defaults to False
config_data["debug"] = False
if module.params["debug"]:
    config_data["debug"] = True
# Inventory parameters
config_data["hostname"] = module.params["hostname"]   # inventory_hostname
config_data["hostip"] = module.params["hostip"]       # ansible_host
config_data["username"] = module.params["username"]   # ansible_user
config_data["password"] = module.params["password"]   # ansible_password
# hostvars
config_data["hostvars"] = {}
if module.params["hostvars"]: 
    config_data["hostvars"] = module.params["hostvars"]
# netmiko_device_type
config_data["netmiko_device_type"] = ''
if module.params["netmiko_device_type"]: 
    config_data["netmiko_device_type"] = module.params["netmiko_device_type"]

if errors:
    result["errors"] = errors
    module.fail_json(msg=f'Invalid module parameters.', **result)
    
beat = basebeat(mode=config_data["mode"], config_data=config_data)
if config_data["mode"] != 'post':
    collect_result = collect_data(config_data)
# Test or collect mode
error_flag = False
if config_data["mode"] in ['test', 'collect']:
    result["elastic_docs"] = collect_result["elastic_docs"]
    if config_data["mode"] == 'test':
        result["messages"] = beat.msgs
    for msg in beat.msgs:
        if 'ERROR:' in msg:
            error_flag = True
    if error_flag:
        module.fail_json(msg=f'Test failed.', **result)
    else:
        module.exit_json(**result)
# Run mode
elif config_data["mode"] == 'run':
    beat.elastic_docs = collect_result["elastic_docs"]
    post_result = beat.post()
    result["elastic_docs"] = collect_result["elastic_docs"]
    result["messages"] = beat.msgs
    if config_data["debug"]:
        result["debug"] = collect_result["debug_msgs"]
    if post_result["rc"]:
        module.fail_json(msg=f'POST to elastic failed.', **result)
    else:
        module.exit_json(**result)
# Post mode
else:
    post_result = beat.post(docs=config_data["hostvars"])
    result["messages"] = beat.msgs
    if post_result["rc"]:
        module.fail_json(msg=f'POST to elastic failed.', **result)
    else:
        module.exit_json(**result)
