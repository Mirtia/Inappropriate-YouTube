"""
Author : Myrsini Gkolemi
Date : 08/02/2021
Description : This file includes functions to collect data for each user or video that is not 
reachable through the Youtube Data API.
"""

import json
import re
import time

import requests
from bs4 import BeautifulSoup


def findDictionary(text, start):
    """
    Returns string representation of dictionary found in script nonce section.
    """
    curlyBraceR = curlyBraceL = 0
    for index,char in enumerate(text):        
        if char == "{":
            curlyBraceL += 1
        elif char == "}":
            curlyBraceR += 1
        if curlyBraceL == curlyBraceR and curlyBraceL > 0:
            print(curlyBraceL, curlyBraceR)
            return text[start:index + 1]


def returnKeyValue(dictionary, targetKey):
    """
    Returns value of given key in the dictionary.
    """
    try:            
        value = dictionary[targetKey]            
        return value
    except (KeyError, TypeError) as e:
        nestedStruct = None   
        if type(dictionary) == dict:
            nestedStruct = list(dictionary.values())  
        elif type(dictionary) == list:
            nestedStruct = dictionary  
        else:             
            return None        
        returnValue = None
        for elem in nestedStruct:                           
            returnValue = returnKeyValue(elem, targetKey)                    
            if returnValue:     break  
    return returnValue 


def getMail(channelId):
    """
    Checks if About Tab has an email address button.
    """
    url = "https://www.youtube.com/channel/" + channelId + "/about"
    engHeaders = {"Accept-Language": "en-US, en;q=0.5", 'User-Agent' : \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/83.0.4103.97 Safari/537.36"}
    srcCode = requests.get(url, headers = engHeaders).text
    bsSrc = BeautifulSoup(srcCode, "lxml",)
    scriptSection = bsSrc.find_all("script")    
    email = False    
    for script in scriptSection:
        strScript = str(script)        
        if """businessEmailLabel""" or """For business inquiries""" in strScript:
            email = True
            break
    return {"email" : email}


def getReasonRemovedVideo(videoId):
    """
    Extracts reason from script section in page source of video.
    """
    print(videoId)
    url = "https://youtube.com/watch?v=" + videoId
    engHeaders = {"Accept-Language": "en-US, en;q=0.5", 'User-Agent' : \
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    srcCode = requests.get(url, headers = engHeaders).text
    bsSrc = BeautifulSoup(srcCode, "lxml",)
    scriptSection = bsSrc.find_all("script")

    errorMsg = None    
    for script in scriptSection:
        strScript = str(script)
        if """{"status":"ERROR","reason":""" in strScript:            
            jsonResponse = json.loads(findDictionary(strScript, 69))            
            errorMsg = returnKeyValue(jsonResponse, targetKey="simpleText")
    return errorMsg


def getChannelRemovedReason(channelId):
    """
    Extracts reason from script section in page source of channel.
    """
    url = "https://youtube.com/channel/"+ channelId
    engHeaders = {"Accept-Language": "en-US, en;q=0.5", 'User-Agent': \
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    srcCode = requests.get(url, headers = engHeaders).text
    bsSrc = BeautifulSoup(srcCode, "lxml",)
    scriptSection = bsSrc.find_all("script")  
    errorMsg = None
    for script in scriptSection:  
        strScript = str(script)   
        if "alertRenderer" in strScript: 
            jsonResponse = json.loads(findDictionary(strScript, 59))            
            errorMsg = returnKeyValue(jsonResponse, targetKey="simpleText")
    return errorMsg



def getChannelId(videoId):
    """
    Returns channelId from a specific video.
    Not Youtube API dependant.
    """
    engHeaders = {"Accept-Language": "en-US, en;q=0.5", 'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) \
        Gecko/20100101 Firefox/52.0'}    
    response = requests.get("https://www.youtube.com/watch?v=" + videoId, headers = engHeaders, timeout = 10)
    srcCode = response.text 
    bsSrc = BeautifulSoup(srcCode, "lxml")
    scriptSection = bsSrc.find_all("script") 
       
    if response.status_code == 404:
        return None        
    channelId = None
    for script in scriptSection:      
        try:
            # channelId is of fixed length
            channelId = (re.search(r'\"channelId\":\".{24}\"', script.text))
            if channelId == None:
                continue
            else: 
                return channelId.group(0)[13:37]        
        except AttributeError as e:
            print("videoId:", videoId, "\n", e)           
            exit()    
    return channelId


def getPostDetails(postUrl):
    """
    Gets post details given a post url.
    """
    engHeaders = {"Accept-Language": "en-US, en;q=0.5", \
        'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    
    try:
        response = requests.get("https://www.youtube.com/" + postUrl, headers = engHeaders, timeout = 30)
        srcCode = response.text
          
    except requests.exceptions.ConnectionError as e:  
        # Retry request after two minutes
        time.sleep(120)
        response = requests.get("https://www.youtube.com/" + postUrl, headers = engHeaders, timeout = 30)
        srcCode = response.text        
    except requests.exceptions.TooManyRedirects as e:
        print("Error: Too many Redirections.", e)  
        exit()
    except requests.exceptions.Timeout as e:        
        print("Error: Timeout Error:", e)
        exit()
    except requests.exceptions.RequestException as e:
        print("Error: There was an ambiguous exception that occurred while handling your\
              request. Exiting...", e)
        exit()

    bsSrc = BeautifulSoup(srcCode, "lxml")
    scriptSection = bsSrc.find_all("script")  
    text = {}

    if response.status_code == 404:
        return {"Error": "Post has been removed."}

    for script in scriptSection:
        strScript = script.text
        if "var ytInitialData" in strScript:
            
            jsonResponse = json.loads(findDictionary(strScript, 20))            
            likeCount = 0
            targetTab = 3   # Default Tab number.
            contentJson = jsonResponse["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
            try:
                contentJson[targetTab]                
            except IndexError as e:
                print("Tab Error: Tabs are less.( " + str(e) + " )" + "\nPost:" + postUrl)
                targetTab = 0   # In rare ocassions the tabs are 0 in number. 1/16000
            try:
                thumbnailVideo = contentJson[targetTab]\
                ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]\
                ["contents"][0]["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]["backstageAttachment"]\
                ["videoRenderer"]["videoId"] 
            except KeyError as e:
                print("Thumbnail Error: Key does not exist.( " + str(e) + " )" +"\nPost:" + postUrl)
                thumbnailVideo = None
            except IndexError as e:
                print("Thumbnail Error: Index out of range.( " + str(e) + " )" +"\nPost:" + postUrl)
                thumbmnailVideo = None
            try:
                # datePublished key should always exist.
                
                datePublished = contentJson[targetTab]\
                ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]\
                ["contents"][0]["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]\
                ["publishedTimeText"]["runs"][0]["text"]

                likeCount = contentJson[targetTab]\
                ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]\
                ["contents"][0]["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]\
                ["voteCount"]['simpleText']

                # likeCount may be zero, so key does not exist in this case. => likeCount = 0
            except KeyError as e:
                if e == "likeCount":
                    print("likeCount Error: Key does not exist.( " + str(e) + " )" + "\nPost:" + postUrl)                       
                elif e == "datePublished":
                    datePublished = None

            description = ""
            tags = []   
            descriptionMetaData = ""
            channelLinks = []                
            
            try:
                descriptionList = contentJson[targetTab]\
                    ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]\
                    ["contents"][0]["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]\
                    ["contentText"]["runs"]
                descriptionMetaData = jsonResponse["metadata"]["channelMetadataRenderer"]["description"]
            
                for token in descriptionList:
                    description += token["text"]
                    if "@" == token["text"][0]:
                        tags.append(token["text"].strip('@'))
                        channelLinks.append(token["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"])
            
            except KeyError as e:
                print("Description list Error: Key does not exist.( " + str(e) + " )" + "\nPost:" + postUrl)  

            hashTags = re.findall(r'#[A-Za-z_0-9]+\s',description)       
            youtubeLinks = re.findall(r'https:\/\/www.youtube\.com\/[^\s]+|https:\/\/youtu\.be\/[^\s]+|https:\/\/youtube\.com\/[^\s]+', descriptionMetaData)
            extIterator = re.finditer(r'https:\/\/(?!.*(www.youtube\.com|youtu\.be|youtube\.com)\/)[^\s]+', descriptionMetaData)
            
            externalLinks = []
            if extIterator:
                for match in extIterator:                    
                    externalLinks.append(match.group(0))       

            postId = postUrl.strip("https://www.youtube.com/post/")
            
            text = {"id":postId, "description": description, "datePublished":datePublished, "youtubeLinks" : youtubeLinks, \
                    "thumbnailVideo" : thumbnailVideo, "externalLinks" : externalLinks, "channelLinks" : channelLinks, "likeCount" : likeCount, \
                    "hashTags" : hashTags, "tags" : tags}
            
    return text       
