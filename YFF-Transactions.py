import mechanize
from bs4 import BeautifulSoup
import csv
import logging
import urllib
import requests
import time
import os

path = '' # working path
FORMAT = '%(asctime)s %(levelname)s - %(message)s' # debug.log formatting
logging.basicConfig(filename= path + 'debug.log',level=logging.INFO,format=FORMAT)
delay = 60.0 # delay between loops

# touch - use this for touching a file so we know the last time it ran
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

# return a league name based on the league number
def get_league_name(league):
	# league = yahoo league ID (usually 5-6 numbers)

	# URL for scraping transactions
	mainURL = 'https://football.fantasysports.yahoo.com/f1/' + league

	# open html and clean it up
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]

	# scrape the main league page to extract the leage name
	league_scrape = br.open(mainURL).get_data()
	league_soup = BeautifulSoup(league_scrape,"lxml")

	# extract the league name from the title of the main league page & strip spaces
	league_name = league_soup.title.string.split('|')[0]
	league_name = ' '.join(league_name.split())

	# for error handling in future
	# if we find u\xa0, this is a private league - exit
	# -1 means it's a public league and we find a league name
	public_league = league_name.find(u'\xa0')

	# if it's -1, it's a public league
	# if it's anything but -1, there is an error
	# log it and return an empty string
	if public_league is not -1:
		logging.warning('League ' + league + ' is not public.')
		return ''

	return league_name

# this is the main function
# it opens a URL, scrapes the league transactions, turns that into text,
# checks that text against a log file to identify new transactions,
# opens a URL to push those transactions using Pushover, then logs those 
# transactions to a file
# returns 0 if no errors
# retruns 1 if error
def Transactions(league, league_name, user_key, api_token):
	# league = yahoo league ID (usually 5-6 numbers)
	# league_name = yahoo league name (string)
	# user_key = pushover user key = 30 characters
	# api_token = pushover app api token = 30 characters
	# https://pushover.net
	# https://pushover.net/apps

	# logfile stores transactions for a league so we can check for new ones
	logfile = path + 'logs/' + league + '.txt'
	# URL for scraping transactions
	URL = 'https://football.fantasysports.yahoo.com/f1/' + league + '/transactions'

	# open html and clean it up
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]

	# scrape the transactions page
	html_scrape = br.open(URL).get_data()
	soup = BeautifulSoup(html_scrape, "lxml")

	# find tables
	tables = soup.findAll('table')

	# if no tables, error
	if len(tables) is 0:
		logging.warning('No tables')
		return 1

	# get the second table - this is the transaction table
	table=tables[1]

	# get all of the rows in the table
	rows = table.findAll({'tr'})
	numrows = len(rows)

	# open transactions log file for appending
	f = open(logfile, "a")

	# loop through all rows in table from last to first
	# last row has the oldest transaction so we go from oldest to newest
	for i in xrange(numrows-1,-1,-1):
		# rowString will be a string with the current row of the table
		# each row has a different transaction
		rowString= ""
		row=rows[i]

		# div separates everything in a row
		cols = row.find_all({'div'})
		# loop throw all cells, clean up text, and combine them into a single string
		for j in xrange(0,len(cols)):
			# get each cell and strip out extras
			cell = cols[j].get_text().rstrip().strip()
			# replace line feeds with a space
			cell = cell.replace('\n', ' ').replace('\r', '')
			# change multiple spaces into a single space
			cell = ' '.join(cell.split())
			# add that cell to our row
			rowString = rowString + '\n' + cell
		# check if this row is in the transactions log file
		# all previous transactions are logged in the file
		if rowString in open(logfile).read():
			# if so, skip it (it's not new)
			pass
		else:
			# if not, it's new, send it to Puhsoverlog it to the file
			# send rowString as the message

			# Send to Pushover
			# API: https://pushover.net/api
			pushover_data = [
			('token', api_token),
			('user', user_key),
			('title', league_name),
			('html', '1'),
			('message', rowString),
			]
			r = requests.post('https://api.pushover.net/1/messages.json', data=pushover_data)

			# log what we send
			logging.info ('League : ' + league)
			logging.info ('User   : ' + user_key)
			logging.info ('API    : ' + api_token)
			logging.info ('Message: ' + rowString)
			logging.info ('Status : ' + str(r.status_code))

			# if r.status_code = 200, everything OK
			# anything but 200 means there is an error
			if r.status_code is not 200:
				logging.warning ('League : ' + league)
				logging.warning ('User   : ' + user_key)
				logging.warning ('API    : ' + api_token)
				logging.warning ('Message: ' + rowString)
				logging.warning ('Status : ' + str(r.status_code))
				return 1

			# Log transaction to file
			# This is checked each time to see if it's a new transaction
			f.write(rowString + '\n')

	# Close transactions log file when done
	f.close()
	return 0 # no errors

# what time did this python script start
starttime=time.time()
while True:
	# open leagues.csv and process each line
	f = open(path + 'leagues.csv','rb')
	reader = csv.DictReader(f) # get labels from row 1
	headers = reader.fieldnames # capture headers
	csv_data = [l for l in reader] # store all CSV data
	csv_data2 = csv_data # make a copy of it to see if anything has changed
	f.close()

	# loop through each row in CSV file
        for row in csv_data:
		# get number of errors
		if row['errors'] is None:
			row['errors'] = 0
		# if league name is empty, fill it
		if row['league_name'] is None:
			row['league_name'] = get_league_name (row['league'])
                # run transactions function & get result
		t = Transactions (row['league'], row['league_name'], row['user_key'], row['api_token'])
		# t=0 - no errors
		# t=1 - errors
		# total up errors
		row['errors'] = int(row['errors']) + int(t)

	# did anything chane?
	if csv_data is csv_data2:
		pass
	else:
		# if something changed (got a new league name OR counted an error)
		# then log the changes to a new file
		f2 = open(path + 'new.csv','wb')
		writer = csv.DictWriter(f2, fieldnames=headers)
		writer.writeheader() # write headers to row 1
		writer.writerows(csv_data) # write new data
		f2.close()

  	touch(path + 'lastrun.txt')
 
 	# repeat every 60 seconds
  	time.sleep(delay - ((time.time() - starttime) % delay))
