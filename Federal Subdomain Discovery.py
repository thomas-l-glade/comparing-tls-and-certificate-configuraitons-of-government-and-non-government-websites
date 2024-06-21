import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests as r
import time

df = pd.read_csv('current-federal.csv')

headers = {
    "apikey": "bc8762e0-98ea-11ed-a17e-65d49412c0fa"}

zen_url = 'https://app.zenserp.com/api/v2/search'

with open('zenserp_query.txt', 'w') as logFile:
    logFile.write('*** Starting New Log *** ' + '\n')


def get_subdomain(instring, domain):
    instring = str(instring).lower()
    domain = str(domain).lower()
    https_prefix = 'https://'
    http_prefix = 'http://'
    if instring.startswith(https_prefix):
        instring = instring[len(https_prefix):]
    elif instring.startswith(http_prefix):
        instring = instring[len(http_prefix):]
    if instring.startswith('www.'):
        instring = instring[4:]
    s = instring.find('/')
    if s > 0:
        instring = instring[0:s]
    if instring.endswith('.' + domain):
        return instring
    elif instring == domain:
        return domain
    else:
        return ''


for index, row in df.iterrows():

    parent_domain = row['Domain Name']

    params = (
        ("q", '*.' + parent_domain),
    )

    response = r.get(
        zen_url, headers=headers, params=params)

    retries = 0
    while (response.status_code != 200):
        time.sleep(10)
        response = r.get(
            zen_url, headers=headers, params=params)
        retries += 1
        if retries >= 15:
            with open('zenserp_query.txt', 'a') as logFile:
                logFile('Error - Max retries passed: ' + parent_domain + '\n')
            break
    if retries >= 15:
        continue

    response = response.json()

    tempDf = pd.DataFrame(response['organic'])

    for address in tempDf['url']:
        if type(address) == str:
            tempSub = get_subdomain(address, parent_domain).upper().strip()
            with open('zenserp_query.txt', 'a') as logFile:
                logFile.write('Checking subdomain: ' + tempSub + ' of domain: ' +
                              parent_domain + ' current check is: ' + address + '\n')
            if tempSub != parent_domain.upper() and tempSub != '':
                with open('zenserp_query.txt', 'a') as logFile:
                    logFile.write('Subdomain found: ' + tempSub + '\n')
                newRow = dict()
                for column in df.columns:
                    if column == 'Domain Name':
                        newRow[column] = tempSub
                    else:
                        newRow[column] = row[column]
                df.loc[len(df.index)] = newRow

df.drop_duplicates(['Domain Name'], inplace=True)
df.to_csv('allDomains.csv')
