# Transform validated warTags into a DataFrame

# Imports go here
import requests
import pandas as pd
import numpy as np
import MyKeys
import json
import datetime
import CWL_Functions as cf
from collections import Counter
from collections import defaultdict
from tqdm import tqdm

# reduce pandas warning for SettingWithCopyWarning 
pd.set_option('mode.chained_assignment', None)

# Automate pointers for the pipeline -- avoid erasing previous month
month=datetime.datetime.now().strftime('%B')

# API Token used with the documented Authorization header. 
# The headers are the necessary params of each endpoint
MyToken = MyKeys.MyToken
headers = {'authorization': 'Bearer '+(MyToken), 'Accept': 'application/json'}
base = 'https://api.clashofclans.com/v1/'

# ******* OUTPUT locations ********
out_file_df = f'output/cwl_df_{month}.csv'
out_file_clans = f'output/cwl_group_performance_{month}.csv'

# open JSON file to update with current CWL
with open(f"output/pipeCheckpoint_2_VALIDATED_{month}.json") as fp:
    LeagueBins = json.load(fp)

# Only Leagues of interest
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


session = requests.Session()
session.headers.update(headers)


cwl_day_bucket = pd.DataFrame(data = None)
clan_count_bucket = Counter()
cwl_groups = defaultdict(list)
cwl_star_bucket = defaultdict(int)
cwl_damage_bucket = defaultdict(float)

#leagues =leagueBinsNotEmpty(dictObj)

# Clan Counter to avoid double grabbing -- optimized

for league in leagues:
    print(league)
    for warTag in tqdm(LeagueBins[league]):
        war_id_transformed = warTag.strip('#')
        url= f'{base}clanwarleagues/wars/%23{war_id_transformed}'
        response = session.get(url,timeout=10)
        roundClanTags = [response.json()['clan'].get('tag'),response.json()['opponent'].get('tag')]
        clan_count_bucket.update(roundClanTags)
        
        if not ((clan_count_bucket.get(roundClanTags[0]) > 7) or (clan_count_bucket.get(roundClanTags[1]) > 7)):
            # group num collect
            cwl_groups[roundClanTags[0]].append(roundClanTags[1])
            cwl_groups[roundClanTags[1]].append(roundClanTags[0])
            # cwl star collect
            rs = cf.grab_cwl_stars(response)
            cwl_star_bucket[rs[0]]+=rs[1]
            cwl_star_bucket[rs[2]]+=rs[3]
            # cwl damage collect
            cwl_damage_bucket[rs[0]]+=rs[4]
            cwl_damage_bucket[rs[2]]+=rs[5]
            # individual performance collect
            df_day = cf.frame_attacks(response, league)
            cwl_day_bucket=cwl_day_bucket.append(df_day, ignore_index=True)

# ADD key to group values before sorting and removing duplicates
for key, group in cwl_groups.items():
    group.append(key)
    
# list of sorted groups
group_sets =[sorted(item) for item in cwl_groups.values()]

# Unique list of groups in comprehension
cwl_unique_groups = [list(x) for x in set(tuple(x) for x in group_sets)]
unique_df=pd.DataFrame(cwl_unique_groups)
uni_df_T = unique_df.T
groups_for_merge = pd.melt(uni_df_T, var_name='group_num', value_name='clan_tag')

# Add league to group df
group_leagues=cwl_day_bucket.groupby(['clan_tag','league'])['name'].count().reset_index()

# Calculate bonus +10 stars for each war win
stars=pd.Series(cwl_star_bucket).to_frame(name = 'Tot_Clan_Stars')
clans_ds=pd.Series(cwl_damage_bucket).to_frame(name='Tot_Clan_Damage').join(stars)
clans_ds_with_league=clans_ds.join(group_leagues.set_index('clan_tag')[['league']])
stars_groups=groups_for_merge.set_index('clan_tag').join(clans_ds_with_league).reset_index()

# Rank the groups for final placement with total clan damage as tie breaker
stars_groups['group_rank'] = stars_groups.sort_values(by = 'Tot_Clan_Damage', 
                         ascending=False).groupby('group_num')['Tot_Clan_Stars'].rank(method = 'first',
                                                                                      ascending = False)

# Map promotion determined by league
def promo_results(x,y,z):
    if x <= y:
        return 'PROMOTED'
    elif x >= z:
        return 'DROPPED'
    else:
        return 'REMAINED'

two_promo = [ 'Gold League III',
            'Gold League II',
            'Gold League I',
            'Crystal League III',
            'Crystal League II']

one_promo =  ['Crystal League I',
            'Master League III',
            'Master League II',
            'Master League I',
            'Champion League III',
            'Champion League II']

# Split by league results
ones=stars_groups[stars_groups['league'].isin(one_promo)]
twos=stars_groups[stars_groups['league'].isin(two_promo)]
threes=stars_groups[stars_groups['league']=='Champion League I']

ones['result']=ones['group_rank'].apply(promo_results, args=[1,7])
twos['result']=twos['group_rank'].apply(promo_results, args=[2,7])
threes['result']=threes['group_rank'].apply(promo_results, args=[0,6])

stars_groups=pd.concat([ones,twos,threes])

# Write to file Clans measures
stars_groups.to_csv(out_file_clans, index=True)

cwl_df=cwl_day_bucket.merge(stars_groups[['clan_tag','group_rank','result']], on = 'clan_tag')
cwl_df.to_csv(out_file_df, index=True)
