import mechanize
from bs4 import BeautifulSoup
import csv
import urllib
import requests
import time
import os

# touch - use this for touching a file so we know the last time it ran
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

# this is the main function
# it opens a URL, scrapes the league transactions, turns that into text,
# checks that text against a log file to identify new transactions,
# opens a URL to push those transactions using Pushover, then logs those 
# transactions to a file
def Transactions(league, token, api):
	# league = yahoo league ID (usually 5-6 numbers)
	# token = pushover user token = 30 characters
	# api = pushover app api token = 30 characters
	# https://pushover.net
	# https://pushover.net/apps

	# logfile stores transactions for a league so we can check for new ones
	logfile = 'logs/' + league + '.txt'
	# URL for scraping transactions
	mainURL = 'https://football.fantasysports.yahoo.com/f1/' + league
	URL = 'https://football.fantasysports.yahoo.com/f1/' + league + '/transactions'

	# open html and clean it up
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]

	# scrape the main league page to extract the leage name
	league_scrape = br.open(mainURL).get_data()
	league_soup = BeautifulSoup(league_scrape,"lxml")

	# extract the league name from the title of the main league page
	league_name = league_soup.title.string.split('|')[0]

	# for error handling in future
	# if we find u\xa0, this is a private league - exit
	# -1 means it's a public league and we find a league name
	public_league = league_name.find(u'\xa0')
	
	# if it's -1, it's a public league
	# if it's anything but -1, there is an error so stop here
	if public_league is not -1:
		return

	# for logging
	print time.ctime() + ' - ' + league + ' - ' + league_name

	# scrape the transactions page
	html_scrape = br.open(URL).get_data()
	soup = BeautifulSoup(html_scrape, "lxml")

	# find tables
	tables = soup.findAll('table')

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
		if rowString in open(logfile).read():
			# if so, skip it
			pass
		else:
			# if not, send it to Puhsoverlog it to the file

			# Send to Pushover
			# API: https://pushover.net/api
			pushover_data = [
			('token', token),
			('user', api),
			('title', league_name),
			('html', '1'),
			('message', rowString),
			]
			r = requests.post('https://api.pushover.net/1/messages.json', data=pushover_data)

			# r = 200 is OK
			# if r = 200, OK
			# if anything but 200, there is an error

			# Log transaction to file
			f.write(rowString + '\n')

	# Close transactions log file when done
	f.close()

# what time did this python script start
starttime=time.time()
while True:
  # print current time
  # print time.ctime()
  # open leagues.csv and process each line
  with open('leagues.csv','rb') as csvfile:
	reader = csv.DictReader(csvfile) # get labels from row 1
	# run the Transactions function on each row
        for row in reader:
                Transactions (row['league'], row['user_key'], row['api_token'])
  # log most recent run time
  touch('lastrun.txt')
  # repeat every 60 seconds
  # time.sleep(60.0 - ((time.time() - starttime) % 60.0))
