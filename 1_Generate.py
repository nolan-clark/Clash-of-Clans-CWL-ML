# Generate and collect clan tags of clans in 15v15 CWL 

# Import packages

import requests
import pandas as pd
import json
import datetime
from tqdm import tqdm
import os

import CWL_Functions as cf
import MyKeys # Private API KEY -- update MyKeys.py 

# Automate pointers for the pipeline -- avoid erasing previous month
month=datetime.datetime.now().strftime('%B')


# Write output directory if first run
path = './output'

# check whether directory already exists
if not os.path.exists(path):
  os.mkdir(path)
  print("Folder %s created!" % path)
else:
  print("Folder %s already exists" % path)
    
# ******* OUTPUT location ********
out_file = f'output/pipeCheckpoint_1_{month}.json'

# API Token used with the documented Authorization header. 
# The headers are the necessary params of each endpoint
MyToken = MyKeys.MyToken
headers = {'authorization': 'Bearer '+(MyToken), 'Accept': 'application/json'}
base = 'https://api.clashofclans.com/v1/'

# Collection Bins 
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


# Large collection of clan tags -- potential clans in CWL
bucket = []
clanPointInts = [20000,30000,40000,50000]

for points in clanPointInts:
    params = {'limit':'100','minClanPoints':points}
    after_page = ''
    while after_page != False:
        all_tags = cf.search_clans_v2(**params)
        bucket.extend(all_tags[0])
        after_page = all_tags[1]
        params['after'] = after_page

top_clans = pd.unique(bucket)
print(f'Total unique clan tags collected: {len(top_clans)}')

# Initiate Session for testing candidacy 
session = requests.Session()
session.headers.update(headers)

# Check if clan tag is in CWL and keep 15v15s

for clan in tqdm(top_clans):
    url=f'{base}clans/%23{clan}/currentwar/leaguegroup'
    response = session.get(url,timeout=10)
    j = cf.status15(response)
    if j != False:
            url=f'{base}clans/%23{clan}'
            response = session.get(url,timeout=10)
            league = response.json()['warLeague']['name']
            LeagueBins[league].append(clan)

# Write Checkpoint of unique clans generated before continuing. 
print(f'Writing output to {out_file}')

with open(out_file,"w") as write_file:
    json.dump(LeagueBins, write_file)
