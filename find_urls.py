import urllib.request
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

        "ips4_IPSSessionFront":"vu698a7t6eovk76udpbj93aog1",
        "ips4_ipsTimezone":"America/Denver",
        "ips4_hasJS":"true",
        "laravel_session":	"eyJpdiI6Ik9hRDE2Q2ExRGlhY3JDczkxOEFSaXc9PSIsInZhbHVlIjoib3BhNEs1NDAzMzVoOVlWeGtBNU9MUWpndUlWdjNpQ1wvNklVS3RCeDZHSEp0SnRQMlFmMWhPN1RsYTJVTUxcL3JFQWhCUkRzTnNuVHRpQU9cL2tcL21aUGR3PT0iLCJtYWMiOiJmMGNmMjg1NjM3ZWIwOWRlNzNjOGQ4MjU4M2FjZjViZTBlZTdkZDVlM2EwNjEyMmJlNjVkODNhZGZmMTU2ZGY0In0%3D"
        }

referenceTable = {} # {name:( buyerFlag, numConributions, index), ...}
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

                    if author in referenceTable:
                        stats = referenceTable[author]
                        stats[1] += 1
                    else:
                        stats = [0,1,0]
                    referenceTable[author] = stats



table = [] # [ (name, [reviewers]), ...]

for person in people:
    href = person[1]
    fp = requests.get(href,cookies=cookies)
    data= fp.text

    inner_soup = BeautifulSoup(data, 'html.parser')

    try:
        buyerFlag = inner_soup.body.find_all('div',recursive=False)[4].find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1].find_all('div',recursive=False)[-1].table.thead.tr.find_all('th')[1].string
        reviews = inner_soup.body.find_all('div',recursive=False)[4].find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1].find_all('div',recursive=False)[-1].table.tbody('tr')
    except AttributeError:
        reviews = None
        buyerFlag = None

    try:
        if buyerFlag.strip() == 'Provider':
            buyerFlag = True
        else:
            buyerFlag = False
    except AttributeError:
        buyerFlag = True

    stats = referenceTable[person[0]]
    stats[0] = buyerFlag
    referenceTable[person[0]] = stats

    names = []
    if reviews is not None:
        for review in reviews:
            if review['class'][0] == 'normal-row':
                name = review.find_all('td')[1].a.string
                names.append(name)
        table.append((person[0], names))
    else:
        del referenceTable[person[0]]


nodes = set()
print("ref table ", len(set(referenceTable.keys())))
for person in table:
    people = person[1]
    nodes.add(person[0])
    for node in people:
        nodes.add(node)
        if node not in referenceTable:
            stats = [ not referenceTable[person[0]][0],0,0]
            referenceTable[node] = stats

print("There are ", len(nodes), " Nodes")
print("ref table ", len(set(referenceTable.keys())))


nodeSet = list(nodes)
connections = []

for person in table:
    start = nodeSet.index(person[0])
    if start == 0:
        print(person[0])
    referenceTable[person[0]][2] = start
    people = person[1]
    for user in people:
        end = nodeSet.index(user)
        referenceTable[user][2] = end

        if start != end:
            connections.append((start, end))
contribs = []
flags     = []
index    = []
for person in referenceTable.values():
    contribs.append(person[1]*.5 + 10)
    if person[1]:
        color =  "lightblue"
    else:
        color = "orange"
    flags.append(color)
    index.append(person[2])

    flags = [x for _,x in sorted(zip(index, flags))]
    contribs = [x for _,x in sorted(zip(index, contribs))]
    index = sorted(index)

g = igraph.Graph(connections)
g.vs['label'] = index
g.vs['color'] = flags
g.vs['size']  = contribs
igraph.plot(g, "covid-contrib.png", labels=True, bbox=(2000,2000))

