#!/usr/bin/env python
import re
from mechanize import Browser
from bs4 import BeautifulSoup
import cookielib
import os, sys
import argparse

global nextposturl
delim = "|"

# use this command: 
# python python-scrape.py --limit="20"

prog = re.compile(r'^https?://(?!(?:www\.)?bitcointalk\.org).+')

def extract_article_url(posturl):
	mech = Browser()
	cj = cookielib.LWPCookieJar()

	mech.set_handle_equiv(True)
	#mech.set_handle_gzip(True)
	mech.set_handle_redirect(True)
	mech.set_handle_referer(True)
	mech.set_handle_robots(False)
	#mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
	mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	page = mech.open(posturl)
	html = page.read()

	global soup
	soup = BeautifulSoup(html)

	global articleURL
	#print soup.prettify()

	for item in soup.find_all('div', class_='post'):
		for link in item.find_all('a'):
			string = link.get('href')
			if prog.match(string):
				# find the link that is to the article (link outside of bitcointalk.org forum)
				articleURL = link.get('href')
				return link.get('href')
	return "No article url"

def go_to_next_post():
	global nextposturl
	for tag in soup.find_all('a'):
		if tag.string != None:
			# check to make sure there is text for that link
			string = tag.string
			match = re.search('next topic', string)
			if match: 
			# we found the link to the next post in the forum!                     
	   			nextposturl = unicode(tag.get('href'))
	   			return nextposturl
	   			break

def f_write(f, str):
	f.write(str)

def print_headers():
	f = open('bitcoinReporters.csv', 'w')
	f.write("Article url" + delim)
	#f.write("Next forum post url" + delim)
	f.write("Author" + delim)
	f.write("Positive percentage" + delim)
	f.write("Negative percentage" + delim)
	f.write("\n")
	f.close()

def process_article(posturl):
	f = open('bitcoinReporters.csv', 'a')
	
	f_write(f, extract_article_url(posturl) + delim)
	
	go_to_next_post()

	authorURL = find_author(articleURL)

	if authorURL != None:
		f_write(f, authorURL + delim)
	else:
		f_write(f, "No author found" + delim)

	scrape_article_words()
	analyze_article()

	f_write(f, str(pos_perc) + delim)
	f_write(f, str(neg_perc) + delim)

	f_write(f, "\n")
	f.close()

	if os.path.isfile('bitcoinArticleText.txt'):
		os.remove('bitcoinArticleText.txt')
        # delete the file with the article text so the next article starts clean 

def find_author(articleURL):
	mech = Browser()
	cj = cookielib.LWPCookieJar()

	mech.set_handle_equiv(True)
	#mech.set_handle_gzip(True)
	mech.set_handle_redirect(True)
	mech.set_handle_referer(True)
	mech.set_handle_robots(False)
	#mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
	mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	page = mech.open(articleURL)
	html = page.read()

	global soup
	global authorTag

	soup = BeautifulSoup(html)

	for tag in soup.find_all('a'):
		possiblename = unicode(tag.get('href'))
		# if tag.has_attr('itemprop'):
		# 	if tag['itemprop'] == "name":
		# 		#print tag['itemprop']
		# 	elif tag['itemprop'] == "author":
		# 		#print tag['itemprop']
		# if tag.has_attr('rel'):
		# 	if tag['rel'] == "author":
		# 		#print tag['rel']
		if tag.parent.has_attr('itemprop'):
			if tag.parent['itemprop'] == "name":
				authorTag = tag
				return tag.string
				break
		if re.search(r'author',possiblename):
			if tag.string == None:
				continue
			else:
				authorTag = tag
				return tag.string
			break
		elif re.search(r'/users', possiblename):
			if tag.string == None:
				continue
			else:
				authorTag = tag
				return tag.string
			break
		elif re.search(r'/people', possiblename):
			if tag.string == None:
				continue
			else:
				authorTag = tag
				return tag.string
				break
		elif re.search(r'/contributor', possiblename):
			if tag.string ==None:
				continue
			else: 
				authorTag = tag
				return tag.string
				break


def scrape_article_words():
	authorFound = False
	for tag in soup.find_all():
		# set authorFound to True if there was no authorTag found in the article. 
		# this ensures that scraping with begin at beginning of article if there is no authorTag to initiate scraping.
		if authorTag == None or tag == authorTag:
			# found the author.
			authorFound = True
		if not authorFound:
			# we haven't hit the author tag yet, go to next tag (next iteration of for loop)
			continue
		if tag.string == None:
			continue
		else: 	
			possiblecomments = tag.string.encode("utf-8")
		#if re.search(r'(?i)comments', possiblecomments):
			# we hit the start of the comments section. stop scraping.
			#break
		addText = possiblecomments
		# grab the text associated with that tag
		j = open('bitcoinArticleText.txt', 'a')
	
		f_write(j, addText)
		
		j.close()

def analyze_article():

	try:
		f = open('bitcoinArticleText.txt', 'r')
	except: 
		return

	bitcoinArticleText = str(f.read())
	lowercasetext = bitcoinArticleText.lower()
	clean = re.sub(r'\W', " ", lowercasetext)
	words = re.split(r'\s+', clean)
	total = len(words)

	global pos_perc, neg_perc
	pos = 0
	neg = 0 
	pos_perc = 0
	neg_perc = 0
	
	for word in words:
		if word in pos_words_list:
			pos += 1
		if word in neg_words_list:
			neg += 1

	# DEBUG:
	# if pos < 5 or neg < 5:
	# 	for word in words:
	# 		if word in pos_words_list:
	# 			print "FOUND+:", word
	# 		if word in neg_words_list:
	# 			print "FOUND-:", word
	
	pos_perc = float(pos) / total *100
	neg_perc = float(neg) / total *100
	
def find_first_article():
	mech = Browser()
	cj = cookielib.LWPCookieJar()

	mech.set_handle_equiv(True)
	#mech.set_handle_gzip(True)
	mech.set_handle_redirect(True)
	mech.set_handle_referer(True)
	mech.set_handle_robots(False)
	#mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
	mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	page = mech.open("https://bitcointalk.org/index.php?board=77.0")
	html = page.read()

	soup = BeautifulSoup(html)

	first_article_tag = soup.find("td", class_="windowbg")

	global startingpost
	startingpost = first_article_tag.span.a.get('href')
	print startingpost

def python_scrape():
	repeatPost = False

	print_headers()

	global pos_words_list
	g = open('FT/positive-words.txt')
	pos_words_string = str(g.read())
	pos_words_list = pos_words_string.split()

	global neg_words_list
	h = open('FT/negative-words.txt')
	neg_words_string = str(h.read())
	neg_words_list = neg_words_string.split()

	find_first_article()

	# Process the first article.
	process_article(startingpost)
	print 'Processed article # 1 !'

	articleCount = 1
	while not repeatPost:
		process_article(nextposturl)
		articleCount += 1
		print 'Processed article #', articleCount
		if nextposturl == startingpost:
			repeatPost = True

	# for i in range(0,limit):
	# 	process_article(nextposturl)
	# 	print 'Processed article #', i+2, "!"

if __name__ == "__main__":

	#parser = argparse.ArgumentParser()

	#parser.add_argument('--url', help="starting forum post url")
	#parser.add_argument('--limit', help="number of articles to scrape")
	#args = parser.parse_args()
	#if args.url is None or args.limit is None: 
	#if args.limit is None:
		#print "Please specify limit!"
		#sys.exit(1)
	#python_scrape(args.url, int(args.limit))
	#python_scrape(int(args.limit))
	python_scrape()

