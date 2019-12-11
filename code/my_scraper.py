#!/usr/local/bin/python3

import sys
import praw
from prawcore import NotFound, PrawcoreException
import json
import datetime as dt


import multiprocessing as mp
import os
import queue



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# worker function to process the posts collected
def process_post(collected, comments, sub, search):
    # set up directory structure for files
    path = "./%s/%s" % (sub, search)

    while True:
        try:
            post = collected.get_nowait()

        except queue.Empty:
            break
        else:
            #do the thing
            # create JSON object with fields from the post
            overview = {}
            overview["Title-text"] = post.title
            overview["Score"] = post.score
            overview["ID"] = post.id
            overview["URL"] = post.url
            overview["Comment Count"] = post.num_comments
            overview["Created"] = dt.datetime.fromtimestamp(post.created).strftime("%m-%d-%Y %H:%M:%S")    # Convert UNIX time to readable format
            
            filename = "%s-post.json" % overview["ID"]

            full_path = "%s/%s/%s" % (path, overview["ID"], filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # print obj to file 
            with open(full_path, "w") as fout:
                print("%s\n" % json.dumps(overview), file=fout) 

            # add the post ID to the comment queue for comment threads to work
            # on
            comments.put((overview["ID"], "%s/%s" % (path, overview["ID"])))
            

# worker function to process comments on a given post

def main():
    # setting up queues for workers and process list to join on
    processing_collected = mp.Queue()
    processes = []
   
    processing_comments = mp.Queue()
    
    # subreddits to search [TODO: change to file input maybe]
    SUBS = ["ios", "android", "windows", "macos", "ubuntu", "osx",
            "playstation", "xbox", "Gear360", "NintendoSwitch"]
    # search terms to use on each subreddit [TODO: change to file input maybe]
    SEARCH_TERMS = ["update version", "upgrade", "security patch",
                "security update", "should I update", "should I upgrade"]
    NEW_S_TERMS = []
    for sub in SUBS:
        for sterm in SEARCH_TERMS:
            NEW_S_TERMS.append("%s %s" % (sub, sterm))
    
    SUBS = ["news"] 
    # use 2x the number of cpus for threads - should be tweaked since the
    # bottleneck here is I/O not CPU [TODO: figure out a better #]
    NUM_PROCESSES = mp.cpu_count() ** 2


    ### Get current date
    date = dt.datetime.now().strftime("%m-%d-%Y")
      
    api_creds =  {"c_id": "", 
                "c_secret": "", 
                "u_a": "", 
                "usrnm": "",
                "passwd": ""}


    ### Reddit Login
    reddit = praw.Reddit(client_id = api_creds["c_id"],  
                         client_secret = api_creds["c_secret"], 
                         user_agent = api_creds["u_a"], 
                         username = api_creds["usrnm"], 
                         password = api_creds["passwd"])
    
    for sub in SUBS:
        subreddit = reddit.subreddit(sub)
        eprint("Working on subreddit: %s" % sub)
        
        for s_term in NEW_S_TERMS:
            eprint("\tWorking on search term: %s" % s_term)
            # Get all responses from the search
            collected = subreddit.search(s_term, limit=None)
            count_coll = 0
            for item in collected:
               processing_collected.put(item)
               count_coll += 1
            
            eprint("\t\tCollected %d posts" % count_coll)

       
            # Process posts
            eprint("\t\t\tStarting post workers")
            for w in range(NUM_PROCESSES):
                p = mp.Process(target=process_post,
                    args=(processing_collected,processing_comments, sub, s_term))
                processes.append(p)
                p.start()
                
            eprint("\t\t\t\tBlocking on post workers")
            for p in processes:
                p.join()

            eprint("\t\t\t\tPost workers finished")
            
if __name__ == "__main__":
    main()
    
