#!/Users/swsprec/opt/anaconda3/bin/python3

import json 
import sys
import datetime


full_data = {}

clips = {}
with open("../clipping_dates.json", "r") as clip_in:
    for line in clip_in.readlines():
        clips = json.loads(line)

for sub, date in clips.items():
    clips[sub] = datetime.datetime.strptime(date, "%m-%d-%Y")


with open(sys.argv[1], 'r') as fin:
    for line in fin.readlines():
        line = line.strip()
        obj = json.loads(line)
        if obj["topic"] not in full_data:
            full_data[obj["topic"]] = {}
        
        date = obj["date"].split(" ")[0]
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        if date < clips[obj["topic"]]:
            continue


        date = datetime.datetime.strftime(date, "%m-%d-%Y")
        if date not in full_data[obj["topic"]]:
            full_data[obj["topic"]][date] = []

        full_data[obj["topic"]][date].append(obj["title"])

for sub in full_data:
    info = full_data[sub]
    
    dates = [datetime.datetime.strptime(ts, "%m-%d-%Y") for ts in list(info.keys())]
    dates.sort()
    sorted_dates = [datetime.datetime.strftime(ts, "%m-%d-%Y") for ts in dates]

    x = []
    y = []
    hovertext = []
    for date in sorted_dates:
        x.append(date)
        y.append(-2)
        hovertext.append(info[date])
        assert(len(x) == len(hovertext))
    hovertext = ["\n".join(x) for x in hovertext]

    stuff = {"x": x, "y": y, "hovertext": hovertext}
    with open("articles-%s.json" % sub, "w") as fout:
        print(json.dumps(stuff), file=fout)
