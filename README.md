# Clash of Clans CWL ML
Data pipeline from the Clash of Clans API for machine learning models of Clan War Leagues (CWL). Modeling used to optimize clan performance with team selection, indicate upgrade priorities, and predict final placements of clans. Generates ~1 million rows of player performance data.

## Clash of Clans API
API key is a JSON Web Token. All requests must include this token, MyKeys.MyToken reference this in the headers section.
* Link to main page of API documentation: https://developer.clashofclans.com/#/documentation

## Workflow
The pipeline is time sensitive due Clash of Clans API only allowing pulls of current clan war league data. Each war has a warTag that can be used at a later date to pull data on that war. Best practice is to identify clans that are in 15v15 CWLs within the first week of the month and then collect all 28 warTags before CWL ends. After all 28 warTags are collected, determine the final end time of the wars (or wait for the CWL event to close). Perform quality check to verify Clash of Clans database contains data for all warTags (data will reguarly be perged from database). Then, create dataframes for modeling.

### Time windows for each function of pipeline 
* AutoPipeLeague: execute ~9th day of the month
* MidCWL: execute 12th+
* DataFrameCWL: execute after MidCWL, but before 1st of next month
