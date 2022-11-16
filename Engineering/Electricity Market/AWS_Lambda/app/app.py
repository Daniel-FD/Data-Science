from functions_ePrices import query_prices_and_save_to_db, today_tomorrow_str_dates
import pandas as pd
import json

country_code = 'ES'

def lambda_handler(event, context):
    # 
    yesterday_str, tomorrow_str = today_tomorrow_str_dates()
    start = pd.Timestamp(yesterday_str, tz='Europe/Brussels')
    end = pd.Timestamp(tomorrow_str, tz='Europe/Brussels')
    query_prices_and_save_to_db(start, end, country_code)
    #
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
