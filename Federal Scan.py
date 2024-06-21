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
df = pd.read_csv('allDomains.csv')
for index, row in df.iterrows():

    hostName = row['Domain Name']
    newRow = dict()

    try:
        request_url = url + hostName + params
        response = r.get(request_url)
        retries = 0

        while (response.status_code != 200):
            time.sleep(10)
            response = r.get(request_url)
            retries += 1
            if retries >= 15:
                with open('query.txt', 'a') as logFile:
                    logFile.write(
                        'Error - Max retries passed: ' + hostName + '\n')
                for column in hostData.columns:
                    if column == 'host':
                        newRow[column] = hostName
                    elif column == 'status':
                        newRow[column] = 'INCOMPLETE'
                    else:
                        newRow[column] = np.nan
                break
        if retries >= 15:

            continue
        else:
            jReq = response.json()

            with open('query.txt', 'a') as openFile:
                openFile.write('Obtained domain: ' + hostName + '\n')

            for column in hostData.columns:
                if column == 'host':
                    newRow[column] = hostName
                elif column in jReq:
                    newRow[column] = jReq[column]
                else:
                    newRow[column] = np.nan

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
    hostData.loc[len(hostData.index)] = newRow
hostData.to_csv('Federal Host Data.csv')
