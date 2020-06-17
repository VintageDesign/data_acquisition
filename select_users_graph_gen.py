import urllib.request
from progress.bar import ChargingBar
import cairo
import igraph
import requests
import csv
import numpy as np
from  bs4 import  BeautifulSoup
from datetime import datetime

import json


cookies= {

        "ips4_IPSSessionFront":"mk5n7u1aspebap32kutdc5uvm4",
        "ips4_ipsTimezone":"America/Denver",
        "ips4_hasJS":"true",
        "laravel_session":"eyJpdiI6IlFuaGNMSmpjWGJTeW5EUUdrNHh3bHc9PSIsInZhbHVlIjoiVnR0YTA3ZXpcL044eTByRjIybzlMRDArMjJIMEF3KzhlenBsaTVuRWxTeE14eTQzQ2pLUEZrRnBnQW0yckE4YlpKVW9GajlxQVdxaDNvZDEreHlOVWhBPT0iLCJtYWMiOiIzNzZhM2U2NzQ3N2FmYjY4ODI5NTNlYTUwZDBiNjk5NzU4YjhiN2FmYmRlY2ZhNWQ5MzdjMWRlMWQ5ZmQ4MDBkIn0%3D"
        }

user_link_t = []
with open('covid_graph.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file, delimiter='|', quotechar='"')
    for row in reader:
        user_link_t.append((row['author'], row['Profile']))
print('Links parsed')



################################################################################
# 2019
################################################################################

people = [] # [ (user_name, [reviewers]),...]
personal_info = {} # { user_name: provider_flag }

start_date = datetime(2019, 2, 28)
end_date   = datetime(2019, 5, 10)

bar = ChargingBar("Gathering Connections 2019" , max=len(user_link_t))

for user in user_link_t:
    bar.next()
    base_url = user[1]

    fp = requests.get(base_url,cookies=cookies)
    data= fp.text

    inner_soup = BeautifulSoup(data, 'html.parser')
    try:
        base = inner_soup.body.find_all('div',recursive=False)[4].find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1].find_all('div',recursive=False)[-1].table
    except IndexError:
        print(base_url)
        break



    try:
        buyerFlag = base.thead.tr.find_all('th')[1].string
        reviews   = base.tbody('tr')
    except AttributeError:
        reviews = None
        buyerFlag = None

    if buyerFlag == None or buyerFlag.strip() == "Provider":
        buyerFlag = True
    else:
        buyerFlag = False

    personal_info[user[0]] = buyerFlag



    names = []

    # Gets the First Page of 'connections'
    if reviews is not None:
        for review in reviews:
            if review['class'][0] == 'normal-row':
                date = review.find_all('td')[-1].string
                date = datetime.strptime(date, '%m/%d/%y')

                if date < end_date and date > start_date:
                    name = review.find_all('td')[1].a.string
                    names.append(name)
                    personal_info[name] = not buyerFlag

    # If there are more pages of 'connections' we can grab them like this
    quit = True
    index = 1
    while quit != False:
        if base_url[-1] == '/':
            url = base_url + "reviews/p?p=" + str(index)
        else:
            url = base_url + "/reviews/p?p=" + str(index)
        index += 1

        fp = requests.get(url,cookies=cookies)
        try:
            page = json.loads(fp.text)
        except json.decoder.JSONDecodeError:
            print(url)
            #print(fp.text)
            break
        quit =  page['hasMore']
        page_data = page['html']

        if len(page_data) > 0:
            page_data = page_data.replace("\t", "")
            page_data = page_data.replace("\n", "")
            soup = BeautifulSoup(page_data, 'html.parser')
            for review in soup:
                if review['class'][0] == 'normal-row':
                    date = review.find_all('td')[-1].string
                    date = datetime.strptime(date, '%m/%d/%y')

                    if date < end_date and date > start_date:
                        name = review.find_all('td')[1].a.string
                        names.append(name)
                        personal_info[name] = not buyerFlag

    people.append((user[0], names))


connections = []
color = []
indicies = []
user_indexs = list(personal_info.keys())


with open('user_index_2019.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(['name', 'index', 'buyer'])
    for user, flag in personal_info.items():
        writer.writerow([user, user_indexs.index(user), flag])

for user in people:
   start = user_indexs.index(user[0])
   hookers = user[1]
   for hooker in hookers:
       end = user_indexs.index(hooker)
       connections.append((start, end))

for user, flag in personal_info.items():
    if flag: #Buyer
        color.append('lightblue')
    else: # Seller
        color.append('orange')

    indicies.append(user_indexs.index(user))


g = igraph.Graph(connections)
g.vs['label'] = indicies
g.vs['color'] = color
g.layout('lgl')
igraph.plot(g, "select_users_2019.png", labels=True, bbox=(1000,1000))
print("")
print("Nodes: ", len(personal_info))

################################################################################
# 2020
################################################################################

people = [] # [ (user_name, [reviewers]),...]
personal_info = {} # { user_name: provider_flag }

start_date = datetime(2020, 2, 28)
end_date   = datetime(2020, 5, 10)

bar = ChargingBar("Gathering Connections 2020" , max=len(user_link_t))

for user in user_link_t:
    bar.next()
    base_url = user[1]

    fp = requests.get(base_url,cookies=cookies)
    data= fp.text

    inner_soup = BeautifulSoup(data, 'html.parser')
    try:
        base = inner_soup.body.find_all('div',recursive=False)[4].find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1].find_all('div',recursive=False)[-1].table
    except IndexError:
        print(base_url)
        break



    try:
        buyerFlag = base.thead.tr.find_all('th')[1].string
        reviews   = base.tbody('tr')
    except AttributeError:
        reviews = None
        buyerFlag = None

    if buyerFlag == None or buyerFlag.strip() == "Provider":
        buyerFlag = True
    else:
        buyerFlag = False

    personal_info[user[0]] = buyerFlag



    names = []

    # Gets the First Page of 'connections'
    if reviews is not None:
        for review in reviews:
            if review['class'][0] == 'normal-row':
                date = review.find_all('td')[-1].string
                date = datetime.strptime(date, '%m/%d/%y')

                if date < end_date and date > start_date:
                    name = review.find_all('td')[1].a.string
                    names.append(name)
                    personal_info[name] = not buyerFlag

    # If there are more pages of 'connections' we can grab them like this
    quit = True
    index = 1
    while quit != False:
        if base_url[-1] == '/':
            url = base_url + "reviews/p?p=" + str(index)
        else:
            url = base_url + "/reviews/p?p=" + str(index)
        index += 1

        fp = requests.get(url,cookies=cookies)
        try:
            page = json.loads(fp.text)
        except json.decoder.JSONDecodeError:
            print(url)
            #print(fp.text)
            break
        quit =  page['hasMore']
        page_data = page['html']

        if len(page_data) > 0:
            page_data = page_data.replace("\t", "")
            page_data = page_data.replace("\n", "")
            soup = BeautifulSoup(page_data, 'html.parser')
            for review in soup:
                if review['class'][0] == 'normal-row':
                    date = review.find_all('td')[-1].string
                    date = datetime.strptime(date, '%m/%d/%y')

                    if date < end_date and date > start_date:
                        name = review.find_all('td')[1].a.string
                        names.append(name)
                        personal_info[name] = not buyerFlag

    people.append((user[0], names))


connections = []
color = []
indicies = []
user_indexs = list(personal_info.keys())


with open('user_index_2020.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(['name', 'index', 'buyer'])
    for user, flag in personal_info.items():
        writer.writerow([user, user_indexs.index(user), flag])

for user in people:
   start = user_indexs.index(user[0])
   hookers = user[1]
   for hooker in hookers:
       end = user_indexs.index(hooker)
       connections.append((start, end))

for user, flag in personal_info.items():
    if flag: #Buyer
        color.append('lightblue')
    else: # Seller
        color.append('orange')

    indicies.append(user_indexs.index(user))


g = igraph.Graph(connections)
g.vs['label'] = indicies
g.vs['color'] = color
g.layout('lgl')
igraph.plot(g, "select_users_2020.png", labels=True, bbox=(1000,1000))
print("")
print("Nodes: ", len(personal_info))
print("Done")

