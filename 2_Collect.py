# Collect tags for each round of CWL from clan tags generated in step 1

# import packages

import MyKeys
import json
import requests
import datetime
from tqdm import tqdm
import pandas as pd
import pprint

# Automate pointers for the pipeline -- avoid erasing previous month
month=datetime.datetime.now().strftime('%B')

# ******* OUTPUT location ********
out_file = f'output/pipeCheckpoint_2_{month}.json'

# open JSON file to update with current CWL
with open(f"output/pipeCheckpoint_1_{month}.json") as fp:
    tag_bin = json.load(fp)

MyToken = MyKeys.MyToken
headers = {'authorization': 'Bearer '+(MyToken), 'Accept': 'application/json'}
base = 'https://api.clashofclans.com/v1/'


LeagueBins = {'Bronze League III': [],
 'Bronze League II': [],
 'Bronze League I': [],
 'Silver League III': [],
 'Silver League II': [],
 'Silver League I': [],
 'Gold League III': [],
 'Gold League II': [],
 'Gold League I': [],
 'Crystal League III': [],
 'Crystal League II': [],
 'Crystal League I': [],
 'Master League III': [],
 'Master League II': [],
 'Master League I': [],
 'Champion League III': [],
 'Champion League II': [],
 'Champion League I': []}


# Initiate Session for -- faster than inititing thousands of get calls 
session = requests.Session()
session.headers.update(headers)

# LARGE GRAB

leagueNames=list(tag_bin.keys())

for league in leagueNames:
    print(f'Collecting Rounds for {league}')
    for tag in tqdm(tag_bin[league]):
        try:
            collect = []
            url = f'{base}clans/%23{tag}/currentwar/leaguegroup'
            response = session.get(url, timeout=10)
            
            # range of 7 so that only CWL with all rounds will be pulled
            for i in range(7):
                collect.extend(response.json().get('rounds')[i].get('warTags'))
            if collect[-1] == '#0':
                rounds = None
            else:
                rounds = collect
                
            LeagueBins[league].extend(rounds)
        except (TypeError, IndexError):
            pass

print(' \n \nCollection Completed! Pipeline Report: \n \n ------------------------------------------------')
print('Total rounds collected:')
pprint.pprint({key: (len(LeagueBins[key])) for key in  LeagueBins.keys()}, sort_dicts=False)
print('Total unique rounds collected:')
pprint.pprint({key: (len(pd.unique(LeagueBins[key]))) for key in  LeagueBins.keys()}, sort_dicts=False)
print('Total duplicate rounds collected:')
pprint.pprint({key: (len(LeagueBins[key])-len(pd.unique(LeagueBins[key]))) for key in  LeagueBins.keys()}, sort_dicts=False)

cwlRoundsBins={key: list(pd.unique(LeagueBins[key])) for key in  LeagueBins.keys()}

# write the updated file -- test to make sure all warTags are full. each cwl should have 28
print(f'Writing output to {out_file}')

if {key: (len(cwlRoundsBins[key])//28) for key in  cwlRoundsBins.keys()} == {key: (len(cwlRoundsBins[key])/28) for key in  cwlRoundsBins.keys()}:
    with open(out_file,"w") as write_file:
        json.dump(cwlRoundsBins, write_file)
else:
    print(f'No good. See -> output/pipeCheckpoint_2_{month}_ERROR_for_QA.json <- for potential errors')
    with open(f'output/pipeCheckpoint_2_{month}_ERROR_for_QA.json',"w") as write_file:
        json.dump(cwlRoundsBins, write_file)

print('Total expected rows of data = ', sum([len(i) for i in cwlRoundsBins.values()]) * 30)
