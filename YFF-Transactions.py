import mechanize
from bs4 import BeautifulSoup
import urllib
import requests
import time
import os

# define the 3 things we need - Yahoo league, user token, and API
# https://pushover.net/
# token = pushover user key
# API = pushover application API token - https://pushover.net/apps
# token and API are 30 character strings
league = '20314'
pushover_token = ''
pushover_api = ''

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
	# data will have the pushover message
	data = [] 

	# logfile stores transactions for a league so we can check for new ones
	logfile = league + '.txt'
	# URL for scraping transactions
	URL = 'https://football.fantasysports.yahoo.com/f1/' + league + '/transactions'

	# open html and clean it up
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
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
			print league + ': OLD: ' + rowString
		else:
			# if not, send it to Puhsoverlog it to the file
			print league + ': NEW: ' + rowString

			# Send to Pushover
			# API: https://pushover.net/api
			# Future: Replace 'Transaction' with league name (scrape this from transaction URL)
			data = [
			('token', token),
			('user', api),
			('title', 'Transaction'),
			('html', '1'),
			('message', rowString),
			]
			requests.post('https://api.pushover.net/1/messages.json', data=data)

			# Log transaction to file
			f.write(rowString + '\n')

	# Close transactions log file when done
	f.close()

# what time did this python script start
starttime=time.time()
while True:
  # print current time
  print time.ctime()
  # run the main function
  Transactions(league, pushover_token, pushover_api)
  # log most recent run time
  touch('lastrun.txt')
  # repeat every 60 seconds
  time.sleep(60.0 - ((time.time() - starttime) % 60.0))
