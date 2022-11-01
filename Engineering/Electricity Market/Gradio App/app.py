import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import gradio as gr

list_of_EIC_codes = ["10Y1001A1001A46L","10YDK-1--------W","10YES-REE------0","10YFR-RTE------C"]


def plot_e_pricing(EIC_code,start_date,end_date,tomorrow_rate):
    # 
    # 
    if tomorrow_rate == True:
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        now = now.replace(microsecond=0).isoformat() + 'Z'
        tomorrow = tomorrow.replace(microsecond=0).isoformat() + 'Z'
        # 
        start_date = now
        end_date = tomorrow
    # 
    url = "https://electri.p.rapidapi.com/api/v1/day-ahead-prices"
    querystring = {"to":end_date,"from":start_date,"eic":EIC_code}
    headers = {
      "X-RapidAPI-Key": "7ad267cb53mshf4f5255c38f192ap19f964jsnc7abc0be43eb",
      "X-RapidAPI-Host": "electri.p.rapidapi.com"
    }
    data = requests.request("GET", url, headers=headers, params=querystring).json()
    df = pd.json_normalize(data['data']['series'])
    df['time'] = pd.to_datetime(df['time'])
    # 
    df_metadata = pd.json_normalize(data)
    currency = df_metadata['data.currency'].iloc[0]
    power_unit = df_metadata['data.unit'].iloc[0]
    eic = df_metadata['data.eic'].iloc[0]
    # 
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df['time'], df['price']);
    plt.title('Electrical prices '+ str(eic))
    plt.xlabel('Time')
    plt.ylabel('Price [' + str(currency) + '/' + str(power_unit) + ']')
    fig.autofmt_xdate()
    # 
    # 
    return fig


inputs = [
    gr.Dropdown(list_of_EIC_codes, label="Electrical Provider EIC"),
    gr.Textbox(label="Start Date [YYYY-MM-DDTHH:MMZ]"),
    gr.Textbox(label="End Date [YYYY-MM-DDTHH:MMZ]"),
    gr.Checkbox(label="Tomorrow's rates?",default='False'),
]
outputs = gr.Plot()

demo = gr.Interface(
    fn=plot_e_pricing,
    inputs=inputs,
    outputs=outputs,
    examples=[
        ["10Y1001A1001A46L","2022-04-05T22:00Z","2022-05-05T22:00Z",False],
        ["10YDK-1--------W","2022-08-05T22:00Z","2022-08-06T22:00Z",False],
        ["10YDK-1--------W"," "," ",True],

    ],
    cache_examples=True,
)

if __name__ == "__main__":
    demo.launch()

# Requirements
# pipreqs .