# import libraries
from datetime import datetime, timezone
import os.path
#import BeautifulSoup4 For installation
from bs4 import BeautifulSoup
import urllib.request
import re
import json
from models import Post


debugMode = True  # True for use temporary file
targetUrl = "https://new.reddit.com/r/bapcsalescanada/search?q=CPU&restrict_sr=1&sort=new"

def loadPage():
    # Use temporary file
    htmlFile = 'reddit.html'

    if not debugMode or (debugMode and not os.path.isfile(htmlFile)):
        # Download web page

        # To prevent the server from denying access (403)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read().decode('utf-8')

        soup = BeautifulSoup(webpage, features="html.parser")

        # Save web page in local file
        f = open(htmlFile, mode="w", encoding='utf-8')
        f.write(soup.prettify()) # Save pretty format
        f.close()

    else:
        # Read the file containing the web page
        f = open(htmlFile, mode="r", encoding='utf-8')
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

    listPosts = []

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


def parseScriptPart():
    try:
        listPosts = []

        for oneScript in soup.find_all('script', attrs={'id': 'data'}):
            regScript = re.compile(r'(window\.___r = )(.*)(;)')
            match = regScript.match(str(oneScript.text.strip()))
            if match:
                json_data = match.group(2)
                parsed_json = (json.loads(json_data))
                # print(json.dumps(parsed_json, indent=4, sort_keys=True))
                # print(parsed_json['posts']['models'])
                for key, value in parsed_json['posts']['models'].items():
                    # print(f"{key} : {value}")
                    if 'id' in value :
                        post_id = value['id']
                        post_title = value['title']
                        post_nbVotes = value['score']
                        post_nbComments = value['numComments']
                        post_created = int(value['created']/1000)
                        post = Post(post_id, post_created, post_title, post_nbVotes, post_nbComments)
                        print(post)
                        listPosts.append(post)

    except ValueError:
        # print("Script hasn't 'id' attribute")
        print(ValueError)
        pass


    print('NbPosts=' + str(len(listPosts)))
    return listPosts


print('###################################')

# Load and parse page content
soup = loadPage()
# listPosts = parseHTMLPart()
listPosts = parseScriptPart()

print('###################################')