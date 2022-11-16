from datetime import date, datetime, timedelta
from uuid import uuid4

import config
import pandas as pd
import seaborn as sns
import sqlalchemy
from entsoe import EntsoePandasClient
from sqlalchemy import create_engine
from sqlalchemy.types import BIGINT, DATETIME, FLOAT, INTEGER, VARCHAR
# 
# REQUIREMENTS
# API
API_KEY = config.API_KEY
# AWS
HOST = config.HOST
USER = config.USER
PASSWORD = config.PASSWORD
DATABASE = config.DATABASE
PORT = config.PORT

def query_prices_and_save_to_db(start, end, country_code, save_to_path = False):
    # 
    df_prices = query_electrical_prices(start, end, country_code, save_to_path = False)
    save_prices_to_db(df_prices)

# 
def query_electrical_prices(start, end, country_code, save_to_path = False):
    # 
    client = EntsoePandasClient(api_key=API_KEY)    
    prices = client.query_day_ahead_prices(country_code, start=start,end=end)
    df_prices = pd.DataFrame({'date':prices.index, 'price':prices.values})
    # 
    df_prices['date'] = pd.to_datetime(df_prices['date'])
    df_prices['country_code'] = country_code
    df_prices['unique_id'] = df_prices['date'].astype('int64') // 10**9
    df_prices['unique_id'] = str(country_code) + df_prices['unique_id'].astype(str)
    df_prices.set_index('unique_id',inplace=True)
    # 
    if save_to_path == True:
        df_prices.to_csv('prices.csv')
    # 
    return df_prices

def save_prices_to_db(df_prices):
    # 
    col_options = dict(
        dtype={
            'unique_id': sqlalchemy.types.VARCHAR(length=25),
            'date': sqlalchemy.types.DATETIME(),
            'price': sqlalchemy.types.FLOAT,
            'country_code': sqlalchemy.types.VARCHAR(length=25)
        }
    )
    table_name = 'prices-table'
    index_name = 'unique_id'
    # 
    db_connection_str = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}'
    connection = create_engine(db_connection_str)
    try:
        df_prices.to_sql(name=table_name, con=connection, if_exists = 'append', index=True, index_label=index_name, **col_options)
        with connection.connect() as con:
            con.execute('ALTER TABLE `' + str(table_name) + '` ADD PRIMARY KEY (`'+ str(index_name) + '`);')
    except Exception as e:
        print(e)
        for i in range(len(df_prices)):
            try:
                df_prices.iloc[i:i+1].to_sql(name=table_name, con=connection, if_exists = 'append')
            except Exception as e:
                print(i, e)
                pass
    
    return("Prices were saved (attemped) in RDS database")
    
def today_tomorrow_str_dates():
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    # 
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y%m%d')
    # 
    return yesterday_str, tomorrow_str