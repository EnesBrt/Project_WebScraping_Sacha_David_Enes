# import libraries
from datetime import datetime, timezone, timedelta
import os.path
#import BeautifulSoup4 For installation
from bs4 import BeautifulSoup
import urllib.request
import requests
import re
import json
from models import Post
import utils
import pandas as pd
from random import randint
from time import sleep


# debugMode = False  # True for use temporary file
# # targetUrl = "https://new.reddit.com/r/bapcsalescanada/search?q=CPU&restrict_sr=1&sort=new"
# targetUrl = "https://new.reddit.com/r/bapcsalescanada/new/"

def loadPage(targetUrl, debugMode = False, localFile = 'reddit.html'):
    localFile = "data\\" + localFile
    if not debugMode or (debugMode and not os.path.isfile(localFile)):
        # Download web page

        # To prevent the server from denying access (403)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read().decode('utf-8')

        soup = BeautifulSoup(webpage, features="html.parser")

        # Save web page in local file
        f = open(localFile, mode="w", encoding='utf-8')
        f.write(soup.prettify()) # Save pretty format
        f.close()

    else:
        # Read the file containing the web page
        f = open(localFile, mode="r", encoding='utf-8')
        webpage = f.read()
        f.close()

    # Parse the HTML content
    soup = BeautifulSoup(webpage, features="html.parser")
    # print(soup.prettify())
    return soup

def parseHTMLPart():
    CLASS_POST_LIST = 'QBfRw7Rj8UkxybFpX-USO'
    CLASS_POST_ITEMS = '_1oQyIsiPHYt6nx7VOmd1sz'
    CLASS_POST_TITLE = '_eYtD2XCVieq6emjKBH3m'
    CLASS_POST_VOTES = '_1rZYMD_4xY3gRcSS3p8ODO'
    CLASS_POST_COMMENTS = 'FHCV02u6Cp2zYL0fhQPsO'

    nodePosts = soup.find(['div'], attrs={'class', CLASS_POST_LIST})
    for oneComment in nodePosts.find_all(['div'], attrs={'class', CLASS_POST_ITEMS}):
        post_id = oneComment['id']
        post_created = None
        post_title = oneComment.find(['h3', 'span'], attrs={'class', CLASS_POST_TITLE}).text.strip()
        post_nbVotes = oneComment.find(['div'], attrs={'class', CLASS_POST_VOTES}).text.strip()
        post_nbComments = oneComment.find(['span'], attrs={'class', CLASS_POST_COMMENTS}).text.strip()
        post = Post(post_id, post_created, post_title, post_nbVotes, post_nbComments)
        listPosts.append(post)
        print(post)
        print('--------')

    print('NbPosts=' + str(len(listPosts)))
    return listPosts


def parseScriptPart(oldDate):

    try:
        for oneScript in soup.find_all('script', attrs={'id': 'data'}):
            regScript = re.compile(r'(window\.___r = )(.*)(;)')
            match = regScript.match(str(oneScript.text.strip()))
            if match:
                json_data = match.group(2)
                parsed_json = (json.loads(json_data))
                # print(json.dumps(parsed_json, indent=4, sort_keys=True))
                # print(parsed_json['posts']['models'])
                for key, value in parsed_json['posts']['models'].items():
                    if 'id' in value :
                        post_id = value['id']
                        if 'isLocked' in value:
                            if value['isLocked'] == False:
                                if len(post_id) < 20:
                                    # print(f"{key} : {value}")
                                    post_title = value['title']
                                    post_nbVotes = value['score']
                                    post_nbComments = value['numComments']
                                    post_created = int(value['created'])
                                    post = Post(post_id, post_created, post_title, post_nbVotes, post_nbComments)
                                    # print(post)
                                    listPosts.append(post)

                                    currentDate = utils.timestamp_to_datetime(post_created)
                                    if oldDate > currentDate:
                                        # Save the oldest date
                                        oldDate = currentDate
                                        # print(str(post_created) + " > " + utils.datetime_to_string(oldDate))

    except ValueError:
        # print("Script hasn't 'id' attribute")
        print(ValueError)
        pass


    print('NbPosts=' + str(len(listPosts)))
    return listPosts, oldDate


print('###################################')

listPosts = []
targetUrl = "https://new.reddit.com/r/bapcsalescanada/new/"
startDate = datetime.now()
oldDate = datetime.now()
numPage = 0
localFileName = 'reddit_page_' + str(numPage).zfill(4) +'_.html'
endDate = startDate.today() - timedelta(90)
print('Search until ' + utils.datetime_to_string(endDate) + '...')
lastid = ""

while oldDate > endDate:
    # Load and parse page content
    soup = loadPage(targetUrl, debugMode=True, localFile=localFileName)
    # listPosts = parseHTMLPart() # Alternative without date
    listPosts, oldDate = parseScriptPart(oldDate)

    if lastid == listPosts[-1].id:
        #Security infinity loop
        print('No more posts !')
        break

    # Next loop
    lastid = listPosts[-1].id
    targetUrl = "https://new.reddit.com/r/bapcsalescanada/new/?after=" + lastid
    numPage += 1

    localFileName = 'reddit_page_' + str(numPage).zfill(4) + '_.html'
    # print('URL : ' + targetUrl)
    # localFileName = 'reddit_' + utils.timestamp_to_string(listPosts[0].created, "%Y%m%d_%H%M%S") + '.html'

    # Pause 300ms to 1000ms
    sleep(randint(3,10)/100)

    print('Page ' + str(numPage) + ' : ' + utils.datetime_to_string(startDate) + ' -> ' + utils.datetime_to_string(oldDate))


print('###################################')

if listPosts:
    # save data into an output
    # fields = ['id', 'created', 'title', 'title', 'nbVotes', 'nbComments']
    df = pd.DataFrame.from_records([post.to_dict() for post in listPosts])
    df.sort_values(by='intCreated', ascending=False, inplace=True)
    df.reindex()
    print(df.to_string())

