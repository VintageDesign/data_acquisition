import urllib.request
from progress.bar import ChargingBar
from igraph.drawing.text import TextDrawer
import cairo
import igraph
import requests
import csv
import numpy as np
from  bs4 import  BeautifulSoup

people = set()

cookies= {

        "ips4_IPSSessionFront":"q68lq49hgrr7u8fkfamqssc4q2",
        "ips4_ipsTimezone":"America/Denver",
        "ips4_hasJS":"true",
        "laravel_session":"yJpdiI6IndnbEV0ZzVaeU9YQTcwUE9HYXZLMHc9PSIsInZhbHVlIjoiU3dCMVN2eGcxNXZYWlJubHVcL1FONmIyOTE4NnNlbUJBakhlbDlQN3FQY05GbHBwWld4eVdmdDB2emZOYzBtK0tQMHdZVUVseXdZQlowOFJSUTFsUTZRPT0iLCJtYWMiOiIzMDdjMzJkNTk4YzM3NWVkZmQzMmRmMTgyZDg2NjkyMmFmMTYyNDczMDRlZDFhYzhkMjM2OGIzYzc0MTE1NGIxIn0%3D"
        }

user_link_t = []
with open('covid_graph.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file, delimiter='|', quotechar='"')
    for row in reader:
        if 'Yes' in row['Get all comments']:
            user_link_t.append((row['author'], row['Forum']))
print('Links parsed')

auth_list = set()
with open('covid_data_otherboard.csv', 'w') as csvfile:

    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(['author', 'date_time','title' ,  'comment_text'])


    with ChargingBar("Getting all comments for " + str(len(user_link_t)) + " Users", max=len(user_link_t)) as bar:
            for user in user_link_t:
                fp = requests.get(user[1],cookies=cookies)
                data= fp.text
                comments = BeautifulSoup(data, 'html.parser')
                for comment in comments.find_all('li'):
                    bar.next()
                    try:
                        if "ipsClearfix" in comment.div['class']:
                            title = comment.div.div.div.h2.a.string
                            content = comment.div.find_all('div', recursive=False)[1].div.div.string
                            date_time = comment.div.ul.li.a.time['title']
                            writer.writerow([user[0],  date_time,title, content])
                    except (TypeError, KeyError, AttributeError):
                        pass




