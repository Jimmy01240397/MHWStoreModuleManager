#!/bin/python3

import requests
import sys
import re
import os
import concurrent.futures
from absl import app, flags
from bs4 import BeautifulSoup

exefile = __file__
if os.path.islink(exefile):
    exefile = os.path.realpath(exefile)

os.chdir(os.path.dirname(os.path.abspath(exefile)))

location = 'common/facility'

wikiurl = 'https://mhworld.kiranico.com'
idurl = 'https://mhw.poedb.tw/cht/rawitems'

allsearchresult = []

def nametoid(name):
    global allsearchresult
    apikey = re.search('(?<=apiKey: )"[a-z0-9]+"', requests.get(wikiurl).text).group(0).replace('"', '')
    searchdata = {"q": name,"attributesToHighlight":["*"],"attributesToCrop":["content"],"cropLength":30}
    languagelist = re.findall('<a href="https://mhworld.kiranico.com/([a-zA-Z\-]+)">.+</a>', requests.get(f'{wikiurl}/en').text)

    allsearchresult = []

    def searchwiki(lenguage):
        global allsearchresult
        searchresult = requests.post(f'https://search.kiranico.gg/indexes/mhworld_{lenguage}_docsearch/search', headers={'Authorization': f'Bearer {apikey}'}, json=searchdata)
        allsearchresult += searchresult.json()['hits']

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(languagelist)) as executor:
        executor.map(searchwiki, languagelist)

    print("select your target:")
    for i, a in enumerate(allsearchresult):
        print(f"{i}: {a['lvl2']}")

    while True:
        try:
            index = int(input('> '))
            assert index < len(allsearchresult)
            break
        except KeyboardInterrupt:
            print('Canceled')
            sys.exit(1)
        except:
            pass

    enname = BeautifulSoup(requests.get(BeautifulSoup(re.search('<a href=".*?">English</a>', requests.get(f"{wikiurl}{allsearchresult[index]['url']}").text).group(0), 'html.parser').a['href']).text, 'html.parser').find_all("div", class_="align-self-center")[0].string

    rows = re.findall('<tr><td>([0-9]+?)<td>[0-9]+?<td>[0-9]+?<td>[0-9]+?<td>([^<]+)', requests.get(idurl).text)
    data = {key: value for value, key in rows}
    return int(data[enname])



def idtopage(id):
    id -= 1
    print(f"Shop List Index: {int(id / 255)}")
    print(f"Shop Page: {int((id % 255) / 11) + 1}")
    print(f"Item index in Shop Page: {((id % 255) % 11) + 1}")
    return int(id / 255)

def reset():
    if os.path.isfile(os.path.join(location, 'shopList.slt')):
        for a in range(11):
            if not os.path.isfile(os.path.join(location, f'shopList_{str(a).zfill(2)}.slt')):
                os.rename(os.path.join(location, 'shopList.slt'), os.path.join(location, f'shopList_{str(a).zfill(2)}.slt'))
                break

def main(argv=()):
    page = -1
    rundirectly = False
    if args.page != -1:
        page = args.page
    elif args.id != -1:
        page = idtopage(args.id)
    elif args.name != '':
        page = idtopage(nametoid(args.name))
    elif args.reset:
        pass
    else:
        rundirectly = True
        name = input('Please enter your search item name: ')
        page = idtopage(nametoid(name))

    reset()
    if page != -1:
        os.rename(os.path.join(location, f'shopList_{str(page).zfill(2)}.slt'), os.path.join(location, 'shopList.slt'))
    
    if rundirectly:
        input("Press Enter to continue...")

flags.DEFINE_string('name', '', 'Item name')
flags.DEFINE_integer('id', -1, 'Item id')
flags.DEFINE_integer('page', -1, 'Store page')
flags.DEFINE_boolean('reset', False, 'Reset module')
args = flags.FLAGS
app.run(main)



