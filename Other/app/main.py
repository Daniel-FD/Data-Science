import streamlit as st
import requests
import json
from PIL import Image
import pandas as pd

# Page title
st.set_page_config(page_title='HelpFirst AI Assistant')
st.title('HelpFirst AI Assistant')

# Text input
st.divider()
txt_input = st.text_area('Enter your case text to be analysed:', 
 '''Hi there,

This is about my neighbour. He had a stroke recently. He's only 42 but he can't use his left side now so he can't get out to top up the meter since he came home from hospital.  I put about £50 on each of them, then I had to travel up to look after my mother who is ill. 
He likes to keep the heat on because he gets very cold. When I called him today he told me that the gas and electric aren't working anymore and he can't make any food and his flat is freezing.  I don't know how long it's been off for, he didn't tell me.

Can you help him? My other neighbour gave me this email address. 

He has also requested to get access to his data.

Thanks

Katy''', 
height=200)

# Form to accept user's text input for summarization
result = []
with st.form('summarize_form', clear_on_submit=True):
    # api_key = st.text_input('Access Key', type = 'password', disabled=not txt_input)
    submitted = st.form_submit_button('Submit')
    # if submitted and api_key == 'test-key':
    if submitted:
        with st.spinner('Our AI Assistant is Analysing the Case...'):
            url = "http://risk-alert-env.eba-7umtkmkf.eu-west-2.elasticbeanstalk.com/"
            payload = json.dumps({"message": txt_input, "case_id": ''})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url + '/risk_assessor', headers=headers, data=payload)
            json_response = json.loads(response.text)
            result.append(json_response)
            # del api_key

with st.sidebar:
    def add_logo(logo_path, width, height):
        logo = Image.open(logo_path)
        modified_logo = logo.resize((width, height))
        return modified_logo
    
    my_logo = add_logo(logo_path="/Users/danielfiuzadosil/Documents/GitHub_Repo/helpfirst/risk-alert/app/.streamlit/helpfirst-logo.png", width=1115, height=220)
    st.sidebar.image(my_logo)
    my_animation = add_logo(logo_path="/Users/danielfiuzadosil/Documents/GitHub_Repo/helpfirst/risk-alert/app/.streamlit/helpfirst-animation.gif", width=1491, height=1169)
    st.sidebar.image(my_animation)
    st.write("Give vulnerable clients the priority they deserve.")
    st.markdown("1. Top priority: Stop everything")
    st.markdown("2. Today")
    st.markdown("3. Next 24 hrs - could wait till tomorrow")
    st.markdown("4. Standard")
    st.markdown("5. Low priority")
    # st.write("Trusted by:")
    # ehu_logo = add_logo(logo_path="/Users/danielfiuzadosil/Documents/GitHub_Repo/helpfirst/risk-alert/app/.streamlit/ehu-logo.png", width=292, height=161)
    # st.sidebar.image(ehu_logo)
    # civtech_logo = add_logo(logo_path="/Users/danielfiuzadosil/Documents/GitHub_Repo/helpfirst/risk-alert/app/.streamlit/civtech-logo.png", width=320, height=70)
    # st.sidebar.image(civtech_logo)



if len(result):
    st.subheader('Outputs', divider='gray')
    # WARNINGS and ACTIONS
    print("Risk_Score:", result[0]['output']['risk_score'])
    if result[0]['output']['risk_score'] == 1:
        action = "⚠️⚠️⚠️⚠️⚠️ Action: Top priority: Stop everything."
        icon = "1️⃣"
    elif result[0]['output']['risk_score'] == 2:
        action = "⚠️⚠️⚠️⚠️ Action: Today."
        icon = "2️⃣"
    elif result[0]['output']['risk_score'] == 3:
        action = "⚠️⚠️⚠️ Action: Next 24 hrs - could wait till tomorrow."
        icon = "3️⃣"
    elif result[0]['output']['risk_score'] == 4:
        action = "⚠️⚠️ Action: Standard."
        icon = "4️⃣"
    elif result[0]['output']['risk_score'] == 5:
        action = "⚠️ Action: Low Prioriy."
        icon = "5️⃣"
    else:
        action = "Undefined"
    # 
    if result[0]['output']['risk_score'] < 5:
        st.error(action)
        warning_msg = "HelpFirst Score"
        st.info(warning_msg, icon=icon)
    else: 
        st.info(action)
        warning_msg = "HelpFirst Score"
        st.info(warning_msg, icon=icon)
    # 
    # RISKS
    print(result[0]['output']['risks'])
    for i in range(len(result[0]['output']['risks'])):
        if result[0]['output']['risks'][i]['risk_output'] == 'risk present':
            risk_type = result[0]['output']['risks'][i]['risk_type']
            warning_tex = risk_type + " risk present!"
            st.warning(warning_tex, icon="⚠️")
    # SAR REQUEST
    print(result[0]['output']['sar_request'])
    if result[0]['output']['sar_request'][0]['SAR_requested'] == True:
        st.info('Check for a SAR Request!', icon="📝")

    # RISK DATAFRAME
    st.subheader('Risks', divider='grey')
    df_risks = pd.json_normalize(result[0]['output']['risks'])
    df_risks.sort_values('risk_output')
    def highlight(s):
        if s.risk_output == 'risk present':
            return ['background-color: yellow'] * len(s)
        else:
            return ['background-color: white'] * len(s)
    df_risks.style.apply(highlight, axis=1)
    st.dataframe(df_risks, hide_index = True, column_order = ['risk_type','risk_output','explanation'])
    # 
    # CASE SUMMARY
    st.subheader('Case Summary', divider='grey')
    st.text_area('', result[0]['output']['risk_summary'], height=100)
    # 
    # SAR REQUEST
    if result[0]['output']['sar_request'][0]['SAR_requested'] == True:
        st.subheader('SAR Request', divider='grey')
        st.text_area('', result[0]['output']['sar_request'][0]['explanation'], height=200)
        df_sar = pd.json_normalize(result[0]['output']['sar_request'])
        st.dataframe(df_sar, hide_index = True, column_order = ['SAR_requested','explanation'])

     # JSON file
    st.subheader('JSON Output', divider='grey')
    st.download_button(
        label="Download JSON",
        file_name="results.json",
        mime="application/json",
        data=json.dumps(result[0]),
    )
    st.json(result[0], expanded=True)