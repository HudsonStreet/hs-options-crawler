import urllib.request
import json
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

frontrow = [
    'RowID', 'Date', '买量', '买价bid', '最新价last', '卖价ask', '卖量', '振幅%change', '涨跌幅change',
    '行权strike', '买量', '买价', '最新价', '卖价', '卖量', '振幅', '涨跌幅', '行权'
]


def match_twins(month: int):
    prefix = 'http://hq.sinajs.cn/list=OP_'
    # suffix = '_51005017' 
    suffix = '_510050'
    url1 = f'{prefix}UP{suffix}{str(month)}'
    url2 = f'{prefix}DOWN{suffix}{str(month)}'
    return (get_paried_urls([url1, url2]))


def get_paried_urls(twin_list: list) -> list:
    urls = []
    paired_url = []
    for url in twin_list:
        content = urllib.request.urlopen(url, None).read().decode('GBK')
        paired_url.append(get_all_name(content))
    return (re_pair(paired_url))


def get_all_name(content) -> list:
    quo_pos = content.find('"')
    seg = content[quo_pos + 1:-3]
    stock_list = seg.split(',')
    return stock_list[:-1]


def re_pair(li) -> list:
    finished_pair = []
    for i in range(len(li[0])):
        middle_pair = []
        middle_pair.append(li[0][i])
        middle_pair.append(li[1][i])
        finished_pair.append(middle_pair)

    return finished_pair


# PAIR to DATA
def data_parser(double_query):
    prefix = 'http://hq.sinajs.cn/list='

    row = []
    for code in double_query:
        url = prefix + code
        data = urllib.request.urlopen(url, None).read().decode('GBK')

        eq_pos = data.find('=')
        params_seg = data[eq_pos + 2:-3]
        params = params_seg.split(',')
        row.extend(params[0:8])
    return (row)


"""Get option expire dates
"""
def get_op_expire_day(date):
    url = "http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date={date}01"
    data = get(url.format(date=date)).json()['result']['data']
    return (data['expireDay'])


"""Get option monthes, so that we don't need a loop from 1 to 12
    Return a list of monthes, formate like: ['201904', '201905', '201906', '201909']
"""
def get_op_dates():
    url = "http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getStockName"
    dates = get(url).json()['result']['data']['contractMonth']
    return [''.join(i.split('-')) for i in dates][1:]


# Writing to CSV
with open('sing_stock_data.csv', 'w', newline='') as csvfile:
    fcntl.flock(csvfile.fileno(), fcntl.LOCK_EX) #Add write lock here
    start_time = datetime.datetime.now()
    print('Lock the file to write at {start_time}'.format(start_time=start_time))
    
    writer = csv.writer(csvfile, delimiter=',')
    op_contract_month = get_op_dates()
    print('Contract monthes: {monthes}'.format(monthes=op_contract_month))
    
    for current_contract_month in op_contract_month:
        date = get_op_expire_day(current_contract_month)

        for pairs in match_twins(current_contract_month[2:]):
            target_date = date
            op_item_within_strike = data_parser(pairs)
            rowId = str(target_date) + '-' + str(op_item_within_strike[7]) #Use date+strike as rowId\
            writer.writerow([rowId] + [target_date] + op_item_within_strike)
        print(f'done with data from month {current_contract_month[4:]}')
end_time = datetime.datetime.now()
print('Relase the lock at {end_time}, the program takes: {runtime} sec'.format(end_time=end_time, runtime=(end_time-start_time).seconds))