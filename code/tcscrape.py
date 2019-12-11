from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from newspaper import Article
from urllib.parse import unquote
import json
import csv
import traceback
from multiprocessing import Pool


import requests

def resolve_url(base_url):
    r = requests.get(base_url)
    return r.url

def chase_redirects(url):
    while True:
        r = requests.head(url)
        if 300 < r.status_code < 400:
            url = r.headers['location']
        else:
            break
    return url


def getresults(term):
    res = []
    urls = set([])
    driver = webdriver.Firefox()
    driver.get("https://techcrunch.com/")

    driver.find_element_by_class_name('search-box-container').click()

    inputElement = driver.find_element_by_id("search-box-form__input")
    inputElement.send_keys(term)
    inputElement.send_keys(Keys.ENTER)

    global_cnt = 0
    while(True):
        time.sleep(5)

        search_url = []
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            try:
                url = elem.get_attribute("href")
                if "search.techcrunch.com" in url:
                    search_url.append(url)
                # url = resolve_url(chase_redirects(url))
                url = url.split("RU=")[1]
                url = url.split("/RK=")[0]
                url = unquote(url)
                article = Article(url)
                article.download()
                article.parse()
                if article.publish_date:
                    if url not in urls:
                        urls.add(url)
                        print(url)
                        print(article.title, article.publish_date)
                        res.append({"topic":term,"title":article.title,"date": article.publish_date, "url": url})
            except:
                traceback.print_exc()
        # break
        #try:
        a = driver.find_element_by_class_name('next')
        if not a:
            break
        else:
            if global_cnt < 3:
                a.click()
                global_cnt += 1
            else:
                try:
                    driver.get(search_url[-4])
                    global_cnt +=1
                except:
                    traceback.print_exc()
                    break

    driver.close()
    
    toCSV = res
    keys = toCSV[0].keys()
    with open(term+'.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)
    


allterms = ['ios']

#allterms = ['Gear360',
# 'NintendoSwitch',
# 'android',
# 'ios',
# 'macos',
# 'osx',
# 'playstation',
# 'ubuntu',
# 'windows',
# 'xbox']

# for a in allterms:
#     getresults(a)

pool = Pool(len(allterms))
pool.map(getresults, allterms)
pool.close() 
pool.join()

