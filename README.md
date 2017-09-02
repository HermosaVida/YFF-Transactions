# YFF-Transactions
Yahoo Fantasy Football - scrape and push transactions using Pushover

This requires:
1. Publicly viewable Yahoo fantasy football league
2. Pushover user key (https://pushover.net)
3. Pushover application API key (https://pushover.net/apps)

Todo:
1. Create the ability to run this as a batch against many leagues
2. Add error checking (if something isn't working, keep going on the other leagues)

Details for running as a batch:
1. Keep list of leagues in leagues.csv (one league per line)
2. leagues.csv has 4 fields: email,yahoo_league,user_key,api_token
3. Open leagues.csv, read each line, run the main function on each league, then repeat

Details for error checking:
1. If a league is "broken" then at least process other leagues
