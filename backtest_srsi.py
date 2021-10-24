import json
import sys, getopt
from pprint import pprint

from utils import get_symbols, get_benchmark, get_signal_data


# get the command line parameters for the trading policy and the ticker symbol
def get_opt(argv):
    input_index = ''
    start_date = ''
    end_date = ''
    hwm = 0.8
    lwm = 0.2
    rsi_type = 'srsi'
    try:
        opts, args = getopt.getopt(argv, "hi:s:e:t:u:l:")
    except getopt.GetoptError:
        print('invalid argument: -i <input index> -s <start date> -e <end date> -t <rsi type> '
              '-u <rsi high mark> -l <rsi lower mark>')
        print('example: backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t <srsi or rsi> '
              '-u <0.8 or 70> -l <0.2 or 30>')
        sys.exit(-1)

    for opt, arg in opts:
        if opt == '-h':
            print('invalid argument: -i <input index> -s <start date> -e <end date> -t <rsi type> '
              '-u <rsi high mark> -l <rsi lower mark>')
            print('example: backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t <srsi or rsi> '
                  '-u <0.8 or 70> -l <0.2 or 30>')
            sys.exit(0)
        elif opt == '-i':
            input_index = arg
        elif opt == '-s':
            start_date = arg
        elif opt == '-e':
            end_date = arg
        elif opt == '-t':
            rsi_type = arg
        elif opt == '-u':
            hwm = float(arg)
        elif opt == '-l':
            lwm = float(arg)
        else:
            print('invalid argument: -i <input index> -s <start date> -e <end date> -t <rsi type> '
              '-u <rsi high mark> -l <rsi lower mark>')
            print('example: backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t <srsi or rsi> '
                  '-u <0.8 or 70> -l <0.2 or 30>')
            sys.exit(0)

    if input_index == '' or start_date == '' or end_date == '':
        print("Given value is invalid such as no input index, no start or end date!")
        print('invalid argument: -i <input index> -s <start date> -e <end date> -t <rsi type> '
              '-u <rsi high mark> -l <rsi lower mark>')
        print('example: backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t <srsi or rsi> '
              '-u <0.8 or 70> -l <0.2 or 30>')
        sys.exit(-1)
    print("input_index: '%s', start_date: '%s', end_date: '%s', type: '%s', high mark: '%.2f', low mark '%.2f'"
          % (input_index, start_date, end_date, rsi_type, hwm, lwm))
    return input_index, start_date, end_date, rsi_type, hwm, lwm


# parse the response data and process the buy/sell signal
def process_data(resp, entries, rsi_type, hwm, lwm, balance_sheet):
    result = json.loads(resp)
    if "status" in result:
        print("Return status: %s, error: %s" % (result['status'], result['error']))
        sys.exit(-1)

    if result['hits']['total']['value'] > 0:
        hits = result['hits']['hits']
        for hit in hits:
            entry = entries[hit['_source']['symbol']]
            if hit['_source'][rsi_type] > hwm:
                if entry['share'] > 0:
                    entry['date'] = hit['_source']['date']
                    entry[rsi_type] = hit['_source'][rsi_type]
                    entry['close'] = hit['_source']['close']
                    trade = (entry['close'] - entry['buy']) * entry['share']
                    if trade > 0:
                        entry['num_of_win'] += 1
                    else:
                        entry['num_of_loss'] += 1
                    entry['profit'] += trade
                    balance_sheet.append("date: %s, symbol: %s, buy: %.3f, close: %.3f, rsi: %.3f, "
                                         "share: %d, profit: %.3f, win: %d, loss: %d, total profit: %.3f"
                                         % (entry['date'], entry['symbol'], entry['buy'], entry['close'],
                                            entry[rsi_type], entry['share'], trade, entry['num_of_win'],
                                            entry['num_of_loss'], entry['profit']))
                    entry['share'] = 0
                    entry['buy'] = 0
                else:
                    balance_sheet.append("date:%s, symbol: %s, %s: %.3f, close: %.3f no share, not sell"
                                         % (hit['_source']['date'], hit['_source']['symbol'], rsi_type,
                                            hit['_source'][rsi_type], hit['_source']['close']))

            elif hit['_source'][rsi_type] < lwm:
                if entry['share'] == 0:
                    entry['date'] = hit['_source']['date']
                    entry['rsi'] = hit['_source']['rsi']
                    entry['buy'] = hit['_source']['close']
                    entry['share'] = 1
                    entry['num_of_trade'] += 1
                    balance_sheet.append("date:%s, symbol: %s, rsi: %.3f, close: %.3f buy a share, num_of_trades: %d "
                                         % (hit['_source']['date'], hit['_source']['symbol'], hit['_source'][rsi_type],
                                            hit['_source']['close'], entry['num_of_trade']))
                else:
                    balance_sheet.append("date:%s, symbol: %s, rsi: %.3f, close: %.3f hold a share, not buy"
                                         % (hit['_source']['date'], hit['_source']['symbol'], hit['_source'][rsi_type],
                                            hit['_source']['close']))


def initialize(symbols, rsi_type, value):
    entries = dict()
    for symbol in symbols:
        entries[symbol] = dict()
        entries[symbol]['symbol'] = symbol
        entries[symbol]['buy'] = 0.0
        entries[symbol]['profit'] = 0.0
        entries[symbol]['date'] = '0000-00-00'
        entries[symbol][rsi_type] = value
        entries[symbol]['share'] = 0
        entries[symbol]['num_of_trade'] = 0
        entries[symbol]['num_of_win'] = 0
        entries[symbol]['num_of_loss'] = 0
    return entries


def finalize(input_index, start_date, end_date, entries, balance_sheet):
    for key in entries:
        entry = entries[key]
        data = get_benchmark(input_index, start_date, end_date, entry['symbol'])
        if data is None:
            print("get_benchmark(%s, %s, %s, %s) got failure"
                  % (input_index, start_date, end_date, entry['symbol']))
            sys.exit(-1)
        if entry['share'] > 0:
            trade = (data['Close']['value'] - entry['buy']) * entry['share']
            if trade > 0:
                entry['num_of_win'] += 1
            else:
                entry['num_of_loss'] += 1
            entry['profit'] += trade
            balance_sheet.append("date: %s, symbol: %s, buy: %.3f, close: %.3f, "
                "share: %d, trade: %.2f profit: %.2f"
            % (entry['date'], entry['symbol'], entry['buy'], data['Close']['value'],
               entry['share'], trade, entry['profit']))

        entry['benchmark_profit'] = data['CSum_DClose']['value']
        balance_sheet.append("symbol: %s, num_of_trade: %d, win: %d, loss: %d, total profit: %.3f, benchmark_profit: %.3f"
                             % (entry['symbol'], entry['num_of_trade'],
                                entry['num_of_win'], entry['num_of_loss'],
                                entry['profit'], entry['benchmark_profit']))


def print_balance_sheet(balance_sheet):
    print('Balance sheet : ')
    print('-' * 80)
    pprint(balance_sheet, width=120)
    print('-' * 80)
    print()


def main(argv):
    input_index, start_date, end_date, rsi_type, hwm, lwm = get_opt(argv)
    symbols = get_symbols(input_index, start_date, end_date)
    if symbols is None:
        print('No symbols returned')
        sys.exit(-1)
    balance_sheet = []
    entries = initialize(symbols, rsi_type, (hwm+lwm)/2)
    resp = get_signal_data(input_index, start_date, end_date, rsi_type, hwm, lwm)
    process_data(resp, entries, rsi_type, hwm, lwm, balance_sheet)
    finalize(input_index, start_date, end_date, entries, balance_sheet)
    print_balance_sheet(balance_sheet)


if __name__ == '__main__':
    main(sys.argv[1:])
