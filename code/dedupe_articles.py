#!/usr/bin/python3

import sys
import json
import csv


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


article_titles = []

headers = []
comp_head = ['topic', 'title', 'date', 'url']

counter = 0
with open(sys.argv[1], 'r') as fin:
    creader = csv.reader(fin)
    for line in creader:
        if counter % 100 == 0:
            eprint("\t\tcounter -- %d" % counter)
        arr = line 
        obj = {}
        if counter == 0 or arr == comp_head:
            headers = arr
        else:
            sub_counter = 0
            for head in headers:
                obj[head] = arr[sub_counter] 
                sub_counter += 1
        counter += 1
        if obj:
            if obj['title'] not in article_titles:
                print(json.dumps(obj))
                article_titles.append(obj['title'])
        line = fin.readline()
