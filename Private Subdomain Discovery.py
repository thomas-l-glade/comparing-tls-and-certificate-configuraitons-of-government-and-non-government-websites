
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests as r
import time

all_websites = pd.read_csv('all_websites.csv')

headers = {
    "apikey": "bc8762e0-98ea-11ed-a17e-65d49412c0fa"}

zen_url = 'https://app.zenserp.com/api/v2/search'

all_domains = all_websites


def get_subdomain(instring, domain):
    instring = str(instring).lower()
    domain = str(domain).lower()
    https_prefix = 'https://'
    http_prefix = 'http://'

    if domain.startswith(https_prefix):
        domain = domain[len(https_prefix):]
    elif domain.startswith(http_prefix):
        domain = domain[len(http_prefix):]
    if domain.startswith('www.'):
        domain = domain[4:]
    if domain.endswith('/'):
        domain = domain[0:len(domain)-1]

    if instring.startswith(https_prefix):
        instring = instring[len(https_prefix):]
    elif instring.startswith(http_prefix):
        instring = instring[len(http_prefix):]
    if instring.startswith('www.'):
        instring = instring[4:]
    if instring.endswith('/'):
        instring = instring[0:len(instring)-1]
    s = instring.find('/')
    if s > 0:
        instring = instring[0:s]
    if instring.endswith('.' + domain):
        return instring
    elif instring == domain:
        return domain
    else:
        if domain.count('.') > 1:
            dot_index = domain.find('.')
            get_subdomain(instring, domain[dot_index+1:])
        else:
            return ''


def subdomain_scan(start, stop):

    for index, row in all_domains.loc[start:stop].iterrows():

        parent_domain = row['Website']

        params = (
            ("q", '*.' + parent_domain),
        )

        response = r.get(
            zen_url, headers=headers, params=params)

        retries = 0
        while (response.status_code != 200) and (retries < 15):
            time.sleep(5)
            response = r.get(
                zen_url, headers=headers, params=params)
            retries += 1
        if retries >= 15 and response.status_code != 200:
            continue

        response = response.json()

        tempDf = pd.DataFrame(response['organic'])

        for address in tempDf['url']:
            if type(address) == str:
                tempSub = get_subdomain(address, parent_domain).lower().strip()

                if tempSub != parent_domain.lower() and tempSub != '':

                    newRow = dict()
                    for column in all_domains.columns:
                        if column == 'Website':
                            newRow[column] = tempSub
                        else:
                            newRow[column] = row[column]
                    all_domains.loc[len(all_domains.index)] = newRow
    all_domains.drop_duplicates(['Website'], inplace=True)


subdomain_scan(0, len(all_domains))

for col in all_domains.columns:
    if 'Unnamed' in col:
        all_domains.drop([col], axis=1, inplace=True)
all_domains.drop_duplicates(subset=['Website'], keep='first', inplace=True)
all_domains['Website'] = all_domains['Website'].apply(str.lower)
all_domains.to_csv('Private Domains.csv')
