#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Goodreads Analyzer 1.1
#
# apt-get install python-requests python-matplotlib
#
# https://www.goodreads.com/shelf/show/cyberpunk (p.1-25)
# https://www.goodreads.com/shelf/show/science-fiction (p.1-25)
# https://www.goodreads.com/list/show/19341.Best_Science_Fiction (p.1-29)
#

import sqlite3,requests,StringIO,lxml.html,argparse,numpy,time,sys,re
import matplotlib.pyplot as plt
#from matplotlib.ticker import FixedLocator
from numpy import mean

FIREFOX='/home/user/.mozilla/firefox/2wfpvx7b.default/cookies.sqlite'

GOOD='https://www.goodreads.com'

#SHELF = GOOD + '/shelf/show/cyberpunk'
#SHELF = GOOD + '/shelf/show/science-fiction'
SHELF = GOOD + '/list/show/19341.Best_Science_Fiction'
LAST_PAGE = 29

#OUTFILE='cyber-dataset.csv'
#OUTPNG='popular-cyberpunk-all.png'

#OUTFILE='scifi-dataset.csv'
#OUTPNG='popular-scifi-all.png'

OUTFILE='best-scifi-dataset.csv'
OUTPNG='best-scifi-all.png'

#--------------------------------------

parser = argparse.ArgumentParser(description='Goodreads Analyzer 1.1')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--scrap', help='Scrap HTML data.', action='store_true')
group.add_argument('--plot', help='Plot scrap from CSV file.', action='store_true')
group.add_argument('--filter', help='Filter data from CSV file.', action='store_true')
args = parser.parse_args()

#--------------------------------------

print('Goodreads Analyzer 1.0\n')

if args.scrap:

	# COOKIE
	#
	# https://goodreads.com -> Remember login -> Login -> Quit

	COOKIES={}

	try:
		conn = sqlite3.connect(FIREFOX)
		cur = conn.cursor()
		cur.execute("SELECT name,value FROM moz_cookies WHERE host = 'www.goodreads.com'")
		rows = cur.fetchall()
		for name,value in rows: COOKIES[name] = value
	except:
		print('Failed to get cookies.')
		sys.exit(1)

	# SCRAP & PARSE

	print('Scraping data .. (this may take a while)\n')

	DATASET = {}

	session = requests.Session()

	for i in range(1, LAST_PAGE + 1):
		print('Page: ' + str(i))
		req = session.get(SHELF + '?page=' + str(i), cookies=COOKIES)
		if req.status_code == 200:
			#p = lxml.html.HTMLParser()
			#t = lxml.html.parse(StringIO.StringIO(req.text), p)
			#o = t.xpath("//div[@class='elementList']")

			# "Best SF" modified parsing
			#
			p = lxml.html.HTMLParser()
			t = lxml.html.parse(StringIO.StringIO(req.text), p)
			o = t.xpath("//tr[@itemtype='http://schema.org/Book']")

			for i in range(0,len(o)):

			#	book = o[i].xpath(".//a[@class='bookTitle']")
			#	if book:
			#		book_title = book[0].text.encode('utf-8')
			#		book_url = book[0].get('href').encode('utf-8')
			#		book_id = re.sub('.*/(\d+).*', '\\1', book_url)

			#	author = o[i].xpath(".//a[@class='authorName']//span")
			#	if author:
			#		book_author = author[0].text.encode('utf-8')

			#	data = o[i].xpath(".//span[@class='greyText smallText']")
			#	if data:
			#		book_avg = re.findall('avg rating.*', data[0].text)
			#		book_ratings = re.findall('.*ratings', data[0].text)
			#		book_published = re.findall('published.*', data[0].text)
				
			#	DATASET[book_id] = {
			#		'title':book_title.replace(';',' -'),
			#		'author':book_author,
			#		'url':book_url,
			#		'avg': re.sub('avg rating (.*) .*', '\\1', book_avg[0]),
			#		'ratings':re.sub('(.*) ratings.*', '\\1', book_ratings[0]).replace(',','').strip(),
			#		'year':re.sub('published (.*)', '\\1', book_published[0]).strip()
			#	}

				# "Best SF list" modified parsing
				#
				book = o[i].xpath(".//a[@class='bookTitle']//span")
				if book:
					book_title = book[0].text.encode('utf-8')
				#
				url = o[i].xpath(".//a[@class='bookTitle']")
				if url:
					book_url = url[0].get('href').encode('utf-8')
					book_id = re.sub('.*/(\d+).*', '\\1', book_url)
				#
				author = o[i].xpath(".//a[@class='authorName']//span")
				if author:
					book_author = author[0].text.encode('utf-8')
				#
				data = o[i].xpath(".//span[@class='greyText smallText uitext']//span[@class='minirating']/text()")
				if data:
					book_avg = re.sub('(.*) avg.*', '\\1', data[0]).strip()
					book_ratings = re.sub(u'.*\u2014(.*)ratings$', '\\1', data[0]).replace(',','').strip()
				#
				DATASET[book_id] = {
					'title':book_title.replace(';',' -'),
					'author':book_author,
					'url':book_url,
					'avg':book_avg,
					'ratings':book_ratings
				}

		# hold on a second..
		time.sleep(1)

	print('\nDone.')

	# WRITE DATASET

	with open(OUTFILE, 'a') as f:
		for BOOK in DATASET:
			f.write(

				str(BOOK) + ';' +
				DATASET[BOOK]['title'] + ';' +
				DATASET[BOOK]['author'] + ';' +
				DATASET[BOOK]['url'] + ';' +
				DATASET[BOOK]['avg'].encode('utf-8') + ';' +
				#DATASET[BOOK]['ratings'].encode('utf-8') + ';' +
				#DATASET[BOOK]['year'].encode('utf-8') + '\n'

			# "Best SF" modified parsing
			#
				DATASET[BOOK]['ratings'].encode('utf-8') + '\n'
			)

if args.filter:

	# LOAD DATASET

	DATASET={}

	try:
		with open(OUTFILE, 'r') as f:
			for line in f:
				record = line.split(';')
				DATASET[record[0]] = {
					'title':record[1],
					'author':record[2],
					'url':record[3],
					'avg':record[4],
					'ratings':record[5],
					'year':record[6].strip()
				}
	except:
		print('Failed to load dataset.')
		sys.exit(1)

	# MEAN AVERAGE RATING
	print('  AVG (mean): '  + str(mean([float(DATASET[book]['avg']) for book in DATASET])))

	# MEAN RATING COUNT
	print('COUNT (mean): ' + str(mean([int(DATASET[book]['ratings']) for book in DATASET])))

if args.plot:

	# LOAD DATASET

	DATASET={}

	try:
		with open(OUTFILE, 'r') as f:
			for line in f:
				record = line.split(';')
				DATASET[record[0]] = {
					'title':record[1],
					'author':record[2],
					'url':record[3],
					'avg':record[4],
					'ratings':record[5],
					'year':record[6].strip()
				}
	except:
		print('Failed to load dataset.')
		sys.exit(1)

	# CLEANUP

	#exclude "Shadowrun"
	for BOOK in list(DATASET):
		if re.match('.*Shadowrun.*', DATASET[BOOK]['title']):
			del DATASET[BOOK]

	print('Generating plot .. (this may take a while)')

	# PLOT

	fig, ax = plt.subplots(figsize=(8,7))

	for BOOK in DATASET:
		# COLOR BY YEAR
		book_year = DATASET[BOOK]['year']
		if not book_year:
			COLOR = '#F38460'
		else:
			if int(book_year) < 1975: COLOR = '#008856'
			if int(book_year) >= 1975 and int(book_year) < 2003: COLOR = '#F3C300'
			if int(book_year) >= 2003 and int(book_year) < 2010: COLOR = '#A1CAF1'
			if int(book_year) >= 2010: COLOR = '#C2B280'

		# SCATTER
		plt.plot(
			int(DATASET[BOOK]['ratings'].replace(',','')),
				float(DATASET[BOOK]['avg']),
				'o',
				markeredgewidth = 1.5,
				markeredgecolor = 'black',
				markerfacecolor = COLOR,
				markersize = 7		
			)

	# MEAN OF RATING AVERAGE
	plt.axhline(y=mean([float(DATASET[book]['avg']) for book in DATASET]), linewidth=2, color='k')

	# MEAN OF RATING COUNT
	plt.axvline(x=mean([int(DATASET[book]['ratings']) for book in DATASET]), linewidth=2, color='k')

	#  TUNE

	plt.title('Goodreads - Popular Cyberpunk', fontsize=14)

	plt.xlabel('Number of ratings', fontsize=13)
	plt.ylabel('Average Rating', fontsize=13)

	plt.grid(True)

	plt.ticklabel_format(useOffset=True)

	#plt.xlim(left=10000)
	plt.xlim(100000,1000000)

	plt.ylim(3,5)

	# CREATE IMAGE
	plt.savefig(filename=OUTPNG, format='png', dpi=300)

	plt.close()

# EXIT

sys.exit(0)

