import datetime
import pandas as pd
import requests
from google.cloud import bigquery

bigquery_client = bigquery.Client.from_service_account_json('google-auth-key.json')
dataset_id = 'bitmex_trades'


def fetch_and_save_all_trades(symbol: str):
    latest = get_latest_trade_from_bigquery(symbol)
    is_continue = True
    while is_continue:
        stack_trades = []
        for i in range(0, 10):
            trades = fetch_trades_from_bitmex(symbol, latest, None, 1000)
            stack_trades += trades
            print(
                f'fetch trades from Bitmex. result.latest: {latest}, result.length: {len(trades)}, stackTrades.length: {len(stack_trades)}')
            trades_len = len(trades)
            if trades_len > 0:
                latest = trades[-1]["timestamp"]
                if trades_len < 1000:
                    is_continue = False
                    break
            else:
                return
        data_frame = {}
        keys = stack_trades[0].keys()
        for key in keys:
            data_frame[key] = [trade[key] for trade in stack_trades]
        df = pd.DataFrame(
            data_frame,
            columns=keys)
        filename = f'sources/temp/bitmex-{symbol}-{stack_trades[0]["timestamp"]}.csv'
        df.to_csv(filename, index=None, header=True)
        upload_to_bigquery(symbol, filename)


def fetch_trades_from_bitmex(symbol: str, after: datetime = None, before: datetime = None, limit: int = None):
    response = requests.get('https://www.bitmex.com/api/v1/trade',
                            params={
                                'symbol': symbol,
                                'reverse': "false",
                                'startTime': after,
                                'endTime': before,
                                'count': limit})
    trades = response.json()
    return trades


def upload_to_bigquery(symbol: str, filename: str):
    table_ref = bigquery_client.dataset(dataset_id).table(symbol)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.autodetect = True

    with open(filename, "rb") as source_file:
        job = bigquery_client.load_table_from_file(source_file, table_ref, job_config=job_config)

    job.result()  # Waits for table load to complete.
    print("Loaded {} rows into Bigquery {}:{}.".format(job.output_rows, dataset_id, symbol))


def get_latest_trade_from_bigquery(symbol: str):
    try:
        query = (
            f'SELECT timestamp FROM `bitmex_trades.{symbol}` WHERE symbol = "{symbol}" ORDER BY timestamp DESC LIMIT 1'
        )
        trades = bigquery_client.query(query)
        for trade in trades:
            return trade['timestamp']
    except Exception as e:
        print(e)
        print('Ignored if the destination table is exist but empty.')
        return None
    return None


fetch_and_save_all_trades('XBTH18')
