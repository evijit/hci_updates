#!/usr/bin/python

import json
import sys
import csv
import datetime

tech_words = {}
react_words = {}

NUM_TECH_REPORTED = 10 - 1
NUM_REACT_REPORTED = 10 - 1


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

        created = obj["created"].split(" ")[0]
        if created != "created":
            date_time = datetime.datetime.strptime(created, "%m-%d-%Y")
            if date_time < clips[sub]:
                counter += 1
                continue            

        if obj["tech"][0] == "{":
            r = csv.reader([obj["tech"][1:-1]])
            if sub not in tech_words:
                tech_words[sub] = {}
            for term in list(r)[0]:
                term = term.strip().lower()
                if term in tech_words[sub]:
                    tech_words[sub][term].append(obj["created"]) 
                else:
                    tech_words[sub][term] = [obj["created"] ]
        


        if obj["react"][0] == "{":
            r = csv.reader([obj["react"][1:-1]])
            if sub not in react_words:
                react_words[sub] = {}
            for term in list(r)[0]:
                term = term.strip().lower()
                if term in react_words[sub]:
                    react_words[sub][term].append(obj["created"])
                else:
                    react_words[sub][term] = [obj["created"]]

        
        counter += 1



for sub in tech_words:
    info = tech_words[sub]
    sorted_sub = [(k, info[k]) for k in sorted(info, key=lambda k: len(info[k]), reverse=True)]
    counter = 0
    reported_obj = {}
    for term, dates in sorted_sub:
        num = len(dates)
        dates = [ts.split(" ")[0] for ts in dates]
        dates = [datetime.datetime.strptime(ts, "%m-%d-%Y") for ts in dates]
        dates.sort()
        sorted_dates = [datetime.datetime.strftime(ts, "%m-%d-%Y") for ts in dates]
        shit = {}
        for date in sorted_dates:
            if date not in shit:
                shit[date] = 1
            else:
                shit[date] += 1

        x = list(shit.keys())
        y = list(shit.values())
        assert(len(x) == len(y))

        reported_obj[term] = {"x": x, "y": y}


        if counter == NUM_TECH_REPORTED:
            with open("tech-words-%s.json" % sub, 'w') as fout:
                print(json.dumps(reported_obj), file=fout)
            break
        else:
            pass
        counter += 1
    

react_report = {}
for sub in react_words:
    info = react_words[sub]
    sorted_sub = [(k, info[k]) for k in sorted(info, key=lambda k: len(info[k]), reverse=True)]
    counter = 0
    reported_obj = {}
    for term, dates in sorted_sub:
        num = len(dates)
        dates = [ts.split(" ")[0] for ts in dates]
        dates = [datetime.datetime.strptime(ts, "%m-%d-%Y") for ts in dates]
        dates.sort()
        sorted_dates = [datetime.datetime.strftime(ts, "%m-%d-%Y") for ts in dates]
        shit = {}
        for date in sorted_dates:
            if date not in shit:
                shit[date] = 1
            else:
                shit[date] += 1

        x = list(shit.keys())
        y = list(shit.values())
        assert(len(x) == len(y))

        reported_obj[term] = {"x": x, "y": y}
        
        if counter == NUM_REACT_REPORTED:
            with open("react-words-%s.json" % sub, "w") as fout:
                print(json.dumps(reported_obj), file=fout)
            break
        else:
            pass
        counter += 1
 
