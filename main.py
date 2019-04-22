import urllib.request
import csv
import datetime
from requests import get
import fcntl

# expireDate
# http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date=201706
# frontrow = [
#     'Date', 'ExpireDate', 'OptionType', 'Strike', 'Contract Name', 'Last',
#     'Bid', 'Ask', 'Change', '%Change', 'Volume', 'OpenInterest',
#     'ImpliedVolatility', 'UnderlyingPrice'
# ]

SINA_GET_STOCK_NAME = 'http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getStockName'
SINA_GET_REMAINDER_DAY = 'http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay'
SINA_JS_URL = 'http://hq.sinajs.cn/list='

# Following constant is not used anywhere, commented for now
# frontrow = [
#     'RowID', 'Date', '买量', '买价bid', '最新价last', '卖价ask', '卖量', '振幅%change', '涨跌幅change',
#     '行权strike', '买量', '买价', '最新价', '卖价', '卖量', '振幅', '涨跌幅', '行权'
# ]

# TODO (chengcheng): For function match_twins, _get_paired_urls, _get_all_names, re_pair, etc.
# We may need more details about the functionality in the doc, better with some examples,
# or even better, giving more meaningful names.


def _match_twins(year_month):
    suffix = '_510050'
    up_url = f'{SINA_JS_URL}OP_UP{suffix}{year_month}'
    down_url = f'{SINA_JS_URL}OP_DOWN{suffix}{year_month}'
    return _get_paired_urls([up_url, down_url])


def _get_paired_urls(twin_url_list: list) -> list:
    paired_stock_names = []
    for url in twin_url_list:
        content = urllib.request.urlopen(url, None).read().decode('GBK')
        paired_stock_names.append(_get_all_names(content))
    return _re_pair_stocks(paired_stock_names)


def _get_all_names(content) -> list:
    content_start_position = content.find('"') + 1
    stock_content = content[content_start_position:-3]
    stock_names = stock_content.split(',')[:-1]
    return stock_names


def _re_pair_stocks(paired_urls) -> list:
    finished_pair = []
    for index, item in enumerate(paired_urls[0]):
        finished_pair.append([item, paired_urls[1][index]])
    return finished_pair


def data_parser(double_query):
    row = []
    for code in double_query:
        url = SINA_JS_URL + code
        data = urllib.request.urlopen(url, None).read().decode('GBK')

        params_start_position = data.find('=') + 2
        params_seg = data[params_start_position:-3]
        params = params_seg.split(',')
        row.extend(params[0:8])
    return row


def _get_option_expiration_day(contract_month):
    """
    Get option expiration dates
    :param string contract_month: string form like '201904'
    Example returned from sina API for '20190401':
    {
        "result": {
            "status": {
                "code": 0
            },
            "data": {
                "expireDay": "2019-04-24",
                "remainderDays": 2,
                "stockId": "510050",
                "cateId": "510050C1904",
                "zhulikanzhang": "",
                "zhulikandie": ""
            }
        }
    }
    Return format from this function: '2019-04-24'
    :return: string
    """
    contract_date = '?date={month}01'.format(month=contract_month)
    expiration_date = get(SINA_GET_REMAINDER_DAY + contract_date).json()['result']['data']['expireDay']
    return expiration_date


def _get_option_contract_months():
    """
    Get option months, so that we don't need a loop from 1 to 12
    Example returned from sina API:
    {
        "result": {
            "status": {
                "code": 0
            },
            "data": {
                "cateList": ["50ETF","50ETF"],
                "contractMonth": ["2019-04","2019-04","2019-05","2019-06","2019-09"],
                "stockId":"510050",
                "cateId":"510050C1906A02350"
            }
        }
    }
    Return format from this function: ['201904', '201905', '201906', '201909']
    :return: list
    """
    dates = get(SINA_GET_STOCK_NAME).json()['result']['data']['contractMonth']
    return [''.join(i.split('-')) for i in dates[1:]]


def write_data_to_csv():
    """
    Main entry of the crawler
    TODO: consider how do we want to run this? One-time, cron or service?
    :return: n/a
    """
    start_time = datetime.datetime.now()
    with open('sina_stock_data.csv', 'w', newline='') as target_csv:
        fcntl.flock(target_csv.fileno(), fcntl.LOCK_EX)  # Add write lock here
        print(f'Lock the file to write at {start_time}')

        writer = csv.writer(target_csv, delimiter=',')
        option_contract_months = _get_option_contract_months()
        print(f'Contract months: {option_contract_months}')

        for contract_month in option_contract_months:
            expiration_date = _get_option_expiration_day(contract_month)

            print(f'Start writing data for month {contract_month[4:]}')
            for pairs in _match_twins(contract_month[2:]):
                option_item_within_strike = data_parser(pairs)
                row_id = expiration_date + '-' + str(option_item_within_strike[7])  # date + strike as row_id
                writer.writerow([row_id] + [expiration_date] + option_item_within_strike)
            print(f'Done with data for month {contract_month[4:]}')

    end_time = datetime.datetime.now()
    print('Release the lock at {end_time}, the program takes: {runtime} sec'.format(
        end_time=end_time,
        runtime=(end_time - start_time).seconds)
    )


if __name__ == '__main__':
    write_data_to_csv()
