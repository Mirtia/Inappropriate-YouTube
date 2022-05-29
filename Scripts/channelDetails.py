"""
Author : Myrsini Gkolemi
Date : 08/02/2021
Description :  This file includes functions for extracting information for each channel.
Information includes links, statistics, topicDetails ...
"""

import concurrent.futures
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from json.decoder import JSONDecodeError

import requests
from apiclient.discovery import build
from googleapiclient.errors import HttpError

import beauSoupMessage

# File to authenticate credentials.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<PATH>.json"

class channelDetails:
        
    def __init__(self, srcFile, dstFile, apiKey):
        self.apiKey = apiKey
        self.youtube = build('youtube', 'v3', developerKey = self.apiKey, cache_discovery = False)
        self.srcFile = srcFile
        self.dstFile = dstFile
        self.source = True
        self.buffer = []
   

    def readBuffer(self):
        if not self.buffer:
            self.__clearBuffer()
        with open(self.srcFile, mode = "r", encoding = "utf-8") as sf:
            for jsonObj in sf:
                channel = json.loads(jsonObj)
                self.buffer.append(channel)
    

    def __clearBuffer(self):
        self.buffer.clear()

    
    def negateSource(self):        
        self.source = not self.source   


    def dumpFile(self, mode = "w"):    
        with open(self.dstFile, mode, encoding = "utf-8") as df:
            for jsonObj in self.buffer:
               df.write(json.dumps(jsonObj))    
               df.write('\n') 


    def modifySrcDst(self, srcFile, dstFile):
        if self.dstFile != self.dstFile:
            self.srcFile = srcFile            
            self.dstFile = dstFile


    def getBrandingSettings(self, channelID):
        request = self.youtube.channels().list(part ='brandingSettings', id = channelID)   
        reply = request.execute()  
        return reply
    

    def getTopicDetails(self, channelID):
        request = self.youtube.channels().list(part ='topicDetails', id = channelID)   
        reply = request.execute()  
        return reply


    def getStatistics(self, channelID):
        request = self.youtube.channels().list(part ='statistics', id = channelID)   
        reply = request.execute()  
        return reply


    def getStatus(self, channelID):
        request = self.youtube.channels().list(part ='status', id = channelID)   
        reply = request.execute()  
        return reply        


    def getChannelDetails(self, channelID):                
        request = self.youtube.channels().list(part ="snippet, brandingSettings, topicDetails, statistics, status", id = channelID)   
        reply = request.execute()
        print(reply)  
        return reply


    def getChannelDetailsAll(self, mode, lineNumber = 0, source = None): 
        if source != None and source != self.source:           
            self.negateSource()
        self.__getChannelDetailsSource(mode, lineNumber) if self.source  else self.__getChannelDetailsBuffer(mode)
      

    def __getChannelDetailsBuffer(self, mode):
        try:
            if self.buffer:
                for i in range(len(self.buffer)):                 
                    channelID = self.buffer[i]["id"]                  
                    details = self.getChannelDetails(channelID)                
                    self.buffer[i] = details   
            else:
                print("Warning: Empty buffer. Cannot get Details.")
        except HttpError as e:   
            print("Error: HTTPError. Maximum quota exceeded.", e)         
            self.dumpFile(mode)                
      

    def __getChannelDetailsSource(self, mode, lineNumber = 0):        
        try:
            self.__clearBuffer()
            with open(self.srcFile,"r", encoding = "utf-8") as sf:
                for i in range(lineNumber):
                    sf.__next__() 
                for jsonObj in sf:                
                    channelID = (json.loads(jsonObj))["id"]               
                    details = self.getChannelDetails(channelID) 
                    print(details)
                    self.buffer.append(details)    
        except OSError:
            print("Warning: Something went wrong with reading the file.", e)
        except HttpError as e:
            print("Error: HTTPError. Maximum quota exceeded.", e)                  
            self.dumpFile(mode)         


    def getLinks(self, channelID):
        links = beauSoupMessage.extractSocialMediaLinks(channelID)
        return links


    def getLinksAll(self, source = None):        
        if source != None and source != self.source:          
            self.negateSource()
        self.__getLinksSource() if  self.source  else self.__getLinksBuffer()


    def __getLinksBuffer(self):
        if self.buffer:
            for i in range(len(self.buffer)):                 
                channelID = self.buffer[i]["id"]                  
                links = self.getLinks(channelID)
                self.buffer[i]["links"] = links                
        else:
            print("Warning: Empty buffer. Cannot get Links.")   

           
    def __getLinksSource(self):
        self.__clearBuffer()
        try:
            with open(self.srcFile, "r", encoding = "utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    channelID = channel["id"]
                    links = beauSoupMessage.extractSocialMediaLinks(channelID)
                    channel["links"] = links                    
                    self.buffer.append(channel)
        except OSError:
            print("Warning: Something went wrong with reading the file.")
 

    def getPostDetails(self, mode, lineNumber = 0, multithread = True):
        """
        Gets post details through BeautifulSoup. 
        Multithreaded.
        """
        with open(self.srcFile, "r") as sf, open(self.dstFile, mode, encoding = "utf-8") as df: 
            for i in range(lineNumber):
                    sf.__next__() 
            #-----Start timer-----
            start = time.time()
            for srcJson in sf:
                try:
                    posts = [] 
                    futures = []
                    postsList = []
                    try:
                        postsList = json.loads(srcJson)["posts"]  
                        postCount = len(postsList)    
                    except KeyError as e:
                        print("Error: KeyError. Posts do not exist.", e)
                        postCount = -1    
                    
                    channelId = json.loads(srcJson)["id"]
                    maxIndex = min(len(postsList), 100)   

                    if multithread:   
                        with ThreadPoolExecutor(max_workers = 40) as executor:                    
                            for post in postsList[0: maxIndex]:
                                futures.append(executor.submit(beauSoupMessage.getPostDetails, post))
                            for future in futures:                            
                                posts.append(future.result())
                    else:
                    # ---Sequential method---        
                        for post in postsList[0 : maxIndex]: 
                            returnedPosts = beauSoupMessage.extractPostDetails(post)
                            if returnedPosts:
                                posts.append(returnedPosts)
                     
                    dictToWrite = {}
                    dictToWrite["id"] = channelId
                    dictToWrite["Community Tab"] = {"posts" : posts, "postCount" : postCount} 
                    df.write(json.dumps(dictToWrite))    
                    df.write('\n')
                except JSONDecodeError as e:                                       
                    print("Error: Something went wrong with reading .json file.", e)
                    exit()
            end = time.time()
            print("Log: Execution time:", str(end - start))     
  

    def getPostsOfChannel(self, post):                
        """
        Calls BeautifulSoup based method to collect data from posts.
        """
        return beauSoupMessage.extractPostDetails(post)
   

    def finalizeChannelDetails(self): 
        """
        Parses and formats response json from Youtube Data API v3.         
        """            
        with open(self.dstFile, "w", encoding = "utf-8") as df:  
            for channel in self.buffer:               
                try:    
                    channel = channel["items"][0]        

                    subscriberCount = description = descriptionCount = keywords \
                    = keywordsCount = topics = country = featuredChannels = \
                    featuredChannelsCount = 0

                    channelId = beauSoupMessage.returnKeyValue(channel, "id")
                    statistics = beauSoupMessage.returnKeyValue(channel, "statistics")
                    viewCount = beauSoupMessage.returnKeyValue(statistics, "viewCount")
                    videoCount = beauSoupMessage.returnKeyValue(statistics, "videoCount")  
                    brandingSettings = beauSoupMessage.returnKeyValue(channel, "channel")                  
                    hiddenSubscriberCount = statistics["hiddenSubscriberCount"]      
                    subscriberCount =  "N/A" if hiddenSubscriberCount else statistics["subscriberCount"] 
                    publishedAt = beauSoupMessage.returnKeyValue(channel, "publishedAt")               
                   
                    if "description" in brandingSettings:
                        description = brandingSettings["description"]                    
                        descriptionCount = len(re.sub(r'\s+', '', description))
                    else:
                        description = ""
                        descriptionCount = ""
                   
                    if "keywords" in brandingSettings:
                       
                        keywords = brandingSettings["keywords"]
                        keywords = self.parseKeywords(keywords)
                        keywordsCount = len(keywords)
                    else:
                        keywordsCount = "N/A"
                        keywords = "N/A"
                    
                    try:
                        if  "topicCategories" in channel["topicDetails"]:
                            topicCategories = channel["topicDetails"]["topicCategories"]
                            topics = []
                            for topic in topicCategories:
                                topics.append(topic.replace('https://en.wikipedia.org/wiki/',"")) 
                            topicCount = len(topics)
                    except KeyError as e:
                        print("Error: KeyError topicDetails.( " + str(e) + channelId + " )") 
                        topicCategories = "N/A" 
                        topicCount = "N/A"         

                    try:
                        madeForKids = channel["status"]["madeForKids"]
                    except KeyError as e:
                        print("Error: KeyError madeforKids.( " + str(e) + channelId + " )", e) 
                        madeForKids = "N/A"
                    
                    if "country" in brandingSettings:
                        country = brandingSettings["country"]
                    else:
                        country = "N/A"
                                  
                    if "showRelatedChannels" in brandingSettings and brandingSettings["showRelatedChannels"] == True:
                        if "featuredChannelsUrls" in brandingSettings:
                            featuredChannels = brandingSettings["featuredChannelsUrls"]
                            featuredChannelsCount = len(featuredChannels)                       
                    else:
                        featuredChannels = "N/A"
                        featuredChannelsCount = "N/A"

                    detailsDict = {"id" : channelId, "videoCount" : videoCount, "hiddenSubscriberCount" : hiddenSubscriberCount, "subscriberCount" : subscriberCount,
                                   "viewCount": viewCount, "description" : description, "descriptionCharCount": descriptionCount,
                                   "keywords" : keywords, "keywordsCount" : keywordsCount, "topicCategories" : topics, "topicCount" : topicCount,
                                   "featuredChannels" : featuredChannels, "featuredChannelsCount" : featuredChannelsCount, 
                                   "country" : country, "madeForKids" : madeForKids, "publishedAt" : publishedAt}
                    
                    df.write(json.dumps(detailsDict))    
                    df.write('\n')
                              
                except KeyError as e:
                    print("Error: KeyError.( " + str(e) + channelId + " )", e)                   
                except TypeError as e:
                    print("Error: TypeError.( " + str(e) + ")", e)
            

    def parseKeywords(self, keywords):
        """  
        Parses keywords returned by Youtube Data API v3
        """
        keys = keywords.split()
        state = prevIndex = 0
        trueKeys = []
        for index,key in enumerate(keys):            
            if '"' in key and state == 0:
                state = 1
                prevIndex = index              
            elif '"' in key and state == 1:  
                trueKeys.append(" ".join(keys[(prevIndex):(index + 1)]).replace('\"',''))
                state = 0        
            elif '"' not in key and state == 0:                
                trueKeys.append(key)
            else:
                print("Log: Default")   
        return trueKeys        
     
  
    def getTimeCreatedAll(self):    
        """        
        Gets 'publishedAt' from snippet.
        (YouTube Data API v3 request)
        """    
        for index, channel in enumerate(self.buffer):
            request = self.youtube.channels().list(part ='snippet', id = channel["id"])   
            reply = request.execute()            
            try:
                self.buffer[index]["publishedAt"] = reply["items"][0]["snippet"]["publishedAt"]   
                logfile = open("temp", "a")
                print(self.buffer[index]["publishedAt"], file = logfile) 
                logfile.close()  
            except KeyError as e:
                print("Error: ", e)
                self.buffer[index]["publishedAt"] = None        
        self.dumpFile()
