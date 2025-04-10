import requests
import datetime
import pandas as pd
import numpy as np

response = requests.get("https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/2020-01-22/2020-05-10")

# checking the response of json using api
if response.status_code == 200:
    file = response.json()  
    scale = file.get('scale')   # getting the scale values 
    countries = file.get('countries')   # getting the countries values
    data = file.get('data')     # getting the data values

    #data.keys()
    dateList = list(data.keys())    
    countries=pd.DataFrame(countries)   # converting into datafrmae
    #print(dateList)

    # extracting the dates from the json page
    date_data = pd.DataFrame({})
    for date in dateList:
        date_data[date] = data.get(date)

    # creating a list for all the values present in the page
    date = []
    country_code1 = []
    confirmed = []
    deaths = []
    stringency_actual = []
    stringency = []
    stringency_legacy = []
    stringency_legacy_disp = []

    # extracting the values and apppending them into the above created list
    for date1, countries in date_data.items():
        for country_code, country_data in countries.items():
            date.append(country_data['date_value'])
            country_code1.append(country_data['country_code'])
            confirmed.append(country_data['confirmed'])
            deaths.append(country_data['deaths'])
            stringency_actual.append(country_data['stringency_actual'])
            stringency.append(country_data['stringency'])
            stringency_legacy.append(country_data['stringency_legacy'])
            stringency_legacy_disp.append(country_data['stringency_legacy_disp'])

    # creating a new dataframe to store all the list values
    json_data = pd.DataFrame({'Date': date, 'Country code': country_code1, 'Confirmed cases': confirmed, 'Deaths': deaths,
                'Stringency actual': stringency_actual,'Stringency': stringency,'Stringency legacy': stringency_legacy,
                'Stringency legacy disp': stringency_legacy_disp})

    # create separate dataframes for confirmed cases, deaths and stringency
    confirmedcases = pd.DataFrame(columns=date_data.columns)
    deaths = pd.DataFrame(columns=date_data.columns)
    stringency_index = pd.DataFrame(columns=date_data.columns)
     
    # assign country codes to dataframes
    confirmedcases['country'] = country_code1
    deaths['country'] = country_code1
    stringency_index['country'] = country_code1

    # Drop duplicate country codes
    confirmedcases = confirmedcases.drop_duplicates('country')
    deaths = deaths.drop_duplicates('country')
    stringency_index = stringency_index.drop_duplicates('country')
    
    # Reordering column 'country' as the first column
    confirmedcases = confirmedcases[['country'] + [col for col in confirmedcases.columns if col != 'country']]
    deaths = deaths[['country'] + [col for col in deaths.columns if col != 'country']]
    stringency_index = stringency_index[['country'] + [col for col in stringency_index.columns if col != 'country']]

    # loop for confirmed cases
    for index, row in json_data.iterrows():
      country_code = row['Country code']
      date = row['Date']
      confirmed_cases = row['Confirmed cases']
      confirmedcases.loc[confirmedcases['country'] == country_code, date] = confirmed_cases
      
    # Loop for deaths
    for index, row in json_data.iterrows():
        country_code = row['Country code']
        date = row['Date']
        death_cases = row['Deaths']
        # Update death cases in deaths DataFrame
        deaths.loc[deaths['country'] == country_code, date] = death_cases
        
    # Loop for stringency index
    for index, row in json_data.iterrows():
        country_code = row['Country code']
        date = row['Date']
        stringency = row['Stringency']
        # Update stringency index in stringency_index DataFrame
        stringency_index.loc[stringency_index['country'] == country_code, date] = stringency

    confirmedcases.reset_index(inplace=True)
    deaths.reset_index(inplace=True)
    stringency_index.reset_index(inplace=True)
    
    # rename index as country code
    confirmedcases.rename(columns={'index': 'Country code'}, inplace=True)
    deaths.rename(columns={'index': 'Country code'}, inplace=True)
    stringency_index.rename(columns={'index': 'Country code'}, inplace=True)
    
    # droppping duplicate values
    confirmedcases = confirmedcases.drop_duplicates('Country code')
    deaths = deaths.drop_duplicates('Country code')
    stringency_index = stringency_index.drop_duplicates('Country code')

    # writing into different sheets in an excel file
    with pd.ExcelWriter('My_OxCGRT_summary.xlsx') as writer:
      confirmedcases.to_excel(writer, sheet_name='Confirmed Cases', index=False)
      deaths.to_excel(writer, sheet_name='Deaths', index=False)
      stringency_index.to_excel(writer, sheet_name='Stringency Index', index=False)

