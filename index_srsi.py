import json
import sys, getopt

from hlclient import indexing_array, delete_index
from utils import get_symbols, get_srsi_data


# get the command line parameters for the trading policy and the ticker symbol
def get_opt(argv):
    input_index = ''
    start_date = ''
    end_date = ''
    output_index = ''

    try:
        opts, args = getopt.getopt(argv, "hi:b:e:o:")
    except getopt.GetoptError:
        print('index_srsi -i <input_index> -b <start date> -e <end date> -o <output_index>')
        print('example: index_srsi.sh -i fidelity24_fund -b 2021-05-01 -e 2021-09-30 -o indicators')
        sys.exit(-1)

    for opt, arg in opts:
        if opt == '-h':
            print('index_srsi -i <input_index>-b <start date> -e <end date> -o <output_index>')
            print('example: index_srsi.sh -i fidelity24_fund -b 2021-05-01 -e 2021-09-30 -o indicators')
            sys.exit(0)
        elif opt == '-i':
            input_index = arg
        elif opt == '-b':
            start_date = arg
        elif opt == '-e':
            end_date = arg
        elif opt == '-o':
            output_index = arg
        else:
            print('index_srsi -i <input_index> -f <inputfile> -b <start date> -e <end date> -o <output_index>')
            print('example: index_srsi.sh -i fidelity24_fund -b 2021-05-01 -e 2021-09-30 -o indicators')
            sys.exit(-1)

    if input_index == '' or start_date == '' or end_date == '' or output_index == '':
        print("Given value is invalid such as no input file, no start, end date or index!")
        print('index_srsi -i <input_index> -b <start date> -e <end date> -o <output_index>')
        print('example: index_srsi.sh -i fidelity24_fund -b 2021-05-01 -e 2021-09-30 -o indicators')
        sys.exit(-1)
    print("input_index: '%s', start_date: '%s', end_date: '%s', index: '%s'"
          % (input_index, start_date, end_date, output_index))
    return input_index, start_date, end_date, output_index


# parse the response data and refine the buy/sell signal
def parse_data(resp, start_date, symbol):
    result = json.loads(resp)
    if "status" in result:
        print("Return status: %s, error: %s" % (result['status'], result['error']))
        sys.exit(-1)
    aggregations = result['aggregations']
    if aggregations and 'Backtest_SRSI' in aggregations:
        backtest_srsi = aggregations['Backtest_SRSI']

    transactions = []
    if backtest_srsi and 'buckets' in backtest_srsi:
        for bucket in backtest_srsi['buckets']:
            transaction = dict()
            transaction['symbol'] = symbol
            transaction['date'] = bucket['key_as_string']
            transaction['close'] = bucket['Close']['value']
            transaction['rsi'] = bucket['RSI']['value']
            transaction['srsi'] = bucket['SRSI']['value']
            if transaction['date'] >= start_date:
                transaction['smarsi'] = bucket['SMARSI']['value']
                transaction['msrsi'] = bucket['MSRSI']['value']
                transactions.append(transaction)

    return transactions


def main(argv):
    input_index, start_date, end_date, output_index = get_opt(argv)
    symbols = get_symbols(input_index, start_date, end_date)
    if symbols is None:
        print('No symbols returned')
        sys.exit(-1)
    delete_index(output_index)
    for symbol in symbols:
        resp = get_srsi_data(input_index, start_date, end_date, symbol)
        transactions = parse_data(resp, start_date, symbol)
        indexing_array(output_index, transactions)


if __name__ == '__main__':
    main(sys.argv[1:])
