"""
Tools for structured data collection and automated dataset creation:
Advanced practical by Erik Koynov, University of Heidelberg
Definitions of functions used in the scripts provided
"""

import requests
import json
import bs4
import argparse
from datetime import datetime
from datetime import date
import os
from more_itertools import locate
import matplotlib.pyplot as plt
"""
USED IN: QandAcrawler.py
FUNCTION: find_useful_links_and_update() -> parse the given webpage search for links to new questions, until
the old_date has been reach (no more new questions are available) write the links to the found_links dictionary
in order to evade repetitions of links
INPUT:
	soup -> the parsed current page in the frag-einen-anwalt website
	file -> the file to be written to (currently obsolete)
	stop_appending -> boolean variable indicating the newest link in the last update has been reached
	old_date -> the date of the newest link in the last update
	found_lnks -> dictionary passed by reference
OUTPUT:
	stop_appending -> because the function is called in a loop and the boolean variable is constantly checked
	n -> the number of links found on the current page
"""
def find_useful_links_and_update(soup, file, stop_appending, old_date, found_links):
    important_divs = soup.find_all('div',class_="fTopic taxonomy2 cleared")
    
    n=0
    for div in important_divs:
        date_str = div.find('span',class_='tDate').text.split('.')
        date = datetime(int(date_str[2]),int(date_str[1]),int(date_str[0]))
        try:
            link_ = div.find('div',class_='bold').a['href']
            if old_date!=None:
                if date > old_date:
                    print(date)
                    print(old_date)
                    #file.write(str(link_)+'\n')
                    found_links[str(link_)+'\n']=None
                else:
                    stop_appending = True
                    return True, n
            else:
                found_links[str(link_)+'\n']=None
        except TypeError as e:
            print(e)
            continue
        print(date, link_)
        n+=1
    return stop_appending, n
"""
USED IN: QandAcrawler.py
FUNCTION: get_last_datetime -> having received the link to the last "newest" question on frag-einen-anwalt, parse the page
and find the place where the date and time of the publication was printed and return it in the format of python datetime
INPUT: link -> str holding the link to the last question to be stored on the links file
       session -> python requests Session object
       headers -> dictionary holding the headers of the request to be sent to the server of frag-einen-anwalt
OUTPUT: last_datetime -> the date of the last question in the python datetime format
"""

def get_last_datetime(link, session, headers):
    a = session.get(link, headers=headers).text
    soup = bs4.BeautifulSoup(a, "html5lib")
    last_question_info = soup.find('div',class_='fea-question-head-info')
    last_question_datetime = last_question_info.text.strip()

    if last_question_datetime[0] == '|':
        last_question_datetime = last_question_datetime[1:].strip().split('|')[0].split(' ')
    else:
        last_question_datetime = last_question_datetime.split('|')[0].split(' ')
    print(last_question_datetime)

    #print(last_question_datetime)
    last_question_date = last_question_datetime[0].split('.')
    last_question_time = last_question_datetime[1].split(':')
    #print(last_question_date)
    #print(last_question_time)

    last_question_datetime = datetime(int(last_question_date[2]),
                                    int(last_question_date[1]),
                                    int(last_question_date[0]),
                                    int(last_question_time[0]),
                                    int(last_question_time[1]))
    return last_question_datetime

'''
USED IN: QandA_crawler in get_links_update_final()
FUNCTION: merge_files -> write onto the new_file first the newest links from the temp_file and then the old
links from the old_file. Thus a more secure way of substituting the old file with the new one is guaranteed.
INPUT: old_file -> open file which hold the old links
       new_file -> open file which will act as a buffer
       temp_file -> the temporary file holding only the new links
OUTPUT: none
NOTE: keeping the temp_file is done because I wanted to ensure that one could recheck the last updates and now
exactly what has been downloaded and when
'''
def merge_files(old_file, new_file, temp_file):
    print('\n\n\n\nMERGING FILES\n\n\n\n')
    try:
        for line in temp_file:
            new_file.write(line)
    except Exception as e:
        print(e)
        
    try:
        for line in old_file:
            new_file.write(line)
    except Exception as e:
        print(e)
        
    return 0

"""
USED IN: QandAcrawler in download_everything_update_final
FUNCTION: update_json_files -> merge the old data and the new data and write both to a temporary file (_updated)
then move the old file to the thrashbin folder of the project (in order to keep a backup) and rename the _updated
file to have the name of the old file
INPUT: append -> boolean variable holding the flag to permit the execution of the operations
       area -> str holding the area of law
       data -> the collected data
OUTPUT: none
"""
def update_json_files(append, area, data):
    if not os.path.isdir('Q&Adata'):
        os.mkdir('Q&Adata')
    if append:
        try:
            json_file = open('Q&Adata/' + area + '.json', 'r')
            data_ = json.load(json_file)
            json_file.close()
            json_file = open('Q&Adata/' + area +'_updated' +'.json', 'w')
            # delete the old file and replace it with the updated version
            try:
                json.dump(data + data_, json_file, ensure_ascii=False)
            except Exception as e:
                print(e)
                print('UPDATE FAILED ON: ', area)
            else:
                os.rename('Q&Adata/' + area + '.json','thrashbin/' + area + '.json' )
                os.rename('Q&Adata/' + area +'_updated' +'.json','Q&Adata/' + area  +'.json')
        except FileNotFoundError:
            print('writing on a new file')
            json_file = open('Q&Adata/' + area + '.json', 'w')
            json.dump(data, json_file, ensure_ascii=False)

"""
USED IN: build_data_set.py
FUNCTION: create_folders_for_dataset -> create a folder with the naming convention -> the current date + an index
INPUT: none
OUTPUT: the name of the newly created folder
"""
def create_folders_for_dataset():
    date_ = date.today()
    DIR_NAME = 'Dataset'+'_'+str(date_.year)+'_'+str(date_.month)+'_'+str(date_.day)+'_1'
    while os.path.exists(DIR_NAME):
            print('_'.join(DIR_NAME.split('_')[:-1]))
            counter = int(DIR_NAME.split('_')[-1])+1
            DIR_NAME = '_'.join(DIR_NAME.split('_')[:-1]) + '_' +str(counter)
    print(DIR_NAME)
    print('Creating folder: {}'.format(DIR_NAME))
    os.mkdir(DIR_NAME)
    return DIR_NAME

"""
USED IN: build_data_set.py
FUNCTION: parse_preferences -> parse the command line arguments passed to build_data_set.py into a datastructure that can
be later used in build_data_set
INPUT: preferences -> str the command line arguments
OUTPUT: preferences -> the parces preferences as a dict with key the class and value - a list of tuples of paths to the files
that should be used to collect the data for the class and the weights that the data of those files should have in the class
        n_points -> the specified overall number of datapoints (for now all classes have an equal number of datapoints)
"""
# input data should be in the format -c Class -f <PATHs/to/file.json> .... -c Class <PATHs...>
def parse_preferences(preferences):
    preferences = preferences.split(' ')
    if len(list(locate(preferences,lambda x: x=='-n')))>1: # check if -n is specified more than once
        print('You have specified -n more than once. It must be specified once globally')
        exit()
    try:
        idx_of_n = preferences.index('-n')
        n_points = int(preferences[idx_of_n+1])
        string_ = preferences[:idx_of_n] + preferences[idx_of_n+2:]
    except ValueError:
        print('You have not specified an integer number of datapoints per class by -n')
        exit()
    #print(string_)
    string_ = ' '.join(string_)
    class_preferences = string_.strip().split('-c')
    preferences = {}
    class_ = 0 # consecutive class
    for class_p in class_preferences[1:]:

        class_name = class_p.strip().split('-f')[0].strip()
        if class_name == '':
            print('you have chosen -c but have not specified class name')
            exit()
        class_p = class_p.strip().split(' ')
        #class_name = class_p[0]
		#
        class_data = list(map(lambda x: list(map(lambda x: x.strip(), x.strip().split('-p'))),
		' '.join(class_p[1:]).strip().split('-f')))[1:]
        print(class_data)
        # calculate total percentage given
        #print(class_data)
        total_percentage = 0
        not_specified_idx = [] # idx of files for which a percentage was not specified
        if len(class_data)== 0:
            print('please specify files for class "{}" by -f <path to file>'.format(class_name))
            return
		# loop through the classes and fill the tuples
        for i in range(len(class_data)):
            if class_data[i][0]=='':
                print('you have chosen -f but have not specified a file path after it')
                exit()
            if len(class_data[i])>1:
                if class_data[i][1]=='': # check the case there a -p was written but no Number
                    class_data[i][1]=0
                class_data[i][1] = float(class_data[i][1])
                # ensure percentages will sum up to 100
                if (class_data[i][1] + total_percentage)>100:
                    class_data[i][1]=100-total_percentage
                total_percentage+=class_data[i][1]
            else:
                not_specified_idx.append(i)
        for i in not_specified_idx:
            if (len(not_specified_idx) == len(class_data)) or (total_percentage==0): # if inside the class nothing was specified
                class_data[i].append(100/len(not_specified_idx))
            else:
                percentage  = (100-total_percentage)
                if percentage>=0:
                    class_data[i].append(percentage/len(not_specified_idx))
                else:
                    class_data[i].append(0)

        #print(class_name, class_data )
        print(preferences)
        preferences[class_name]=class_data
        class_ +=1
    print('The class arrangements you have chosen: \n',preferences)
    print('Number of data points per class you specified:\n', n_points)
    return preferences, n_points

"""
USED IN: build_data_set
FUNCTION: initial_fill -> since the introduction of percentages for the quantity of
datapoints from a file to be included in a class the need of different stages
in filling the classes became obvious. The first stage -> the initial_fill checks
the percentages specified for each file, check if enough data if available in that
file to fulfill the percentage requirement if not -> put the whole data of that file
into the class, set n_to_be_extracted[1] to False -> no more data to be extracted. The
output of this step will later be used in the other stages of the filling of the classes
INPUT: preferences -> dictionary with key str name of the class and values -> a list of lists
where each of the elements holds the file name and the specified percentage
       name_of_class -> the class name since this function is called in a Loop
	   class_data -> a list, passed by reference, to be filled in place with data
	   n_points -> the number of points for the class
OUTPUT: n_to_be_extracted -> dict with file name as key and values the last index
of the file that was input into the class_data and a boolean telling whether more
data can be extracted. Used as optimization -> first read the boolean and then open
the file if any more data could be loaded
"""

def initial_fill(preferences, name_of_class, class_data, n_points):
    print('Starting collecting the data for {}',name_of_class)
    n_to_be_extracted = {} #hold data that would let us fill up the dataset
    for class_specifications in sorted(preferences[name_of_class]):
        try:
            current_file = open(class_specifications[0],'r')
        except Exception as e:
            print(e)
            print('{} is not a valid file'.format(class_specifications[0]))
            return None, None
        # a [] in which the first element says how much of the data has been used
        # already and the second element if a boolean meaning if there is more
		# data to be loaded in that file.
        n_to_be_extracted[class_specifications[0]]=[]
        print('Loading file ', class_specifications[0])
        data_ = json.load(current_file)
        # keep adding util it suffices

        if class_specifications[1]==0.0:
            n_to_be_extracted[class_specifications[0]].append(0)
            n_to_be_extracted[class_specifications[0]].append(True)
            '''num_points = n_points - len(class_data)
            if num_points<len(data_):
                class_data += data_[:num_points]
                n_to_be_extracted[class_specifications[0]].append(n_points - len(class_data))
                n_to_be_extracted[class_specifications[0]].append(True) # can be used further
            else: # if there are less datapoints than what we want to put in the dataset
                class_data += data_
                n_to_be_extracted[class_specifications[0]].append(len(data_))
                n_to_be_extracted[class_specifications[0]].append(False) '''# cannot be used further
        # if percentages have been specified
        else:
            """
            TODO: if percentages have been specified/ if len class_data is not n_points -> fill up -> if not specify more data
            """
            num_points = int(n_points*(class_specifications[1]/100.0))
            if num_points<len(data_):
                class_data += data_[:num_points]
                n_to_be_extracted[class_specifications[0]].append(num_points)
                n_to_be_extracted[class_specifications[0]].append(True)
            else:
                class_data += data_
                n_to_be_extracted[class_specifications[0]].append(len(data_))
                n_to_be_extracted[class_specifications[0]].append(False)

    return n_to_be_extracted
"""
USED IN: build_data_set
FUNCTION: refill -> Second stage of the filling process. Check if there if anything to be
added in the files, if yes add everything up to the n_points boundary - i.e. disregard
the percentages and give preference to the QandA questions -> because of the sorting of the
file names
INPUT: preferences -> dictionary with key str name of the class and values -> a list of lists
where each of the elements holds the file name and the specified percentage
       name_of_class -> the class name since this function is called in a Loop
	   n_to_be_extracted -> dictionary with name of file as key and values -> last index
that was extracted from that file and boolean variable that tells whether more data could be
extracted
       class_data -> list passed by reference to be filled with data
	   n_points -> total number of datapoints pred class
OUTPUT: boolean -> whether more data needs to be added or not i.e. flag for going to the third
stage of the filling process
"""
def refill(preferences, name_of_class, n_to_be_extracted, class_data, n_points):
    for class_specifications in sorted(preferences[name_of_class]):
        print(n_to_be_extracted)
        if  n_to_be_extracted[class_specifications[0]][1]:
            current_file = open(class_specifications[0],'r')
            print('Loading file ', class_specifications[0])
            data_ = json.load(current_file)
            new_start_point = n_to_be_extracted[class_specifications[0]][0]
            if len(data_[new_start_point:])<n_points - len(class_data):
                class_data+=data_[new_start_point:]
            else:
                class_data+=data_[new_start_point:new_start_point+(n_points - len(class_data))]
                return False # should not be refilled with new FILES
    return True
"""
USED IN: build_data_set
FUNCTION: test_if_file_was_used -> given a new file name check if it is inside the preferences
for the class. Here one could input files that were already used in other classes but since
this is highly unlikely and this app is created for specialists we do not cover this case. However
in the user friendly GUI version this will be removed
INPUT: file_name -> the name of the new file
       preferences -> dictionary with key str name of the class and values -> a list of lists
where each of the elements holds the file name and the specified percentage
       name_of_class -> current class since the funciton is used in a Loop
OUTPUT: boolean -> if file was used -> True else : false
"""
def test_if_file_was_used(file_name, preferences, name_of_class):
    for i in preferences[name_of_class]:
        if file_name==i[0]: # if file was in the files chosen for the class
            return True
    else:
        return False

"""
USED IN: build_data_set
FUNCTION: fill_with_new_file -> Third stage of the filling process-> fill all available data
into the class data until its length has reached n_points
INPUT: file_name -> the new file to be read and filled into the class
	   class_data -> list passed by reference to be filled with data
	   n_points -> number of points per class
OUTPUT: boolean -> whether more data is needed
"""
def fill_with_new_file(file_name, class_data, n_points):
    file_name = open(file_name,'r')
    data_ = json.load(file_name)
    if len(data_)<n_points-len(class_data):
        class_data+=data_
        return True
    else:
        class_data+=data_[:n_points-len(class_data)]
        return False

"""
USED IN: build_data_set
FUNCTION: dataset_statistics_ -> return the statistics in such a format that can be
easily used to plot
INPUT: path to the dataset
OUTPUT: statistics
"""
# example output
#[{'area': 'labor', 'separate_areas': ['Arbeitsrecht', 'Arbeitsrecht Q only'], 'areas_count': [82, 20], 'with_answers_count': [82, 20], 'explode': [0, 0.15]},
# {'area': 'patent', 'separate_areas': ['', 'Patentrecht Q only', '', 'Auto - Kauf und Verkauf Q only'], 'areas_count': [15, 87], 'with_answers_count': [0, 15, 0, 87], 'explode': [0, 0.15, 0, 0.15]}]
def dataset_statistics_(path):
    dataset_statistics=[]
    i = 0
    for file in os.listdir(path):
        print(file)
        file_ = open(os.path.join(path,file),'r')
        file_ = json.load(file_)
        dataset_statistics.append({})
        separate_areas = []
        separate_areas_count = []
        with_answers = []
        explode = []
        old_area = None
        j=-1
        k=-1
        q_only = None # a boolean to hold whether the current area is q_only or qanda
        for entry in file_:
            if entry['area']!= old_area and entry['area'] not in separate_areas and (entry['area']+' Q only') not in separate_areas:
                separate_areas.append('')
                separate_areas.append('')
                j+=2
                k+=1
                #separate_areas_count.append(0)
                with_answers.append(0)
                with_answers.append(0)
                explode.append(0)
                explode.append(0)

            try:
                # record the number of questions with answers for each of the separate areas in a dataset file
                _=entry['answer']
                q_only = False
                if entry['area'] not in separate_areas:
                    separate_areas[-2] = entry['area']


            # if there is no 'answer' then the data is part of the Q only collection
            except KeyError:
                q_only = True
                if (entry['area']+' Q only') not in separate_areas:
                    separate_areas[-1] = entry['area']+' Q only'
                    explode[-1] = 0.15
                #with_answers[j]+=1
                pass
			# find the correct index to append
            if q_only:
                current_area = separate_areas.index(entry['area']+' Q only')
                idx = current_area
            else:
                current_area = separate_areas.index(entry['area'])
                idx = current_area
            with_answers[idx]+=1
            #separate_areas_count[idx]+=1
        separate_areas_idx = 0
        for c_ in range(len(with_answers)):
            if with_answers[c_]!=0:
                separate_areas_count.append(with_answers[c_])
                separate_areas_idx+=1
        dataset_statistics[i]['area']=file[:-5]
        dataset_statistics[i]['separate_areas']=separate_areas
        dataset_statistics[i]['areas_count']=separate_areas_count
        dataset_statistics[i]['with_answers_count']=with_answers
        dataset_statistics[i]['explode']=explode
        i+=1
    print(dataset_statistics)
    return dataset_statistics
"""
USED IN: build_data_set
FUNTION: plot_dataset_statistics -> generate a pie chart with the dataset statistics
INPUT: path -> to the dataset where to store the plot
       dataset_statistics -> statistics
OUTPUT: none
"""
def plot_dataset_statistics(path, dataset_statistics):
    fig = plt.figure(figsize=(23,23))
    cmap = plt.get_cmap("tab20c")

    fig.suptitle('Quantitative analysis:\nContent of dataset regarding the presence of Q only samples', fontsize = 26, weight = 'bold')
    j = 0
    if int(len(dataset_statistics)%2)==1:
        ax = fig.subplots(len(dataset_statistics),1)
        if len(dataset_statistics)>1:
            for i in dataset_statistics:
                patches, texts, autotexts=ax[j].pie(i['with_answers_count'],labels=i['separate_areas'],explode = i['explode'],shadow=True, autopct = lambda p: '{:,.0f}'.format(p * sum(i['areas_count'])/100) if p>0 else '')
                ax[j].set_title(i['area'],fontsize= 20,weight='bold')
                [_.set_fontsize(17) for _ in texts]
                [_.set_fontsize(15) for _ in autotexts]
                j+=1
		# sadly matplotlib is not foolproof and a specific case should be checked where
		# there is only one element because that element cannot be indexed with 0
        else:
            for i in dataset_statistics:
                patches, texts, autotexts=ax.pie(i['with_answers_count'],labels=i['separate_areas'],explode = i['explode'],shadow=True, autopct = lambda p: '{:,.0f}'.format(p * sum(i['areas_count'])/100) if p>0 else '')
                ax.set_title(i['area'],fontsize= 20,weight='bold')
                [_.set_fontsize(17) for _ in texts]
                [_.set_fontsize(15) for _ in autotexts]
                j+=1
    else:
        ax = fig.subplots(int(len(dataset_statistics)/2),2)
        if len(dataset_statistics)!=2:
            for i in dataset_statistics:
                patches, texts, autotexts=ax[int(j/2),int(j%2)].pie(i['with_answers_count'],labels=i['separate_areas'],explode = i['explode'],shadow=True, autopct = lambda p: '{:,.0f}'.format(p * sum(i['areas_count'])/100) if p>0 else '')
                ax[int(j/2),int(j%2)].set_title(i['area'],fontsize= 20,weight='bold')
                [_.set_fontsize(17) for _ in texts]
                [_.set_fontsize(15) for _ in autotexts]
                j+=1
        else:
            for i in dataset_statistics:
                patches, texts, autotexts=ax[int(j%2)].pie(i['with_answers_count'],labels=i['separate_areas'],explode = i['explode'],shadow=True, autopct = lambda p: '{:,.0f}'.format(p * sum(i['areas_count'])/100) if p>0 else '')
                ax[int(j%2)].set_title(i['area'],fontsize= 20,weight='bold')
                [_.set_fontsize(17) for _ in texts]
                [_.set_fontsize(15) for _ in autotexts]
                j+=1
    plt.savefig(os.path.join(path,'fig_.png'))
