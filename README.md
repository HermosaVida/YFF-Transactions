# YFF-Transactions
Yahoo Fantasy Football - scrape and push transactions using Pushover

This script will:
1. Open leagues.csv to get a list of leagues
2. Scrape Yahoo league pages for transactions in each league
3. Check to see if those transactions are new
4. If new, push them out using pushover.net API
5. Repeat that process in a loop

This requires:
1. Publicly viewable Yahoo fantasy football league
2. Pushover user key (https://pushover.net)
3. Pushover application API key (https://pushover.net/apps)
4. leagues.csv

leagues.csv format:

email,league,user_key,api_token,league_name,errors

league = Yahoo league ID (5-6 numbers)

user_key = pushover.net user key

api_token = pushover.net app api token

league_name = name of league, scraped if empty

errors = # of errors from previous processes (for skipping/logging)
