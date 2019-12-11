import sys


AVG_WINDOW = 50
TIMES_LARGER = 4 
interesting_dates = []
first_bit = []

moving_avg = 0
counter = 0
with open(sys.argv[1], "r") as dates_in:
    dates = dates_in.readlines()
    for date in dates:
        counter +=1 
        stuff = date.lstrip().split(" ")
        count = int(stuff[0])
        date = stuff[1].strip()
        
        if counter < AVG_WINDOW:
            first_bit.append((count,date))
        elif counter == AVG_WINDOW:
            start_avg = 0
            for count,date in first_bit:
               start_avg += int(count) 
            moving_avg = start_avg
            start_avg /= AVG_WINDOW     
            for count,date in first_bit:
                if int(count) > start_avg*TIMES_LARGER:
                    interesting_dates.append((count, start_avg, date))
        else:
            shiz = first_bit.pop(0)
            moving_avg -= shiz[0]
            first_bit.append((count,date))
            moving_avg += count
            test = moving_avg/AVG_WINDOW
            if count > (test)*TIMES_LARGER:
                interesting_dates.append((count,test,date))

for count, avg, date in interesting_dates:
    print(date)
#print(interesting_dates)
