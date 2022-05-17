import random
import logging

logger = logging.getLogger(__name__)
# Collector must contain collect_data function.
# collect_data() must return a list of documents (dictionaries) to be posted to elastic.
def collect_data(config_data):
    docs = []
    doc = {'beat': config_data.get('name'), 'inventory_hostname': config_data.get('hostname')}
    docs.append(doc)
    logger.info(f"docs: {docs}")
    return docs

if __name__ == '__main__':
    # Use this config_data when running directly
    config_data = {'beat_name': 'test', 'hostname': 'ukgrnfab1'}
    docs = collect_data(config_data)
    print(docs)