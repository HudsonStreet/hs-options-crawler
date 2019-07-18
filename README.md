# HS Options Crawler
> HS stock options crawler with CSV output 新浪期权数据爬虫

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)
<a href="https://996.icu"><img src="https://img.shields.io/badge/link-996.icu-red.svg" alt="996.icu"></a>

## Requirement
* python 3.6+

## Installation
```
git clone https://github.com/HudsonStreet/sina-stock-crawler.git && cd sina-stock-crawler 
```

## Run
Make sure you have python3 installed and execute the `main.py` with
```
python3 main.py
```
![](https://user-images.githubusercontent.com/19645990/30264451-b5f1b04a-96a6-11e7-9400-4f139714e016.png)

Depends on you network, it might take up to a few minutes, be patient.

## Output file
After crawling, you will get a CSV file named `sina_stock_data.csv` with columns:

'RowID', 'Date', '买量', '买价bid', '最新价last', '卖价ask', '卖量', '振幅%change', '涨跌幅change','行权strike', '买量', '买价', '最新价', '卖价', '卖量', '振幅', '涨跌幅'

![](https://github.com/HudsonStreet/sina-stock-crawler/blob/master/screenshots/screen_shot_HS.jpg?raw=true)
![](https://github.com/HudsonStreet/sina-stock-crawler/blob/master/screenshots/HS_DATA_SAMPLE.jpg?raw=true)

## Source
[50etf Options](http://stock.finance.sina.com.cn/option/quotes.html)

## License
1. MIT
2. Under the Anti 996 License. See the [Anti 996 LICENSE file](https://github.com/HudsonStreet/sina-stock-crawler/blob/master/LICENSE_996) for details.
