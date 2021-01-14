# import libraries
from datetime import datetime, timezone, timedelta
import os.path
# import BeautifulSoup4 # For installation in PyCharm
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

# Initialization of global variables
soup = None
listPosts = []
debugMode = True  # True for use temporary file


def _loadPage(targetUrl: str, debugMode: bool = False, localFile: str = 'localpage.html') -> None:
    """
    Load page from target URL or from local file if debug mode is actived
    The soup global variable will contain the target html page

    :param targetUrl: URL of target website
    :param debugMode: True means that use local file and create if needed
    :param localFile: file name that will store html target file

    :return: nothing
    """
    global soup

    # Create a temporary directory if needed
    tempDir = 'temp'
    if not os.path.exists(tempDir):
        os.mkdir(tempDir)

    localFile = tempDir + "\\" + localFile
    if not debugMode or (debugMode and not os.path.isfile(localFile)):
        # Download web page

        # To prevent the server from denying access (403)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read().decode('utf-8')

        soup = BeautifulSoup(webpage, features="html.parser")

        # Save web page in local file
        f = open(localFile, mode="w", encoding='utf-8')
        f.write(soup.prettify())  # Save pretty format
        f.close()

    else:
        # Read the file containing the web page
        f = open(localFile, mode="r", encoding='utf-8')
        webpage = f.read()
        f.close()

    # Parse the HTML content
    soup = BeautifulSoup(webpage, features="html.parser")
    # print(soup.prettify())


def _parseHTMLPart():
    """
    EXPERIMENTAL function for scraping html code
    DO NOT USED because the date of post is missing!
    instead used parseScriptPart() function
    """
    global soup, listPosts

    if soup == None:
        return  # Security

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

    # print('NbPosts=' + str(len(listPosts)))


def _parseScriptPart(oldDate: datetime) -> datetime:
    """
    Scraping data from script JS and update posts list

    :param oldDate: previous oldest post date
    :return: oldest date of posts list
    """
    global soup, listPosts

    if soup == None:
        return  # Security

    try:
        for oneScript in soup.find_all('script', attrs={'id': 'data'}):
            regScript = r"(window\.___r = )(.*)(;)"
            matches = re.search(regScript, oneScript.string)
            if matches and len(matches.groups()) > 2:
                json_data = matches.group(2)
                parsed_json = (json.loads(json_data))
                # print(json.dumps(parsed_json, indent=4, sort_keys=True))
                # print(parsed_json['posts']['models'])
                for key, value in parsed_json['posts']['models'].items():
                    if 'id' in value:
                        post_id = value['id']
                        if 'isLocked' in value and value['isLocked'] == False:
                            # Exclusions of 'locked' posts that interrupt date sorting
                            if len(post_id) < 20:
                                # Exclusions of posts with huge ID, because they're strange
                                # print(f"{key} : {value}")
                                post_title = value['title']
                                post_score = int(value['score'])
                                post_upVoteRatio = float(value['upvoteRatio'])
                                post_nbComments = value['numComments']
                                post_created = int(value['created'])
                                post = Post(post_id, post_created, post_title, post_score, post_upVoteRatio, post_nbComments)
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

    # print('NbPosts=' + str(len(listPosts)))
    return oldDate


def getLastPosts(targetUrl: str, tillDate: datetime, debugMode: bool = False) -> pd.DataFrame:
    """
    Scraping data from script JS and update posts list.
    Use internet or local file according to debug mode

    :param tillDate: date until which posts must be retrieved
    :return: pandas dataframe sorted posts list
    """
    global soup, listPosts

    soup = None
    listPosts = []
    oldDate = datetime.now()
    numPage = 0
    # Prepare save first local file
    localFileName = 'reddit_page_' + str(numPage).zfill(4) + '_.html'
    print('Search until ' + utils.datetime_to_string(tillDate) + '...')
    lastid = ""

    while oldDate > tillDate:
        # Load and parse page content
        _loadPage(targetUrl, debugMode=debugMode, localFile=localFileName)
        # listPosts = parseHTMLPart() # Alternative without date
        oldDate = _parseScriptPart(oldDate)

        if len(listPosts) and lastid == listPosts[-1].id:
            # Security infinity loop
            print('No more posts !')
            break

        # Prepare next loop
        lastid = listPosts[-1].id
        targetUrl = "https://new.reddit.com/r/bapcsalescanada/new/?after=" + lastid
        numPage += 1

        # Prepare next save local file
        localFileName = 'reddit_page_' + str(numPage).zfill(4) + '_.html'

        # Pause between 300ms to 1000ms so as not to be detected by the server
        sleep(randint(3, 10) / 100)

        print('Page ' + str(numPage) + ' : oldest post = ' + utils.datetime_to_string(oldDate))

    if listPosts:
        print('--- Posts scraper done! ---')

        # save data into an dataframe
        # fields = ['id', 'intCreated', 'strCreated', 'title', 'title', 'nbVotes', 'nbComments']
        df = pd.DataFrame.from_records([post.to_dict() for post in listPosts])
        df.sort_values(by='intCreated', ascending=False, inplace=True)
        df.reindex()
        return df

    raise Exception('No publication!')
