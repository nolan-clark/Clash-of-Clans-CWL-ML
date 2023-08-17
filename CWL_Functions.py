import requests
import json
import datetime
import MyKeys
import pandas as pd

MyToken = MyKeys.MyToken

headers = {'authorization': 'Bearer '+(MyToken), 'Accept': 'application/json'}

def grabTags(ClanTag):
    collect = []
    month=datetime.datetime.now().strftime('%B')
    
    
    url='https://api.clashofclans.com/v1/clans/%23'+ClanTag+'/currentwar/leaguegroup'
    response = requests.get(url, headers=headers, timeout=30)
    print(response.status_code, response.reason)
    
    for i in range(7):
        collect.extend(response.json().get('rounds')[i].get('warTags'))
    
    collDict = {month : collect}
    
    return collDict
    
def get_attacks(response):

    member = response.json()['clan'].get('members')
    o_member = response.json()['opponent'].get('members')
    
    clan_name = response.json()['clan'].get('name')
    clan_tag = response.json()['clan'].get('tag')
    opp_clan_name = response.json()['opponent'].get('name')
    opp_clan_tag = response.json()['opponent'].get('tag')
    
    data = []
    attacks = []
    defense_bin = []
    
# grab first clan Name, ID, TH, Attacks, and Defense stats
    for mem in member:
        output = {'name': mem.get('name'),
                  'tag' : mem.get('tag'),
                  'clan' : clan_name,
                  'clan_tag' : clan_tag,
                  'mapPosition': mem.get('mapPosition'),
                  'TH_lvl' : mem.get('townhallLevel')
                 }
        data.append(output)
        
        
        attack = mem.get('attacks')
        if attack == None:
            attack=[{'attackerTag': mem.get('tag'),
             'defenderTag': None,
             'stars': None,
             'destructionPercentage': None,
             'order': None,
             'duration': None}]
        attacks.append(attack[0])
        
        ['opponentAttacks']
        defense = mem.get('bestOpponentAttack')
        if defense == None:
            defense = {'defenderTag':None,
                         'stars': None,
                         'destructionPercentage': None,
                         'order': None,
                         'duration': None
                        }
        defense_bin.append(defense)
        
# grab second clan Name, ID, TH, Attacks, and Defense stats        
    for mem in o_member:
        output = {'name': mem.get('name'),
                  'tag' : mem.get('tag'),
                  'clan' : opp_clan_name,
                  'clan_tag' : opp_clan_tag,
                  'mapPosition': mem.get('mapPosition'),
                  'TH_lvl' : mem.get('townhallLevel')
                 }
        data.append(output)
        attack = mem.get('attacks')
        if attack == None:
            attack=[{'attackerTag': mem.get('tag'),
             'defenderTag': None,
             'stars': None,
             'destructionPercentage': None,
             'order': None,
             'duration': None}]
        attacks.append(attack[0])
        
        defense = mem.get('bestOpponentAttack')
        if defense == None:
            defense = {'defenderTag':None,
                         'stars': None,
                         'destructionPercentage': None,
                         'order': None,
                         'duration': None
                        }
            
        defense_bin.append(defense)
   
    
    return data,attacks,defense_bin

def frame_attacks(war_id, league=None):
    returned_war_attacks = get_attacks(war_id)

# set info df for merge
    info = pd.DataFrame(returned_war_attacks[0])

# set attack df for merge -- specify attack stats
    atk = pd.DataFrame(returned_war_attacks[1])
    atk.rename(columns={'attackerTag':'tag'}, inplace=True)
    atk = atk[['tag','stars','destructionPercentage','order','duration']]
    atk.rename(columns={'stars':'A_stars',
                       'destructionPercentage':'A_Percent',
                       'order':'A_order',
                       'duration':'A_duration'
                       }, inplace=True)
    
# set defense df for merge -- specify defense stats
    defs = pd.DataFrame(returned_war_attacks[2])
    defs = defs[['defenderTag','stars','destructionPercentage','order','duration']]

    defs.rename(columns={'defenderTag':'tag',
                         'stars': 'D_stars',
                         'destructionPercentage':'D_Percent',
                         'order':'D_order',
                         'duration':'D_duration'
                        }, inplace = True)



    df = pd.merge(info,atk, how = 'inner', on = 'tag')
    df_all = pd.merge(df, defs, how = 'left', on = 'tag')
    
    df_all['league'] = league
    df_all['attack_trans'] = df_all.A_stars*df_all.A_Percent
    df_all['def_trans'] = df_all.D_stars*df_all.D_Percent
    df_all['star_diff'] = (df_all.A_stars - df_all.D_stars)

    
    return df_all

# View the cwl round pull page

def cwlRound(warTag):
    war_id_transformed = warTag.strip('#')
    url=('https://api.clashofclans.com/v1/clanwarleagues/wars/%23'+(war_id_transformed))
    response = requests.get(url, headers=headers, timeout=30)
    
    json_war = response.json()
    
    return json_war

# View the clan pull page

def clan(clanTag):
    clan_id_transformed = clanTag.strip('#')
    url='https://api.clashofclans.com/v1/clans/%23'+clan_id_transformed
    response = requests.get(url, headers=headers, timeout=30)
    
    json_clan = response.json()
    
    return json_clan

# Return the war league of a clan

def league(clanTag):
    
    url='https://api.clashofclans.com/v1/clans/%23'+clanTag
    response = requests.get(url, headers=headers, timeout=30)
    #print(response.status_code, response.reason)
    war_league= response.json()['warLeague']['name']
    
    
    return war_league

# Return true if status of clan is in a 15 clan CWL 

def status15(clanTag):
    url='https://api.clashofclans.com/v1/clans/%23'+clanTag+'/currentwar/leaguegroup'
    response = requests.get(url, headers=headers, timeout=30)
    #print(response.status_code, response.reason)
    
    if response.status_code == 200:
        status = response.json()['state']
        first_round = response.json()['rounds'][0].get('warTags')[0]
        cwl_size = cwlRound(first_round)['teamSize']
        if cwl_size > 15:
            status = False
    else:
        status = False
    
    return status

# Return keys with values

def leagueBinsNotEmpty(dictObj):
    leagueBinCounts ={key: (len(dictObj[key])) for key in  dictObj.keys()}
    fullBins = {k:v for k,v in leagueBinCounts.items() if v >0}
    leagueList = [league for league in fullBins.keys()]
    return fullBins, leagueList

# Return clan and opponent

def getClanOppTags(warTag):
    war_id_transformed = warTag.strip('#')
    url=('https://api.clashofclans.com/v1/clanwarleagues/wars/%23'+(war_id_transformed))
    response = session.get(url,timeout=10)
    
    clans_in_this_war = [response.json()['clan'].get('tag'),response.json()['opponent'].get('tag')]
    
    return clans_in_this_war
    
# Return stars and percentage

def grab_cwl_stars(response):
    
    clan_tag = response.json()['clan'].get('tag')
    opp_tag = response.json()['opponent'].get('tag')
    
    clan_star = response.json()['clan'].get('stars')
    clan_percent = response.json()['clan'].get('destructionPercentage')
    opp_star = response.json()['opponent'].get('stars')
    opp_percent = response.json()['opponent'].get('destructionPercentage')
    
    if clan_star == opp_star:
        if clan_percent > opp_percent:
            clan_star+=10
        elif  clan_percent < opp_percent:
            opp_star+=10
    if clan_star > opp_star:
        clan_star+=10
    else:
        opp_star+=10
        
    return clan_tag, clan_star, opp_tag, opp_star, clan_percent, opp_percent

# Pipeline Function

def melt(ClanTag):
    url='https://api.clashofclans.com/v1/clans/%23'+ClanTag
    response = session.get(url,timeout=10)
    #print(response.status_code, response.reason)
    league= response.json()['warLeague']['name']
    
    
    return league

# Pipeline cwl_round warTags grab

def grabTagsBig(ClanTag):
    collect = []
    
    url='https://api.clashofclans.com/v1/clans/%23'+ClanTag+'/currentwar/leaguegroup'
    response = requests.get(url, headers=headers, timeout=30)
    #print(response.status_code, response.reason)
    
    for i in range(7):
        collect.extend(response.json().get('rounds')[i].get('warTags'))
    
    collDict = collect
    
    return collDict

# Return warStatus of cwl round -- to verify all wars have ended before framing data

def endState(warTag):
    war_id_transformed = warTag.strip('#')
    url=('https://api.clashofclans.com/v1/clanwarleagues/wars/%23'+(war_id_transformed))
    response = requests.get(url, headers=headers, timeout=30)
    
    json_war = response.json()['state']
    
    return json_war