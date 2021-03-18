from celery import shared_task
from celery_progress.backend import ProgressRecorder
import requests
from bs4 import BeautifulSoup
import re
urllist = []
import time
import csv
content=""
@shared_task(bind=True)
def ProcessDownload(self, urllist):

	print('Task started')
	progress_recorder = ProgressRecorder(self)
	filename = "%s.csv" % ProcessDownload.request.id

	print('Start')

	with open("%s" % (filename), "w+") as f:
		writer = csv.writer(f, dialect=csv.excel)
		max = len(urllist)
		itemind = 0
		for i in range(0, len(urllist)):
			try:
				if itemind == max:
					break
				s = get_page(urllist[i], writer)
				data, flag = gdd(s, 0)
				write_csv(data, urllist[i], writer)
				itemind += 1
				time.sleep(.1)
				progress_recorder.set_progress(i, len(urllist), description="Downloading")
			except Exception as e:
				itemind += 1
				print(e)
				time.sleep(0.1)
				progress_recorder.set_progress(i, len(urllist), description="Downloading")
				print("ERROR EIDA")
	print('End')

	return 'Completed'

def get_page(url, writer):
	response = requests.get(url)
	soup=""
	if not response.ok:
		row = ["0", "0", "0", url]
		writer.writerow(row)
		print(response.status_code, url)
	else:
		try:
			soup = BeautifulSoup(response.text, 'html.parser')
		except:
			print("soup error")
	return soup


def gdd(soup, flag):
	print("I, Pl")

	try:
		titles = soup.find_all('h1', id='itemTitle')
		st = str(titles)
		mins = st.find('</span>')
		maxs = st.find('</h1>')
		title = str(st[mins + 7:maxs])

	except:
		title = ''

	try:
		prices = soup.find('span', id='prcIsum')
		pt = str(prices)
		if (pt == "None"):
			prices = soup.find('span', id='mm-saleDscPrc')
			pt = str(prices)
			mins = pt.find('$')
			maxs = pt.find('</span>')
			price1 = str(pt[mins:maxs])
		else:
			mins = pt.find('$')
			maxs = pt.find('</span>')
			price1 = str(pt[mins:maxs])
		# price = re.findall('\d*\.?\d+', price1)[0]
		price = re.findall('[0-9]+,*.*\d*', price1)[0]
		price = str(price)

	except:
		price = ''
	content=""
	try:
		content = str(soup)

		try:
			mins = content.find('available.')
			avail = (content[mins - 10:mins + 5])

			try:
				available = re.findall('\d*\.?\d+', avail)[0]
				qty = str(available)
			except:
				mins = content.find('items available.')
				avail = (content[mins - 10:mins + 5])
				available = re.findall('\d*\.?\d+', avail)[0]
				qty = str(available)

		except:
			avai = str(soup.find_all('span', id='qtySubTxt'))

			max = avai.find('available')
			available = str(avai[max - 20:max])
			availables = re.findall('\d*\.?\d+', available)[0]
			qty = str(availables)

		if (int(qty) < 3):
			flag = 1
	except:
		qty = ''

	try:
		sshipping = soup.find('span', id='fshippingCost')
		ssst = str(sshipping)

		if (ssst == "None"):
			k = content.find("FAST 'N FREE")
			if k == -1:
				ps = content.find('')
				shipping = ''
			else:
				shipping = "Free"
		else:
			mins = ssst.find('<span>')
			maxs = ssst.find('</span>')
			shipping = str(ssst[mins + 6:maxs])
	except:
		shipping = ' '
	try:
		lines = str(soup)

		try:
			m = re.search(r'(.{3}\. .{3}\. \d{1,2} and .{3}\. .{3}\. \d{1,2})', lines)
			deldate = str(m.group(1))
		except:
			m1 = re.search(r'(.{3}\. .{3}\. \d{1,2})', lines)
			deldate = str(m1.group(1))
	except:
		deldate = ''

	try:
		sellername = ''
		mydivs = soup.find("div", {"class": "mbg vi-VR-margBtm3"})
		total = str(mydivs)
		min = total.find('usr/')
		max = total.find('trks')

		sellername = (total[min + 4:max - 2])
	except:
		sellername = ''

	try:
		sellerfeedback = ''
		mydivss = soup.find("span", {"class": "mbg-l"})
		totals = str(mydivss)
		min = totals.find("title=\"feedback score:")
		max = totals.find("</a")
		t = totals[min:max]
		p = t.find('>')
		feedbackscore = str(t[p + 1:])
		if (int(feedbackscore) < 200):
			flag = 1

	except:
		feedbackscore = ''

	try:
		rating = ''
		mydivs = soup.find("div", {"id": "si-fb"})
		total = str(mydivs)
		ratings = re.findall('\d*\.?\d+', total)[0]
		rating = str(ratings)
		if (float(rating) < 98.00):
			flag = 1
	except:
		rating = ''
	data = {
		'title': title,
		'price': price,
		'qty': qty,
		'shipping': shipping,
		'deldate': deldate,
		'sellername': sellername,
		'feedbackscore': feedbackscore,
		'rating': rating
	}
	return data, flag


def write_csv(data, url, writer):
	print(url)
	xs = url.find('?')
	url = str(url[:xs])
	pidind = url.rfind('/')
	pid = str(url[pidind + 1:])
	# imgCollector(url,pid)
	row = [data['price'], data['shipping'], data['qty'], pid]
	print(row)
	writer.writerow(row)


def get_index_data(soup):
	try:
		links = soup.find_all('a', class_='s-item__link')
	except:
		links = []
	urls = [item.get('href') for item in links]
	return urls
