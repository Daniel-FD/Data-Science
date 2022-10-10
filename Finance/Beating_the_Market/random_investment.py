def when_to_invest(start_investment_date, end_investment_date, investment_frecuency = 'daily', investment_type = 'random'):
    # 
    if investment_frecuency == 'monthly' and investment_type == 'random':
        pi = 1/12
    elif investment_frecuency == 'daily' and investment_type == 'random':
        pi = 1
    elif investment_frecuency == 'yearly' and investment_type == 'random':
        pi = 1/365
    else:
        print("Warning: only options for monthly, daily and yearly investments have been configured")
    # 
    if investment_type == 'random':
        number_of_individual_investments = math.ceil((end_investment_date - start_investment_date).days*pi)
        print(number_of_individual_investments)
        investment_dates_list = []
        fake = Faker()
        for i in range(number_of_individual_investments):
            investment_date_temp = fake.date_between(start_date=start_investment_date, end_date=end_investment_date)
            investment_dates_list.append(investment_date_temp)
        # 
        investment_dates_list

    return investment_dates_list