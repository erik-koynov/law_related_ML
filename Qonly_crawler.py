"""
LegalTech Practical
This script crawls the www.---------.de website in order to download all questions in the forum,
which will be later used as data set for the text classification and information extraction tasks


FUNCTIONS: void areas_list()
           void last_forum_index(list)
           void download_links(list,list)
"""
import bs4
import requests
import json
import os
import argparse
"""
FUNCTION: areas_list: Get the links to the different forums which differ from each other with respect to the area of law
which their contents concern - f.e. the forum Arbeitsrecht should be about labor law etc.
The function creates a human readable txt file and a json file holding the pairs of title and link
to a forum
INPUT: None
OUTPUT: None
"""
def areas_list():
    a=requests.get('https://www.------------.de/forum_default.asp',headers={'user-agent':'Mozilla/5.0'}).text
    print(type(a))

    b=bs4.BeautifulSoup(a,"lxml")
    c=b.find("ul",class_="forum-overview--list")
    i=0
    links={}
    for link in c.find_all("a",{"class":"forum-overview--title-text"}):
        links[link.text] = link["href"]
        i+=1
    print(i)
    text_file = open("topics.txt",'w')
    json_file = open("topics.json","w")
    json.dump(links,json_file)
    for keys,values in links.items():
        print(keys)
        print(values)
        text_file.write(keys+'\n'+values+'\n')
    text_file.close()
    json_file.close()


with open("topics_new.json",'r') as t:
    links=json.load(t)
#print(len(links.keys()))


"""
FUNCTOIN: last_forum_index: Knowing the link to the first page of a forum, which is the one we previously stored in the topics.json
we can look for the link to the last page of a forum, which can be accessed by clicking the double arrows
>> at the bottom of the page.
The function creates topics_new .json and .txt files that hold the last page index of each forum so that
we can later loop to that page index in order to loop through all pages
INPUT: links: the list of links to the first page of a topic
"""


def last_forum_index(links):
    for key,link in links.items():
        a = requests.get(link,
                         headers={'user-agent': 'Mozilla/5.0'}).text
        a = bs4.BeautifulSoup(a, 'lxml')
        try:
            print(a.find_all('a', class_="paging-arrow outer")[0]['href'])
            c=a.find_all('a', class_="paging-arrow outer")[0]['href'].split('e=')[1]
            print(1)
            links[key] = (link,int(c))
        except IndexError as e:
            print(e)
    json_file=open("topics_new.json","w")
    json.dump(links,json_file)
    txt_file=open("topics_new.txt","w")
    for key,link in links.items():
        print(key,link)
        txt_file.write(key+',')
        txt_file.write(link[0]+','+str(link[1])+"\n")


import time
"""
FUNCTION: download_links : Download the links to each new topic and write them to a file called Topic_links.txt
INPUT: file : the list of links to the first page of a topic and number of pages in a topic
OUTPUT: None
"""
file=open("topics_new.json","r")

def download_links(file,list_of_topics):
    links = json.load(file)
    time_ = time.time()
    print(time_+120)
    i=2
    for key in links.keys():
        if key in list_of_topics:
            last_index=links[key][1]
            link_=links[key][0]
            
            if os.path.exists("links/"+str(key)+"_links.txt"):
                print('links\' path exists for: ',key)
                continue
            file=open("links/"+str(key)+"_links.txt","w")
            page=requests.get(link_,headers={'user-agent':'Mozilla/5.0'}).text
            soup=bs4.BeautifulSoup(page,'lxml')
            for link in soup.find_all('li',class_='forum-topic-list-item'):
               print(link.a['href'])
               file.write(str(link.a['href'])+'\n')
            file.write('\n')
            print("\n")

            while i<=last_index:
                if time_+0.7<time.time():
                    print(time_,time.time())
                    new_link=link_+'&page='+str(i)
                    page = requests.get(new_link, headers={'user-agent': 'Mozilla/5.0'}).text
                    soup = bs4.BeautifulSoup(page, 'lxml')
                    for link in soup.find_all('li', class_='forum-topic-list-item'):
                        print(link.a['href'])
                        file.write(str(link.a['href'])+"\n")
                    file.write("\n")
                    i+=1


"""
FUNCTION: make_dataset: after having download all links to the questions -> download all questions using the specified links\
INPUT: areas: the areas we want to scrape
OUTPUT: None (data is written to files)
"""
def make_dataset(areas):
    # allow for single strings as topics (not only lists of strings)
    if not isinstance(areas,list):
        areas=[areas]
    for area in areas:
        if os.path.exists(os.path.join('Q_only_data',area+'.json')):
            print('area exists for: ', area)
            continue
        # open the file from which we read the links to each question
        file=open("links/"+area+"_links.txt","r")
        #file=open("links/A2.txt",'r')
        time_ = time.time()
        print(time_ + 120)
        data=[]
        i=1
        p=1
        #txt_file=open(area+"_questions.txt","w")
        id_file=open('id_Qonly.txt','r')
        id=int(id_file.read())
        id_file.close()
        l=1
        nr=1
        for line in file.readlines():
            if line=='\n':
                time.sleep(3)
                p+=1
                continue
            # get rid of the \n character in the URL
            link="https://www.----------.de/"+line[:-1]
            print(link)
            #txt_file.write('\n'+str(i)+'\n'+str(link)+'\n')
            # next topic
            try:
                page=requests.get(link).text
            except Exception as e:
                print(e)
                continue
            soup=bs4.BeautifulSoup(page,'lxml')

            k=soup.find('div',class_="forum-topic--question forum-topic--post-box cleared highlight-content")
            #print(type(k))
            try:
                # title of the question
                title=k.find('div',class_="forum-topic--post-title cleared")
                #print(title.text)
                #print(type(title))
                #txt_file.write(title.text+'\n')
            except Exception as e:

                print(link)
                print(e)
                continue
            # actual question
            question=k.find('article',class_="summary")
            #print(question.text.startswith('ge'))
            try:
                if (question.text.startswith('gelöscht')):
                    continue
            except TypeError:
                continue 
            #print(type(question))
            #print(question.text)
            #txt_file.write(question.text+'\n\n\n')
            #print("\n\n\n")

            data.append({         'id': id,
                                  'link': line[:-1],
                                  'title': str(title.text),
                                  'area': area,
                                  'question': question.text})
            #print('data: ',data)
            i += 1
            id += 1

            if id%6==0:
                
                time.sleep(1)
            # for each 7000 topics create a temporary file so that we don't have to loop through everything again
            # in case of an unexpected failure of the program - we will have to make some changes to the code
            # in order to begin from a certain link and a certain id
	    
            if l%3000==0:
                if not os.path.isdir('Q_only_data/temp'):
                    os.mkdir('Q_only_data/temp')
                f_name='Q_only_data/temp/' + area + 'temp'+str(nr)+'.json'
                json_file = open(f_name, 'w')
                json.dump(data, json_file, ensure_ascii=False)
                nr+=1
            l+=1
        print(p)
        print(i)
        if not os.path.isdir('Q_only_data'):
            os.mkdir('Q_only_data')
        json_file = open('Q_only_data/' + area + '.json', 'w')
        json.dump(data, json_file, ensure_ascii=False)

        id_file = open('id_Qonly.txt', 'w')
        id_file.write(str(id))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--area", required=False, nargs='+',
                        help="areas of law")
    parser.add_argument("-f", "--full", required=False,default=False, action = 'store_const', const = True,
                        help="update all areas")
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

    download_links(file,areas)
    make_dataset(areas)


