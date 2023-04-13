import pandas as pd
import config
from pyairtable import Api, Base, Table
from pyairtable.formulas import match

def obtain_crm_link_from_airtable(uniqueID):
    table_name = 'Intro_Forms'
    table = Table(config.AIRTABLE_API_KEY, config.BASE_ID, table_name)
    formula = match({"Form_Unique_ID": uniqueID})
    record = table.first(formula=formula)
    crm_link = record['fields']['CRM_Customer_Link']
    return crm_link

def obtain_dear_link_from_airtable(uniqueID):
    table_name = 'DEAR_Order_Bespoke'
    table = Table(config.AIRTABLE_API_KEY, config.BASE_ID, table_name)
    formula = match({"Form_Unique_ID": uniqueID})
    record = table.first(formula=formula)
    dear_link = record['fields']['Order_URL']
    return dear_link