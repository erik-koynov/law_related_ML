"""
Tools for structured data collection and automated dataset creation:
Advanced practical by Erik Koynov, University of Heidelberg
Convert all json files in the chosen directory to csv files
"""
import os
import pandas
import json
import sys
FOLDER = '/home/ek/disk/ERIK_ADVANCED_PRACTICAL/'+sys.argv[1]
DESTINATION = FOLDER + '_csv'
for file in os.listdir(FOLDER):
    if os.path.isdir(os.path.join(FOLDER,file)):
        print(file + "is dir")
        continue
    else:
        print(file)
        f = open(os.path.join(FOLDER,file),'r')
        data = json.load(f)
        df = pandas.DataFrame(data)
        df.to_csv(os.path.join(DESTINATION,file[:-5]+'.csv'),index=False)
