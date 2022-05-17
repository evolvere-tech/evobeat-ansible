import sys
import os
import time
import sys
import datetime
import urllib3
import yaml
import json
import logging
import importlib
import importlib.util
import traceback
from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection
from pprint import pprint
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from ansible.module_utils.collector import collect_data


class basebeat(object):

    def __init__(self, **kwargs):
        self.version = '1.0.1'
        self.path = os.getcwd()
        self.msgs = []
        self.elastic_docs = []
        self.debug = False
        self.config_data = {}
        if kwargs:
            self.config_data = kwargs['config_data']
            self.name = self.config_data['name']
            self.mode = self.config_data['mode']

        # Mandatory parameters
        self.elastic_host = self.config_data['elastic_host']
        self.elastic_index = self.config_data['elastic_index']
        self.elastic_username = self.config_data['elastic_username']
        self.elastic_password = self.config_data['elastic_password']
        # Optional parameters
        # elastic_port defaults to 443
        self.elastic_port = self.config_data["elastic_port"]
        # elastic_scheme defaults to 'https'
        self.elastic_scheme = self.config_data["elastic_scheme"]
        # elastic_verify_certs defaults to False
        self.elastic_verify_certs = self.config_data["elastic_verify_certs"]
        # elastic_index_rotate defaults to 'daily'
        self.elastic_index_rotate = self.config_data["elastic_index_rotate"]
        # interval defaults to 30 seconds
        if 'interval' in self.config_data:
            if self.config_data['interval'] < 30:
                sys.exit('ERROR: Minimum interval is 30.')
            self.interval = self.config_data['interval']
        else:
            self.interval = 60
        # Create elastic session
        self.es = Elasticsearch(
                        self.elastic_host,
                        http_auth=(self.elastic_username,self.elastic_password),
                        port=self.elastic_port,
                        scheme=self.elastic_scheme,
                        verify_certs=False,
                        connection_class=RequestsHttpConnection,
                        request_timeout=10
                            )
        # Test connection to elastic
        self.msgs.append(f'INFO: Testing connection to elasticsearch ...')      
        self.msgs.append(f'INFO: host:{self.elastic_host} port:{self.elastic_port} scheme:{self.elastic_scheme}.')
        if not self.es.ping(request_timeout=1):
            if self.mode == "test":
                self.msgs.append('WARNING: Connection to elasticsearch failed.')
            else:
                self.msgs.append('ERROR: Connection to elasticsearch failed.')
        else:
            self.msgs.append('INFO: Connection successful.')
        # Disable certificate warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
        urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)

    def __del__(self):
        try:
            self.msgs.append('Stopped.')
        except:
            pass

    def post(self):
        f_name = sys._getframe().f_code.co_name
        # "mode" is either "run" or "test"
        if self.mode == "test":
            msg = f'WARNING: {f_name}: POST not allowed in test mode.'
            self.msgs.append(msg)
            return {'rc': 1}
        if self.elastic_index_rotate == 'daily':
            index_suffix = '%Y-%m-%d'
        elif self.elastic_index_rotate == 'monthly':
            index_suffix = '%Y-%m'
        else:
            msg = f'ERROR: {f_name}: Invalid index_rotate value {self.elastic_index_rotate}'
            self.msgs.append(msg)
            return {'rc': 1}
        es_index = self.elastic_index + '-' + datetime.datetime.now().strftime(index_suffix)
        doc_header = {
                    "_index": es_index,
                    "_op_type": "create"
                    }
        if time.localtime().tm_isdst:
            offset = time.altzone / 3600
        else:
            offset = time.timezone / 3600
        utc_dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
        for doc in self.elastic_docs:
            # Add doc header to each doc.
            doc.update(doc_header)
            # Add @timestamp field if not already set.
            if '@timestamp' not in doc:
                doc['@timestamp'] = utc_dt.isoformat()
        # POST to elastic.
        if self.debug:
            msg = f'DEBUG: {f_name}: POSTing to index {es_index}'
            self.msgs.append(msg)
        retry = 2
        while retry:
            try:
                bulk_results = helpers.bulk(self.es, self.elastic_docs)
                msg = f'INFO: {f_name}: {bulk_results[0]} documents POSTed successfully.'
                self.msgs.append(msg)
                rc = 0
                retry = 0
            except Exception as error:
                self.msgs.append(str(error))
                rc = 1
                retry -= 1
                if retry:
                    time.sleep(2)
                    msg = f'ERROR: {f_name}: POST failed, retrying.'
                    self.msgs.append(msg)
        # Empty list of collected docs
        self.elastic_docs = []
        return {'rc': rc}
