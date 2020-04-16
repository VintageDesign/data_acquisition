import urllib.request
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

        "ips4_IPSSessionFront":"n18ogbcud4ddsiu65gq4gfg995",
        "ips4_ipsTimezone":"America/Denver",
        "ips4_hasJS":"true",
        "laravel_session":	"eyJpdiI6IkpcL0RRNWRQckxEdTZMVFpkbW5MTStBPT0iLCJ2YWx1ZSI6IkdqeWdYQU1uZ0JZbGw0UWZOdWFrbUJ0elVhODVOQ3ZMZnpiUVA1eTVRTW9aN3d3UzFVUHE0bExFdmVTYnc0OVdPM3ZVMWlZQzhpd2FweVNJS1BaalZ3PT0iLCJtYWMiOiIwZDFmMzQwYjc4MTdhNzBlNzczNzgxOTc5MTk0OWJkODBkMzg0ZjliNjhhZjc3NDRjYjU0NDY1ODAwMjMzNzI3In0%3D"
        }

with open('covid_data_otherboard.csv', 'w') as csvfile:

    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(['author', 'profile_href', 'location', 'date_time', 'comment_text'])

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
                    comment_text = comment.div.div.div.next_sibling.next_sibling.div.get_text()
                    date_time = comment.div.div.div.p.next_sibling.next_sibling.a.time['title']

                    author = comment.aside.h3.strong.a.string

                    writer.writerow([author, profile_href, location, date_time, comment_text])
                    people.add((author, profile_href))


table = [] # [ (name, [reviewers]), ...]

for person in people:
    href = person[1]
    fp = requests.get(href,cookies=cookies)
    data= fp.text

    inner_soup = BeautifulSoup(data, 'html.parser')

    try:
        reviews = inner_soup.body.find_all('div',recursive=False)[4].find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1].find_all('div',recursive=False)[-1].table.tbody('tr')
    except AttributeError:
        reviews = None

    names = []
    if reviews is not None:
        for review in reviews:
            if review['class'][0] == 'normal-row':
                name = review.find_all('td')[1].a.string
                names.append(name)
        table.append((person[0], names))


nodes = set()
for person in table:
    people = person[1]
    people.append(person[0])
    for node in people:
        nodes.add(node)

print("There are ", len(nodes), " Nodes")

nodeSet = list(nodes)
connections = []

for person in table:
    start = nodeSet.index(person[0])
    people = person[1]
    for user in people:
        end = nodeSet.index(user)
        if start != end:
            connections.append((start, end))

g = igraph.Graph(connections)
g.vs['label'] = nodeSet
igraph.plot(g, labels=True, bbox=(2000,2000))

