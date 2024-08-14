# Clash of Clans CWL ML
Data pipeline from the Clash of Clans API to generate ~ 1 million rows of 15v15 Clan War League (CWL) player performance data. Great for developing machine learning models or learning about differences between player performance between leagues.

### Clash of Clans API
Clash of Clans API offers public data access to currently player data. Clash of Clans API does not offer historical data pulling, so pipeline runs are time sensitive. Pipeline runs outside the suggested time window can yield ~ 100,000 rows of data.
* Link to main page of API documentation: https://developer.clashofclans.com/#/documentation

## Usage

Create Clash of Clans developer account to generate JSON Web token for the API key. Copy token into the MyToken variable in the MyKeys.py file to use pipeline.

To maximize pipeline generation, the following timeline should be followed at the beginning of a month:

* 1_Generate: Days 3-6
  * First stage of pipeline collects clanTags of ~3000 clans, then filters by clans currently in 15v15 CWL. Clans can sign up for CWL in the first 48 hours of each month.

* 2_Collect: Days 9-11
  * Second step collects tags of each round. Tags are generated during war preparation phase. Ideal time is near the end of CWL event to collect when the most clans are still in CWL and all 7 days of tags are still available.

* 3_Validate: Days 12-30
  * Third step validates that all tags from step 2 are viable. This should be run after CWL has finished, but before the next CWL begins.

* 4_DataFrame: after validation run
  * Final step generates a dataframe from the validated tags of each round.
