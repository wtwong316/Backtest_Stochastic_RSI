from elasticsearch_dsl import connections
import elasticsearch
import json
import os
import sys
import threading


class HLClient:
    __conn = None
    __conn_lock = threading.Lock()

    @staticmethod
    def get_instance():
        if HLClient.__conn is None:
            with HLClient.__conn_lock:
                if HLClient.__conn is None:
                    HLClient.__conn = \
                        connections.create_connection('hlclient', hosts=['localhost'], port=9200)
        return HLClient.__conn

    def __init__(self):
        raise Exception("This class is a singleton!, use static method getInstance()")


def delete_index(target_index):
    hl_es = HLClient.get_instance()
    exist = hl_es.indices.exists(target_index)

    if exist:
        hl_es.indices.delete(target_index)


def indexing_array(target_index, ar):
    hl_es = HLClient.get_instance()
    exist = hl_es.indices.exists(target_index)

    if not exist:
        root_dir = os.path.abspath(os.curdir)
        file_path = root_dir + '/indicator_mappings.json'
        response = None
        with open(file_path) as f:
            mappings = json.load(f)
            try:
                response = hl_es.indices.create(target_index, body=mappings)
            except elasticsearch.ElasticsearchException as es1:
                print(es1.__cause__)
                sys.exit(-1)

    try:
        response = hl_es.bulk(rec_to_actions(target_index, ar))
    except elasticsearch.ElasticsearchException as es1:
            print(es1.__cause__)

    return response


def rec_to_actions(index, ar):
    import json
    for record in ar:
        yield ('{ "index" : { "_index" : "%s"}}' % (index))
        yield (json.dumps(record, default=int))


if __name__ == "__main__":
    test3 = HLClient.get_instance()
    print("test3", hex(id(test3)))

