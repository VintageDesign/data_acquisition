import urllib.request
from progress.bar import ChargingBar
from igraph.drawing.text import TextDrawer
import cairo
import igraph
import requests
import csv
import numpy as np
from  bs4 import  BeautifulSoup

fp = urllib.request.urlopen("https://theotherboard.com/forum/index.php?/forum/28-general-discussion/")
mybytes = fp.read()

data = mybytes.decode("utf8")
fp.close()

soup = BeautifulSoup(data, 'html.parser')
people = set()

cookies= {

        "ips4_IPSSessionFront":"b7gt46bq53fiqsvcabid5q9f01",
        "ips4_ipsTimezone":"America/Denver",
        "ips4_hasJS":"true",
        "laravel_session":"eyJpdiI6IkVQaUJoOG0wT0VrYmk3NXlPYVBtZGc9PSIsInZhbHVlIjoiY0xhVmdhRGZHTW8zV2lURWxcL2lTeDRmWDZGZFRoSVR2ZlwvOFM5NTBrRlwvdnhpVlVsU3JmNWYzWmZkdENIVmdUQzRCZFhiXC9seFYyN2RuNjZ2WG5Ccnp3PT0iLCJtYWMiOiIwNGIzZjQ3ZjdlZDk5ZTllZDYyM2U3MmQ2YzIzNTFiNWJjMmNkZDVjYTNhNzIxZmE0ZjVkZTY5NzYwOGM4ZDg2In0%3D"
        }

auth_list = set()
with open('all_comments.csv', 'w') as csvfile:

    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(['author', 'profile_href', 'location', 'date_time', 'forum_title',  'comment_text'])

    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None:
            if "corona" in href.lower() or "covid" in href.lower():
                fp = urllib.request.urlopen(href)
                mybytes = fp.read()

                data = mybytes.decode("utf8")
                fp.close()

                inner_soup = BeautifulSoup(data, 'html.parser')


                for comment in inner_soup.find_all('article'):
                    profile_href = comment.aside.ul.find_all('li')[-1].a['href']
                    location = comment.aside.ul.find_all('li')[-2].span
                    if location is not None:
                        location = location.next_sibling.next_sibling.get_text()
                    else:
                        location = "N/A"
                    author = comment.aside.h3.strong.a.string
                    if author not in auth_list:
                        auth_list.add(author)

                        fp = requests.get(profile_href,cookies=cookies)
                        data= fp.text

                        inner_inner_soup = BeautifulSoup(data, 'html.parser')

                        stats = inner_inner_soup.body.find_all('div', recursive=False)[-1].div.div.div#.section.div.find_all('div',recursive=False)[-1].find_all('a')[-1]['href']
                        if "My Listings" in stats.a.string:
                            stats = inner_inner_soup.body.find_all('div', recursive=False)[-1].div.div.find_all('div', recursive=False)[1].section.div.find_all('div',recursive=False)[-1].find_all('a')[-1]['href']
                        else:
                            stats = inner_inner_soup.body.find_all('div', recursive=False)[-1].div.div.div.section.div.find_all('div',recursive=False)[-1].find_all('a')[-1]['href']
                        fp = requests.get(stats,cookies=cookies)
                        data= fp.text

                        comments = BeautifulSoup(data, 'html.parser')

                        with ChargingBar(author, max=len(comments.find_all('li'))) as bar:
                            for comment in comments.find_all('li'):
                                bar.next()
                                try:
                                    if "ipsClearfix" in comment.div['class']:
                                        title = comment.div.div.div.h2.a.string
                                        content = comment.div.find_all('div', recursive=False)[1].div.div.string
                                        date_time = comment.div.ul.li.a.time['title']
                                        writer.writerow([author, stats, location, date_time,title, content])
                                except (TypeError, KeyError, AttributeError):
                                    pass




