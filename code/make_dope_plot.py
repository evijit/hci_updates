#!/Users/swsprec/opt/anaconda3/bin/python3

import plotly.graph_objects as go
import sys
import json
from plotly.offline import plot
from datetime import date, timedelta, datetime

fig = go.Figure()

subreddit = sys.argv[1]
tech_or_no = sys.argv[2]
tech_or_no = int(tech_or_no)


events_file = "articles-%s.json" % subreddit
sentiments_file = "sentiment-%s.json" % subreddit
tech_ner_file = "tech-words-%s.json" % subreddit
react_ner_file = "react-words-%s.json" % subreddit
counts_file = "total_counts-%s.json" % subreddit

clips = {}
with open("clipping_dates.json", "r") as clip_in:
    for line in clip_in.readlines():
        clips = json.loads(line)

for sub, datez in clips.items():
    clips[sub] = datetime.strptime(datez, "%m-%d-%Y")



earliest_date = clips[subreddit]
end_date = datetime(2019, 12, 4)

fill_x = []

delta = end_date - earliest_date
for i in range(delta.days + 1):
    day = earliest_date + timedelta(days=i)
    fill_x.append(datetime.strftime(day, "%m-%d-%Y"))


fill_y = [0] * len(fill_x)

fig.add_trace(
    go.Scatter(
        x = fill_x,
        y = fill_y,
        name = "For Time Scale",
    )
)


## graphing total post/comments
totals = {}
with open(counts_file, "r") as count_in:
    for line in count_in.readlines():
        line = line.strip()
        obj = json.loads(line)
        totals = obj

    cumulative = 0
    new_y_vals = []
    for y_val in totals["y"]:
        new_y_vals.append((y_val + cumulative)/100.0)
        cumulative += y_val

fig.add_trace(
    go.Scatter(
       x = totals["x"],
       y = new_y_vals,
       name = "Total Post / Comments",
       mode="lines",
       line = {"shape": "spline", "smoothing": 0.3, "color": "black", "dash": "dash"},
        hovertemplate = 
        '<b>Date</b>: %{x}<br>' +
        '<b>Number</b>: %{text}',
        text = ["{}".format(int(x*100)) for x in new_y_vals]
    )
)


events = {}
with open(events_file, "r") as event_in:
    for line in event_in.readlines():
        line = line.strip()
        obj = json.loads(line)
        events = obj

# graph 
fig.add_trace(
    go.Scatter(
        x = events["x"],
        y = [-1] * len(events["x"]),
        hovertext = events["hovertext"],
        name = "Events",
        marker=dict(size=14, color="mediumvioletred"),
        mode="markers"
    )
)



sents = {}
with open(sentiments_file, "r") as sent_in:
    for line in sent_in.readlines():
        line = line.strip()
        obj = json.loads(line)
        sents = obj


# graph sentiments
fig.add_trace(
    go.Scatter(
        x = sents["x"],
        y = sents["y"],
        name = "Sentiment",
        fill="tozeroy",
        line = {"shape": "spline", "smoothing": 0.7, "color": "teal"}
    )
)



if tech_or_no:
    top_tech = {}
    with open(tech_ner_file, "r") as ner_in:
        for line in ner_in.readlines():
            line = line.strip()
            obj = json.loads(line)
            top_tech = obj
    
    for word, coords in top_tech.items():
        cumulative = 0
        new_y_vals = []
        for y_val in coords["y"]:
            new_y_vals.append((y_val + cumulative)/10.0)
            cumulative += y_val
        fig.add_trace(
            go.Scatter(
                x = coords["x"],
                y = new_y_vals,
                name = word,
                mode="lines",
                line = {"shape": "spline", "smoothing": 0.3},
                hovertemplate = 
                '<b>Date</b>: %{x}<br>' +
                '<b>Number</b>: %{text}',
                text = ["{}".format(int(x*10)) for x in new_y_vals]
            )
        )

else:
    top_react = {}
    with open(react_ner_file, "r") as ner_in:
        for line in ner_in.readlines():
            line = line.strip()
            obj = json.loads(line)
            top_react = obj
    
    
    for word, coords in top_react.items():
        cumulative = 0
        new_y_vals = []
        for y_val in coords["y"]:
            new_y_vals.append(y_val + cumulative)
            cumulative += y_val
        fig.add_trace(
            go.Scatter(
                x = coords["x"],
                y = new_y_vals,
                name = word,
                mode="lines",
                line = {"shape": "spline", "smoothing": 0.3},
                hovertemplate = 
                '<b>Date</b>: %{x}<br>' +
                '<b>Number</b>: %{text}',
                text = ["{}".format(int(x*10)) for x in new_y_vals]
            )
        )

if tech_or_no:
    t_or_r = "tech"
else:
    t_or_r = "react"


fig.update_layout(
    title="<b>Top %s words, sentiment and events for: %s</b><br>The frequencies of named"\
        " entities is /10 and the total number of posts /100" % (t_or_r, subreddit),
    xaxis_title = "Dates",
    yaxis_title = "-1<->1 for sentiment, # of occurances for NER words"
)


plot(fig, filename='plots/dope_graph-%s-%s.html' % (subreddit, t_or_r))
#fig.show()
