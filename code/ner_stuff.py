from pathlib import Path
import spacy
from nltk.tokenize import TweetTokenizer
import sys
import csv
import json
import re
from pandas.io.json import json_normalize

tknzr = TweetTokenizer()
tknzr = TweetTokenizer(reduce_len=True)

nlp2 = spacy.load(Path('ner_model_50'))


full_data = []
counter = 0
with open(sys.argv[1], "r") as json_in:
    line = json_in.readline()
    while line:
        try:
            if counter % 1000 == 0:
                sys.stderr.write("\t\tcounter --- %d\n" % counter)
            stuff = line.strip()
            
            obj = json.loads(stuff)
            text = obj['text']

            crap = " ".join([w for w in tknzr.tokenize(text)])
            doc = nlp2(crap)


            tech_words = set()
            react_words = set()


            tech_working = ""
            react_working = ""
            for x in doc.ents:
                if x.label_ == "B-TECH":
                    if tech_working:
                        if tech_working in crap:
                            tech_words.add(tech_working)
                    tech_working = x.text

                elif x.label_ == "B-REACT":
                    if react_working:
                        if react_working in crap:
                            react_words.add(react_words)
                    react_working = x.text

                elif x.label_ == "I-REACT":
                    tmp = react_working
                    tmp += " " + x.text
                    if tmp not in crap:
                        if react_working in crap:
                            react_words.add(react_working)
                        react_working = x.text
                    else:
                        react_working = tmp
                
                elif x.label_ == "I-TECH":
                    tmp = tech_working
                    tmp += " " + x.text
                    if tmp not in crap:
                        if tech_working in crap:
                            tech_words.add(tech_working)
                        tech_working = x.text
                    else:
                        tech_working = tmp

            if tech_working:
                if tech_working in crap:
                    tech_words.add(tech_working)
            if react_working:
                if react_working in crap:
                    react_words.add(react_working)

           
            #print("Sentence: ")
            #print(crap)

            #for ent in doc.ents:
            #    print(ent.label_, ent.text)
            #
            #print("tech")
            #print(tech_words)
            #print()
            #print("react")
            #print(react_words)
            #print("\n\n")
            reported_set_tech = set()
            reported_set_react = set()
            

            for element in tech_words:
                stuff = re.split(" \. | \.|\. ", element)
                for shiz in stuff:
                    if shiz and shiz != ".":
                        reported_set_tech.add(shiz)
            for element in react_words:
                stuff = re.split(" \. | \.|\. ", element)
                for shiz in stuff:
                    if shiz and shiz != ".":
                        reported_set_react.add(shiz)


            obj["tech"] = reported_set_tech
            obj["react"] = reported_set_react

            
            full_data.append(obj)
            


            counter += 1
            
            line = json_in.readline()
        except TypeError as err:
            line = json_in.readline()
            counter += 1
            continue
df = json_normalize(full_data)
df.to_csv("csv_with_labels.csv")
