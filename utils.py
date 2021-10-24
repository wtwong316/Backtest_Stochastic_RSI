import requests
import json
import sys
from datetime import datetime, timedelta

iex_date_pattern = '%Y-%m-%d'
get_symbols_file = 'get_symbols.json'
get_srsi_file = 'get_srsi.json'
get_srsi_signal_file = 'get_srsi_signal.json'
get_benchmark_data_file = 'get_benchmark_data.json'
data_prep_day = 100


# get symbols from input index
def get_symbols(input_index, start_date, end_date):
    resp = get_symbol_data(input_index, start_date, end_date)
    if resp is None:
        return None
    else:
        result = json.loads(resp)
        if "status" in result:
            print("Return status: %s, error: %s" % (result['status'], result['error']))
            sys.exit(-1)
        buckets = result['aggregations']['symbols']['buckets']
        symbols = []
        for bucket in buckets:
            symbols.append(bucket['key'])
        return symbols


# get data from elasticsearch server
def get_symbol_data(input_index, start_date, end_date):
    url = 'http://localhost:9200/{}/_search?pretty'.format(input_index)
    with open(get_symbols_file) as f:
        payload = json.load(f)
    payload_json = json.dumps(payload)
    start_datetime = datetime.strptime(start_date, iex_date_pattern)
    new_start_datetime = start_datetime - timedelta(days=data_prep_day)
    new_start_date = new_start_datetime.strftime(iex_date_pattern)
    payload_json = payload_json % (new_start_date, end_date)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload_json, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return None


def get_srsi_data(input_index, start_date, end_date, symbol):
    url = 'http://localhost:9200/{}/_search?pretty'.format(input_index)
    with open(get_srsi_file) as f:
        payload = json.load(f)
    payload_json = json.dumps(payload)
    start_datetime = datetime.strptime(start_date, iex_date_pattern)
    new_start_datetime = start_datetime - timedelta(data_prep_day)
    new_start_date = new_start_datetime.strftime(iex_date_pattern)
    payload_json = payload_json % (new_start_date, end_date, symbol, start_date)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload_json, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return None


def get_signal_data(input_index, start_date, end_date, rsi_type, hwm, lwm):
    url = 'http://localhost:9200/{}/_search?pretty'.format(input_index)
    if rsi_type in ['rsi', 'srsi', 'msrsi', 'smarsi']:
        file_name = get_srsi_signal_file
    else:
        print("Invalid rsi type %s" % rsi_type)
        sys.exit(-1)
    with open(file_name) as f:
        payload = json.load(f)
    payload_json = json.dumps(payload)
    payload_json = payload_json % (start_date, end_date, rsi_type, hwm, rsi_type, lwm)
    new_payload_json = payload_json.replace("\"%s\""%hwm, "%s"%hwm).replace("\"%s\""%lwm, "%s"%lwm)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=new_payload_json, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return None


def get_benchmark(input_index, start_date, end_date, symbol):
    resp = get_benchmark_data(input_index, start_date, end_date, symbol)
    if resp is None:
        return None
    else:
        result = json.loads(resp)
        if "status" in result:
            print("Return status: %s, error: %s" % (result['status'], result['error']))
            sys.exit(-1)
        buckets = result['aggregations']['benchmark']['buckets']
        benchmark = dict()
        for bucket in buckets:
            benchmark['symbol'] = symbol
            benchmark['Close'] = bucket['Close']
            benchmark['CSum_DClose'] = bucket['CSum_DClose']

        if len(buckets) == 1:
            return buckets[0]
        else:
            return None


def get_benchmark_data(input_index, start_date, end_date, symbol):
    url = 'http://localhost:9200/{}/_search?pretty'.format(input_index)
    with open(get_benchmark_data_file) as f:
        payload = json.load(f)
    end_epoch_milli = int(datetime.strptime(end_date, iex_date_pattern).timestamp() * 1000)
    payload_json = json.dumps(payload)
    payload_json = payload_json % (start_date, end_date, symbol, end_epoch_milli)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload_json, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return None
