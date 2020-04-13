import requests
import re
import csv
from bs4 import BeautifulSoup
import urllib.parse

class ScrapeGoogle:

	def __init__(self,domain):
		self.urls=[]
		self.url = "https://www.google.com/search"
		self.headers= {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5'}
		#using google dorking to find sites that holds company's Email adresses:
		self.params={
			"q": f"site:{domain} intext:@{domain}",
			"oq": f"site:{domain} intext:@{domain}",
		}


	#makes the first search request:
	def FirstRequest(self):
		res = requests.get(self.url, params=self.params, headers=self.headers)
		return res.text

	#scrapes Google and gathers the links into a list:
	def scraping_google(self,html):
		soup = BeautifulSoup(html, 'html.parser')
		#select the company's url:
		for url in soup.select('div.g div.r > a:nth-of-type(1)'):
			#skip over translation links:
			if 'translate.google.com' not in url['href']:
				self.urls.append(url['href'])


	#imitates clicking the "next page" button to prevent blocking:
	def nextpage(self, html):
		soup = BeautifulSoup(html, 'html.parser')
		link=soup.select_one("#pnnext")
		#get the next page url:
		getlink=str(link).split('href="')[1].split('"')
		finallink=urllib.parse.unquote(getlink[0])
		url=f'https://www.google.com{finallink}'
		#make a search request with the next page url:
		res=requests.get(url, params=self.params, headers=self.headers)
		scrap=res.text
		#scrape the new page and gathers the links into the list:
		self.scraping_google(scrap)
		#continue scraping google pages until you get 50 links:
		if len(self.urls)!=50:
			self.nextpage(scrap)
		else:
			self.getMails()

	#get Email adresses from the url list:
	def getMails(self):
		emailslist=[]
		for x in self.urls:
			response=requests.get(x)
			y=response.text
			email=re.findall("[a-zA-Z0-9_.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", y)
			for adress in email:
				if adress not in emailslist:
					emailslist.append(adress)
		#export Email adresses to csv file:
		with open('Emails_found.csv', 'w') as Email_file:
			file_writer = csv.writer(Email_file)
			file_writer.writerow(["Email Adress"])
			for Email in emailslist:
				file_writer.writerow([Email])
			print("the file has been created")

def main():
	domain=input("insert domain adress: ")
	if "www." in domain:
		domain=domain.split("www.")[1]
	google= ScrapeGoogle(domain)
	google.scraping_google(google.FirstRequest())
	google.nextpage(google.FirstRequest())


main()
