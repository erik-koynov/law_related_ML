"""
This script crawls the --------------.de website, extracts only the questions and the first
answer to them and writes this pair onto a json file named after the respective area of law.
The output files are stored in the folder Q&Adata. Q&Alinks is a folder of secondary importance
which contains text files holding all links to questions in a particular area of law.

FUNCTIONS: areas_list - downloads the list of all areas of law covered in the website's content
           last_forum_index - for each area of law (forum) get the number of pages
           get_links - downloads the all links to questions about the areas specified
           download_everything - downloads the questions and the answers to them
           download_everything_update_final - download and update
"""
import requests
import os
import json
import bs4
import argparse
from datetime import date as date_
from helper_functions import *
import sys
session=requests.Session()
with open('topics_qanda_new.json','r') as t:
    links=json.load(t)
print('topics_qanda_new.json is now open')
# define headers
headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"ccept-Encoding":"gzip, deflate, br",
"Accept-Language":"en-US,en;q=0.5",
"Connection"	:"keep-alive",
"Host":"www.--------------------.de",
"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"}


"""
FUNCTION: areas_list: Get the links to the different forums which differ from each other with respect to the area of law
which their contents concern - f.e. the forum Arbeitsrecht should be about labor law etc.
The function creates a json file holding the pairs of title and link to a Q&A forum
INPUT: None
OUTPUT: None (writes the areas into a .json file)
"""
def areas_list():
    a = session.get('https://--------------------/', headers=headers).text
    print(type(a))

    soup = bs4.BeautifulSoup(a, "html5lib")

    #print(soup.prettify())
    import re
    areas=soup.find('span',class_="linkList")
    print(areas)
    #print(areas.find_all('span'))
    k=0

    links={}
    for i in areas.find_all('a'):
        if i['href']=='javascript:void(0)':
            break
        print(i['href'])
        print(i.text)
        print('\n\n')
        links[i.text]=i['href']
        k+=1
    print(k)

    json_file=open('topics_qanda.json','w')
    json.dump(links,json_file)

"""
FUNCTION: last_forum_index: for each area get the last page's index so that this index can be
later used for crawling in a for loop
INPUT: links: the dict holding the topic:link pair 
OUTPUT: None (writes the data to a .json file)
"""
def last_forum_index(links):
    links_={}
    for topic,link in links.items():
        a = session.get(link, headers=headers).text


        soup = bs4.BeautifulSoup(a, "html5lib")
        print(topic)
        last_index=soup.find_all('a', class_='paging-item paging-link')[-1].text
        links_[topic]=(link,last_index)
    json_file=open('topics_qanda_new.json','w')
    json.dump(links_,json_file)
import time

# global variable links : a dict holding the link to the main page of a topic

#a = session.get(str(links['Arbeitsrecht'][0]), headers=headers).text
#soup = bs4.BeautifulSoup(a, "html5lib")
import os
# delete the "Beste Treffer" button which for some reason gets displayed in the for loop
#soup.find('div',id='fHead').decompose()

"""
FUNCTION: get_links_update_final: Download the links to each new question and write them to a file called <topic>_links.txt
INPUT: a list of strings (topics- f.e. Arbeitsrecht- the keys in the topics_qanda_new.json)
OUTPUT: None
"""

def get_links_update_final(topics):
    # allow for single strings as topics (not only lists of strings)

    if not isinstance(topics, list):
        topics = [topics]
    num_appends = []
    for topic in topics:
        print(topic)
        stop_appending = False
        if not os.path.exists('Q&Alinks/' + topic + '_links.txt'):
            a = input('\n\nNo file containing the needed links was found for {}. Do you want to continue [y/n]: '.format(topic))
            if a =='y':
                first_link = None
                last_question_datetime = None
                temp_file_name = date_.today()
            # for every
                temp_file_name = 'Q&Alinks_t/' + topic + '_' +str(temp_file_name.year)+'_'+str(temp_file_name.month)+'_'+str(temp_file_name.day)+'_links.txt'
                file = open(temp_file_name, 'w')
            else:
                print('You have chosen not to continue with the download of {}'.format(topic))
                continue
        else:
            temp_file_name = date_.today()
            # for every
            temp_file_name = 'Q&Alinks_t/' + topic + '_' +str(temp_file_name.year)+'_'+str(temp_file_name.month)+'_'+str(temp_file_name.day)+'_links.txt'
            file = open(temp_file_name, 'w') # temporary file which to write the new links to
            old_file = open('Q&Alinks/' + topic + '_links.txt', 'r') # do NOT change 'r' to 'w' !!!! (original file)
            first_link = old_file.readline()[:-1]
            old_file.close()
            print(first_link)
            last_question_datetime = get_last_datetime(first_link, session, headers)
            print('last datetime : ', last_question_datetime)
            print('file exists, appending')
            print('\n\n\n\nUpdating the dataset for {}'.format(topic))
            print('\n\n\n')
            # continue
        # file=open('Q&Alinks/'+topic+'_links.txt','a')
        # loop from 1 to the last possible page index of that topic
        l = 0 # number of links already downloaded
        # make sure there are NO REPETITIONS :
        found_links = {}
        for i in range(1, int(links[topic][1]) + 1):
            print(i)
            if i == 1:
                link = str(links[topic][0])
            else:
                # cut the .html part
                link = str(links[topic][0])[:-5] + '__p' + str(i) + '.html'
            a = session.get(link, headers=headers).text
            soup = bs4.BeautifulSoup(a, "html5lib")
            print(link)
            # delete the "Beste Treffer" button which for some reason gets displayed in the for loop
            try:
                soup.find('div', id='fHead').decompose()
            except AttributeError:
                pass
            # find all meaningful links on that page and write to the temporary file
            stop_appending , n_= find_useful_links_and_update(soup, file, stop_appending, last_question_datetime, found_links)
            
            if stop_appending or (i==int(links[topic][1])):
                print('reached the last newest topic')
                print('Total number of new links: ',l)
                print('Writing to : ',temp_file_name)
                if l > 0:
                    print(len(found_links.keys()))
                    for link_ in found_links.keys():
                        print(link_)
                        file.write(link_)
                    file.write('\n')
                break
            time.sleep(0.3)

            if i % 20 == 0:
                time.sleep(1)
            l+=n_
        file.close()
        # make more than one update on a single day possible
        num_appends.append(l)
        if l > 0 :
            # open the files anew in order to start merging
            file = open(temp_file_name, 'r')
            new_file = open('Q&Alinks/' + topic + '_new' +'_links.txt', 'w')
            try:
                old_file = open('Q&Alinks/' + topic + '_links.txt', 'r')
            except FileNotFoundError:
                old_file = open('Q&Alinks/' + topic + '_links.txt', 'w')
            # merge files
            success = merge_files(old_file, new_file, temp_file = file)
            file.close()
            new_file.close()
            old_file.close()
            if success == 0:
                os.rename('Q&Alinks/' + topic + '_links.txt','thrashbin/' + topic + '_links.txt' )
                os.rename('Q&Alinks/' + topic + '_new' +'_links.txt','Q&Alinks/' + topic + '_links.txt')
            else:
                print('merging files was unsuccessful')
    return num_appends
import shutil
"""
FUNCTION: download_everything_update_final: using the newly donwloaded links -> get the questions and answers on those links
INPUT: areas: the areas we want to scrape
       append: if we want to append or download everything anew
       json_TF, csv_TF : boolean holding the format we want to store the data it
       num_appends : now many appends there were in the get_links step
OUTPUT: None (the downloaded data is stored to files)
"""
def download_everything_update_final(areas, append, json_TF, csv_TF,num_appends):

    print(type(areas))
    # allow for single strings as topics (not only lists of strings)
    if not isinstance(areas,list):
        areas=[areas]
    for area,n_appends in zip(areas,num_appends):
        print(area)
        if n_appends==0:
            print('there were no appends, going to the next area')
            continue
        
        if append:
            temp_file_name = date_.today()
            # for every
            temp_file_name = 'Q&Alinks_t/' + area + '_' +str(temp_file_name.year)+'_'+str(temp_file_name.month)+'_'+str(temp_file_name.day)+'_links.txt'
            try:
                links_file = open(temp_file_name, 'r')

            except FileNotFoundError:
                print('Links to that area : {} : were not found.'.format(area))
                continue
            try:
                csv_file = open('Q&Adata_csv/' + area + '.csv', 'a')
            except FileNotFoundError:
                print('writing on a new file')
                links_file = open('Q&Alinks/' + area + '_links.txt', 'r')
                csv_file = open('Q&Adata_csv/' + area + '.csv', 'w')
        else:
            links_file = open('Q&Alinks/' + area + '_links.txt', 'r')
            a = input('Overwriting (if existing) the file {} Do you wish to continue : y/n'.format('Q&Adata_csv/' + area + '.csv'))
            if a == 'y':
                print('writing on a new file')
                csv_file = open('Q&Adata_csv/' + area + '.csv', 'w')
            else:
                return
        data = []
        # load the id
        id_file = open('id.txt', 'r')
        id = int(id_file.read())
        id_file.close()
        l = 1 # current number of links
        nr = 1 # number of temporary files
        links_lines = links_file.readlines()

        # check if there are no updates
        if len(links_lines)==0:
            print('\n\n\nThere are no updates for {}'.format(area))
            continue
        for line in links_lines:
            if line == '\n':
                continue
            html = session.get(line[:-1], headers=headers).text
            # print(html.encoding)

            print(line)
            print(type(html))

            soup = bs4.BeautifulSoup(html, "html5lib")

            # title
            try:
                title = soup.find('div', class_='boxWhite--container').h1.text
            except Exception as e:
                print(e)
                continue
            # question box
            question_box = soup.find('div', class_='boxWhite--container')
            print(title)

            # delete all stupid text
            for i in question_box.find_all('div'):
                i.decompose()

            question_box.find('h1').decompose()
            for i in question_box.find_all('br'):
                i.decompose()
            question = question_box.get_text('\n', strip=True)
            if (question.startswith('gelöscht')):
                continue
            # print(question)

            # answer
            answer = soup.find("article").get_text('\n', strip=True)
            # print('\n\n' + answer)
            data.append({'id': id,
                         'link': line[:-1],
                         'title': str(title),
                         'area': area,
                         'question': question,
                         'answer': answer})

            id += 1

            if id % 4 == 0:
                time.sleep(1)
            # for each 7000 topics create a temporary file so that we don't have to loop through everything again
            # in case of an unexpected failure of the program - we will have to make some changes to the code
            # in order to begin from a certain link and a certain id
            if l % 7000 == 0:
                if not os.path.isdir('Q&Adata/temp'):
                    os.mkdir('Q&Adata/temp')
                f_name = 'Q&Adata/temp/' + area + 'temp' + str(nr) + '.json'
                json_file = open(f_name, 'w')
                json.dump(data, json_file, ensure_ascii=False)
                nr += 1
            l += 1
            # print(data)
            if csv_TF:
                writer = csv.writer(csv_file,delimiter = ',')

                writer.writerow([answer,area,id,line[:-1],question,str(title)])
        if json_TF:
            update_json_files(append, area, data)
        id_file = open('id.txt', 'w')
        id_file.write(str(id))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", required=False,default=False, action = 'store_const', const = True,
                        help="update all areas")
    parser.add_argument("-a", "--area", required=False, nargs='+',
                        help="areas of law")
    parser.add_argument("-o", "--overwrite", required=False,default=False, action = 'store_const', const = True,
                        help="overwrite")
    parser.add_argument('-c','--csv', required = False, default= False, action='store_const',const = True)
    parser.add_argument('-j','--json', required = False, default= False, action='store_const',const = True)
    args = vars(parser.parse_args())
    areas = args['area']
    if not args['full'] and (areas == None):
        print('please select areas!')
        exit()
    if args['full']:
        areas = list(links.keys())
        print('you have chosen to update all areas')
    else:
        print("areas you've chosen: ",areas)

    append = not bool(args['overwrite'])

    print('append option chosen: ',append)
    exit_ = False
    for area in areas:
        if area not in links.keys():
            print('This area is no available for download: ',area)
            exit_= True
    if exit_:
        print('Available areas: ',str(list(links.keys()))[1:-1])
        print('exiting with status code -1')
        exit(-1)
    print('\n\n\n...\n')
    time.sleep(2)
    print('Downloading links for update')

    num_appends = get_links_update_final(areas)
    print(args['csv'],args['json'])
    if (args['csv']==True) and (args['json']==True):
        print('downloading')
        download_everything_update_final(areas,append,True,True,num_appends)
    elif args['csv']:
        download_everything_update_final(areas,append,False,True,num_appends)
    elif args['json']:
        download_everything_update_final(areas,append,True,False,num_appends)
    else:
        print('please choose an update option (--csv / --json)')
    #
