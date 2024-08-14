# Validate extracted round tags from step 2 before transforming into a dataframe

# import packages
import MyKeys
import json
import requests
import datetime
from tqdm import tqdm
import time
import pprint

# Automate pointers for the pipeline -- avoid erasing previous month
month=datetime.datetime.now().strftime('%B')

# ******* OUTPUT location ********
out_file = f'output/pipeCheckpoint_2_VALIDATED_{month}.json'

# open JSON file to update with current CWL
with open(f"output/pipeCheckpoint_2_{month}.json") as fp:
    LeagueBins = json.load(fp)

# API Token used with the documented Authorization header. 
# The headers are the necessary params of each endpoint
MyToken = MyKeys.MyToken
headers = {'authorization': 'Bearer '+(MyToken), 'Accept': 'application/json'}
base = 'https://api.clashofclans.com/v1/'


# CWL Leagues of interest. Lower leagues most important features are participation
leagues = [ 'Gold League III',
            'Gold League II',
            'Gold League I',
            'Crystal League III',
            'Crystal League II',
            'Crystal League I',
            'Master League III',
            'Master League II',
            'Master League I',
            'Champion League III',
            'Champion League II',
            'Champion League I']

# A tag may have been deleted in between step 2 and 3 -- bin to collect bad tags
dud_bin = {
            'Bronze League III': [],
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

# Test all warTags' states as warEnded before transforming into dataframe

# Initiate session
session = requests.Session()
session.headers.update(headers)


c = {'warEnded':0}
lastEnd = time.localtime()

for league in leagues:
    print(league)
    for warTag in tqdm(LeagueBins[league]):
        war_id_transformed = warTag.strip('#')
        url = f'{base}clanwarleagues/wars/%23{war_id_transformed}'
        try:
            response = session.get(url, timeout=10)
            roundJSON = response.json()
            c[roundJSON['state']]+=1
        except KeyError:
            try:
                flag = time.strptime(roundJSON['endTime'], '%Y%m%dT%H%M%S.%fZ')
                if lastEnd < flag:
                    lastEnd = flag
                    print('Final end updated.')
                continue
            except KeyError:
                dud_bin[league].append(warTag)
                pass
    else:
        continue
    break

print('The final round will be completed at: ',time.asctime(lastEnd), '. If that is in the future, rerun this pipeline at that time. \n')
print('Bad tags found by league: \n')
pprint.pprint({key: (len(dud_bin[key])) for key in  dud_bin.keys()}, sort_dicts=False)

vLeagueBins = {
            'Bronze League III': [],
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

for league in leagues:
    filtered_list=list(filter(lambda i: i not in dud_bin[league], LeagueBins[league]))
    vLeagueBins[league] = filtered_list

# write the updated file
print(f'Writing output to {out_file}')
with open(out_file,"w") as write_file:
    json.dump(vLeagueBins, write_file)
