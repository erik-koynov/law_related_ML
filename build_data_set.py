"""
Tools for structured data collection and automated dataset creation:
Advanced practical by Erik Koynov, University of Heidelberg
Build a balanced dataset from the available data files using user preferences
"""
import os
import json
from datetime import date
from helper_functions import (create_folders_for_dataset, parse_preferences,fill_with_new_file,
                             test_if_file_was_used,refill, initial_fill, dataset_statistics_,
                             plot_dataset_statistics)
import sys
import argparse
import matplotlib.pyplot as plt 
FOLDER='Q&Adata/'
QFOLDER='Q_only_data/'
"""
FUNCTION: statistics : calculate the number of datapoints per file and print it to the console
INPUT: FOLDER : path to the folder to be analyzed
OUTPUT: none
"""
def statistics(FOLDER):

    lenght_of_data={}
    total=0
    for file in os.listdir(FOLDER):

        if not os.path.isdir(os.path.join(FOLDER,file)):

            field=file.split('.')[0]
            file_=open(os.path.join(FOLDER,file),'r')
            data=json.load(file_)
            lenght_of_data[field]=len(data)
            total+=len(data)
            print(os.path.join(FOLDER,file),lenght_of_data[field])
    output=open('Qonly_statistics.json','w')
    json.dump(lenght_of_data,output,ensure_ascii=False)
    print(len(lenght_of_data.keys()))
    print(total)
"""
FUNCTION: build_datasets : build custom balanced datasets form preferences provided by the user
INPUT: preferences : 
	The preferences should be a dictionary with the following datafields:
	{'name_of_Class' : [<path_to_files>]}, n_datapoints_in_class
	Name the new dataset Dataset_<year>_<month>_<day> if such exists : add _counter
       n_points : the number of datapoints per class
OUTPUT: None (a new folder is created holding the new dataset as .json files)
"""
def build_datasets(preferences, n_points):
    DIR_NAME = create_folders_for_dataset()
    # create the datasets
    for name_of_class in preferences.keys():
        final_file = os.path.join(DIR_NAME,name_of_class+'.json')
        class_data = []
        # fill up dataset
        n_to_be_extracted = initial_fill(preferences, name_of_class, class_data, n_points)
        print('Initial fill is over. Current amount of datapoints for {} is {}'.format(name_of_class,len(class_data)))
        if (n_to_be_extracted==None) or (class_data==None):
            print('Deleting folder. Start anew!')
            os.rmdir(DIR_NAME)
            exit()
        # check if class data is enough : if not -> refill
        if len(class_data)<n_points:
            print('Could not collect the specified number of datapoints. Starting refilling')
            to_add = refill(preferences, name_of_class, n_to_be_extracted, class_data, n_points)
            # add new files to fill
            message = 'the data you have initially specified for {} does not seem to have as many datapoints as you have chosen-only {}.\
please add additional paths to files: '
            while (to_add):
                file_name = input(message.format(name_of_class,len(class_data)))

                while(test_if_file_was_used(file_name, preferences, name_of_class)):
                    message = 'The file you have chosen has already been used by you for the same class, Please choose another one: '
                    file_name = input(message)
                try:
                    current_file = open(file_name,'r')
                except FileNotFoundError:
                    print(file_name+'was not found')
                    message = 'Please enter a new path'
                    continue
                to_add = fill_with_new_file(file_name, class_data, n_points)

        final_file = open(final_file,'w')
        json.dump(class_data,final_file,ensure_ascii=False)
    return DIR_NAME
if __name__=='__main__':
    statistics(FOLDER)
    statistics(QFOLDER)
    try:
        preferences, n_points = parse_preferences(input('please choose from the above\
classes and specify the datapath in the following format\
\n-n points per class (only once for all classes)\
\n-c <name of class> \
\n-f <path to file>\
\n-p <percentage of all> (optional) \
\nin that STRICT ORDER for each class: \n '))
    except Exception:
        exit()

    DIR_NAME = build_datasets(preferences, n_points)
    dataset_statistics = dataset_statistics_(DIR_NAME)
    plot_dataset_statistics(DIR_NAME, dataset_statistics)
