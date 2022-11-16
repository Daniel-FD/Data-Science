# https://medium.com/@skalyani103/python-on-aws-lambda-using-docker-images-5740664c54ca
from functions_ePrices import query_prices_and_save_to_db, today_tomorrow_str_dates
import pandas as pd
country_code = 'ES'
yesterday_str, tomorrow_str = today_tomorrow_str_dates()
start = pd.Timestamp(yesterday_str, tz='Europe/Brussels')
end = pd.Timestamp(tomorrow_str, tz='Europe/Brussels')
query_prices_and_save_to_db(start, end, country_code)