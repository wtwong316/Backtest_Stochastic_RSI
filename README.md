# Backtest_RSI
Materials for the article "Wow! Backtest RSI Crossover Strategy in Elasticsearch" in Medium
(https://wtwong316.medium.com/the-more-signals-the-better-stochastic-rsi-vs-rsi-b0740a17c584)

The following steps have been tested with Elasticsearch Server v7.10.1

1. Create an index, fidelity24_fund and the corresponding data are populated. The data for the index, fidelity24_fund, is coming from IEX (Investors Exchange) with the 24 Fidelity commission-free ETFs selected for demo purpose. The time range picked is between 2021-01-01 and 2021-09-30.

$./fidelity24_index.sh

2. Assume you have installed python 3.7, run the following command to go to virtual environment and prepare the python packages needed.

$source venv/bin/activate

$pip install -r requirements.txt

3. After the indice, fidelity24_fund, is created and the data are populated, run the following command to compute different types of RSI and indexing into the given index, for example "indicators".

$./index_srsi.sh -i fidelity24_fund -b 2021-05-01 -e 2021-09-30 -o indicators

4. Perform the backtest for each RSI type of trading strategy include Stochastic RSI, Wilder's RSI and SMA RSI. Specify the parameter of the crossover values for your choice.

$./backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t srsi -u 0.8 -l 0.2

$./backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t msrsi -u 0.8 -l 0.2

$./backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t rsi -u 70 -l 30

$./backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t smarsi -u 70 -l 30

5.  The report will be shown as the following for the statistics.
$ ./backtest_srsi.sh -i indicators -s 2021-05-01 -e 2021-09-30 -t srsi -u 0.8 -l 0.2
</br>
input_index: 'indicators', start_date: '2021-05-01', end_date: '2021-09-30', type: 'srsi', high mark: '0.80', low mark '0.20'</br>
Balance sheet : </br>
------------------------------------------------------------------------------------------</br>
['date:2021-05-03, symbol: FBCG, rsi: 0.000, close: 30.740 buy a share, num_of_trades: 1 ',</br>
 'date:2021-05-03, symbol: FENY, srsi: 0.938, close: 13.700 no share, not sell',</br>
 ……</br>
'date: 2021-05-07, symbol: FCPI, buy: 28.640, close: 29.220, rsi: 1.000, share: 1, profit: 0.580, win: 1, loss: 0, total profit: 0.580',</br>
 ……</br>
'date: 2021-09-10, symbol: ONEQ, buy: 58.820, close: 56.180, share: 1, trade: -2.64 profit: -2.60',</br>
 'symbol: ONEQ, num_of_trade: 4, win: 2, loss: 2, total profit: -2.600, benchmark_profit: 0.041']</br>
------------------------------------------------------------------------------------------</br>
