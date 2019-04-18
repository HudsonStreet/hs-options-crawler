import urllib.request
import json
import csv
import datetime
from requests import get

##Date format
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


def get_op_expire_day(date):
    url = "http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date={date}01"
    data = get(url.format(date=date)).json()['result']['data']
    return (data['expireDay'])


# Writing to CSV
with open('sing_stock_data.csv', 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    rows = csv.DictReader(csvfile)
    for row in rows:
        print(row)
    #TODO(jinsiang): add prints into logs
    print('started checking and saving data, it might take a few minutes') 
    for i in range(12):
        date_string = ''.join(
            (datetime.date.today() +
             datetime.timedelta(i * 365 / 12)).isoformat().split('-'))
        date = get_op_expire_day(date_string[:6])

        if len(match_twins(date_string[2:6])) == 0:
            print(f'no data found in {date_string[4:6]} 月')
        else:
            print(f'found data from {date_string[4:6]} 月, start checking and saving')
        for pairs in match_twins(date_string[2:6]):
            target_date = date
            op_item_within_strike = data_parser(pairs)
            rowId = str(target_date) + '-' + str(op_item_within_strike[7]) #Use date+strike as rowId\
            
            #TODO(jinsiang): Check the row entry before write, if value(op_item_within_strike) no change, goto next, else modify
            writer.writerow([rowId] + [target_date] + op_item_within_strike)
        print(f'done with data from month {date_string[4:6]}')
