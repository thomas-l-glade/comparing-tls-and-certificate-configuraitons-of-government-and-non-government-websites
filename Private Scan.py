import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests as r
import time

url = 'https://api.ssllabs.com/api/v3/analyze?host='
params = '&all=on'

hostData = pd.DataFrame(columns=['host', 'port', 'protocol', 'isPublic', 'status',
                        'startTime', 'testTime', 'engineVersion', 'criteriaVersion', 'cacheExpiryTime', 'endpoints', 'certs'])

with open('query.txt', 'w') as logFile:
    logFile.write('*** Starting New Log *** ' + '\n')


all_domains = pd.read_csv('Private Domains.csv')

url = 'https://api.ssllabs.com/api/v3/analyze?host='
params = '&all=on'


def corp_web_query(start, stop):

    for index, row in all_domains[start:stop].iterrows():
        if row['Query Fin'] == False:
            hostName = row['Website']
            newRow = dict()
            try:

                request_url = url + hostName + params
                response = r.get(request_url)

                retries = 0
                while (response.status_code != 200):
                    time.sleep(5)
                    response = r.get(request_url)
                    retries += 1
                    if retries >= 15:
                        with open('corp_query.txt', 'a') as logFile:
                            logFile('Error - Max retries passed: ' +
                                    hostName + '\n')
                        break
                if retries >= 15:
                    for column in hostData.columns:
                        if column == 'host':
                            newRow[column] = hostName
                        elif column == 'status':
                            newRow[column] = 'INCOMPLETE'
                        else:
                            newRow[column] = np.nan
                    continue
                else:
                    jReq = response.json()

                    with open('corp_query.txt', 'a') as openFile:
                        openFile.write('Obtained domain: ' + hostName + '\n')

                    for column in hostData.columns:
                        if column == 'host':
                            newRow[column] = hostName
                        elif column in jReq:
                            newRow[column] = jReq[column]
                        else:
                            newRow[column] = np.nan
                    all_domains.at[index, 'Query Fin'] = True

            except r.exceptions.ConnectTimeout:
                for column in hostData.columns:
                    if column == 'host':
                        newRow[column] = hostName
                    elif column == 'status':
                        newRow[column] = 'INCOMPLETE'
                    else:
                        newRow[column] = np.nan
            except r.exceptions.ConnectionError:
                for column in hostData.columns:
                    if column == 'host':
                        newRow[column] = hostName
                    elif column == 'status':
                        newRow[column] = 'INCOMPLETE'
                    else:
                        newRow[column] = np.nan
            # if newRow['status'] != 'INCOMPLETE':
            #     all_domains.at[index, 'Query Fin'] = True
            hostData.loc[len(hostData.index)] = newRow


while len(all_domains[all_domains['Query Fin'] == False]) > 0:
    corp_web_query(0, len(all_domains))
hostData.to_csv('Private Host Data.csv')
