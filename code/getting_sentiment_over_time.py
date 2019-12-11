#!/usr/bin/python

import json
import sys
import csv
import datetime

sent_all = {}


headers = ["ID", "author", "created","score","search","sentiment","sub",
            "text","type","tech", "react"]
counter = 0

clips = {}
with open("clipping_dates.json", "r") as clip_in:
    for line in clip_in.readlines():
        clips = json.loads(line)

for sub, date in clips.items():
    clips[sub] = datetime.datetime.strptime(date, "%m-%d-%Y")


with open(sys.argv[1], 'r') as csvfile:
    creader = csv.reader(csvfile)
    for line in creader:
        obj = {}
        sub_counter = 0
        for head in headers:
            obj[head] = line[sub_counter]
            sub_counter += 1
        
        sub = obj["sub"].strip()
        if sub not in sent_all:
            sent_all[sub] = {}
        
        date = obj["created"].split(" ")[0]
        if "0" not in date or datetime.datetime.strptime(date,"%m-%d-%Y") < clips[sub]:
            counter +=1 
            continue

        if date not in sent_all[sub]:
            sent_all[sub][date] = []
        try:        
            sent_all[sub][date].append(float(obj["sentiment"]))
        except ValueError as err:
           pass 
        
        counter += 1



for sub in sent_all:
    reduced = {}
    info = sent_all[sub]
    if not info:
        continue
    for date, arr in info.items():
        if date not in reduced:
            reduced[date] = None
        sum_arg = 0
        for sent in arr:
            sum_arg += sent
        sum_arg /= len(arr)
        reduced[date] = sum_arg
    dates = [datetime.datetime.strptime(ts, "%m-%d-%Y") for ts in list(info.keys())] 
    dates.sort()
    sorted_dates = [datetime.datetime.strftime(ts, "%m-%d-%Y") for ts in dates]
    x = []
    y = []
    for date in sorted_dates:
        x.append(date)
        y.append(reduced[date])

    assert(len(x) == len(y))
    stuff = {"x": x, "y": y}
    with open("sentiment-%s.json" % sub, "w") as fout:
        print(json.dumps(stuff), file=fout)


 
