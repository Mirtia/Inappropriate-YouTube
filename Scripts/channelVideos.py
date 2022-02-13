"""
Author : Anonymous
Date : 15/01/2021
Description : This file behaves as a bridge for mapping videos to channels.
It includes functions to split data according specific categories
and modifying/adding new information to files.
"""

import json
import os

import pandas
from apiclient.discovery import build
from googleapiclient.errors import HttpError

import beauSoupMessage

# File to authenticate credentials.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<PATH>.json"

reasons = [
    "Unavailable channel", 
    "Spam, deceptive practices", 
    "(C) infringment", 
    "Non existant channel", 
    "Violation of Youtube Terms of Service", 
    "Harass bully or threaten", 
    "Violation of Community Guidelines", 
    "Brand accounts not supported", 
    "Violation of Google Terms of Service", 
    "Account linked to acount with (C) infringement", 
    "Violation policy on nudity or sexual content"
    ]
       
possibleMessages = [
    "This channel is not available.",
    "This account has been terminated due to multiple or severe violations of YouTube's policy against spam, deceptive practices, and misleading content or other Terms of Service violations.",
    "This account has been terminated because we received multiple third-party claims of copyright infringement regarding material the user posted.",
    "This channel does not exist.",
    "This account has been terminated for a violation of YouTube's Terms of Service.",
    "This account has been terminated due to multiple or severe violations of YouTube's policy prohibiting content designed to harass, bully or threaten.",
    "This account has been terminated for violating YouTube's Community Guidelines.",
    "This account has been suspended since Brand Accounts are not supported for G Suite for Education users in primary/secondary schools.",
    "This account has been terminated for violating Google's Terms of Service.",
    "This account has been terminated because it is linked to an account that received multiple third-party claims of copyright infringement.",
    "This account has been terminated due to multiple or severe violations of YouTube's policy on nudity or sexual content."
    ]

class channelVideos:

    def __init__(self, srcFile, dstFile, apiKey):
        self.buffer = []       
        self.dstFile = dstFile
        self.srcFile = srcFile
        self.source = True
        self.apiKey = apiKey
        self.messageCounts = [0] * 11
        self.youtube = build('youtube', 'v3', developerKey = self.apiKey)


    def __clearBuffer(self):
        self.buffer.clear()


    def negateSource(self):        
        self.source = not self.source   


    def dumpFile(self):    
        with open(self.dstFile,"w", encoding = "utf-8") as df:
            for jsonObj in self.buffer:
               df.write(json.dumps(jsonObj))    
               df.write('\n') 


    def parseChannelsFile(self):       
        self.__clearBuffer()
        with open(self.srcFile, "r", encoding = 'utf-8') as sf:
            for jsonObj in sf:
                self.buffer.append(json.loads(jsonObj))

    def readFile(self, srcFile):
        buffer = []
        with open(srcFile, "r", encoding = 'utf-8') as sf:
            for jsonObj in sf:
                buffer.append(json.loads(jsonObj))
        return buffer
    
    def changeSrcDstFiles(self, srcFile, dstFile):
        """
        Changes source and destination file
        """
        self.srcFile = srcFile
        self.dstFile = dstFile

    def createChannelsFile(self, extraKeys = [], source = None, condition = True):

        """
        Maps videos to channel. More than one video may
        correspond to the same channel.  
        Parameters:             
        extraKeys: Keys you wish to keep for the mapping.
        condition: lambda expression
        """
        with open(self.srcFile, "r", encoding = "utf-8") as sf:
            for jsonObj in sf:
                videoJson = json.loads(jsonObj)
                try:
                    existingChannel = next((channel for channel in self.buffer \
                        if channel["id"] == videoJson["snippet"]["channelId"] and condition), None)
                    
                    video = {}
                    for key in extraKeys:                       
                        if ":" in key:
                            nestedKeys = key.split(":")                           
                            temp = videoJson
                            for nKey in nestedKeys:
                                try:                                    
                                    temp = temp[int(nKey)]
                                except ValueError:
                                    temp = temp[nKey]                               
                            video[nestedKeys[-1]] = temp
                        else:
                            video[key] = videoJson[key]
                    
                    if "simpleText" in video:
                        video["simpleText"] = videoJson["simpleText"] 

                    if existingChannel:  
                        existingChannel['videoIds'].append(video)
                    else:
                        self.buffer.append({"id":videoJson["snippet"]["channelId"], "videoIds" : [video]})
            
                except KeyError as e:                    
                    print("Error: Key does not exist.( " + str(e) + " )")                      


    def splitChannels(self):
        """
        Splits channels to disturbing and suitable.
        Suitable: All of their videos are suitable.
        Disturbing: At least one video is disturbing.
        """
        with open(self.srcFile, "r", encoding = "utf-8") as sf:
            
            base = os.path.basename(self.srcFile)
            filename = os.path.splitext(base)[0] 
            print(filename)
            
            with open(filename + "Suitable.json", "w", encoding = "utf-8") as sdf,\
                 open(filename + "Disturbing.json","w", encoding = "utf-8") as ddf:

                    for channelObj in sf:
                        channel = json.loads(channelObj)

                        channelVideos = channel["videoIds"]
                        disturbingCount = suitableCount \
                        = madeForKidsRatio =  madeForKidsCount = madeForKidsDisturbing = 0

                        for video in channelVideos:
                            if video["madeForKids"]:
                                madeForKidsCount += 1
                            if video["classification_label"] == "disturbing":
                                if video["madeForKids"]:
                                    madeForKidsDisturbing +=1
                                disturbingCount += 1
                            elif video["classification_label"] == "suitable": 
                                suitableCount += 1
                      
                        try:
                            suitableRatio = suitableCount / len(channelVideos)
                        except ZeroDivisionError as e:
                            print("Error: Division by zero.( " + str(e) + " )")
                            
                        try:
                            madeForKidsRatio = madeForKidsCount / len(channelVideos)
                        except ZeroDivisionError as e:
                            print("Error: Division by zero.( " + str(e) + " )")

                        channel["disturbingCount"] = disturbingCount
                        channel["suitableCount"] = suitableCount                        
                        channel["suitableRatio"] = suitableRatio
                        channel["madeForKidsRatio"] = madeForKidsRatio
                        channel["madeForKidsVideosCount"] = madeForKidsCount
                        channel["madeForKidsDisturbing"] = madeForKidsDisturbing
                        channel["videoIds"] = channelVideos

                        if suitableRatio == 1:
                            sdf.write(json.dumps(channel))
                            sdf.write("\n")
                             
                        elif disturbingCount > 0:
                            ddf.write(json.dumps(channel))
                            ddf.write("\n")
    
            
    def printMadeForKidsStats(self):   
        """
        Computes madeForKids statistics (ratio and counts).
        """
        madeForKidsVideosCount = madeForKidsDisturbingCount = madeForKidsChannelsCount = 0
        madeForKidsList = []
        notMadeForKidsList = []

        self.parseChannelsFile()   

        for channel in self.buffer:
            if channel["madeForKids"] == True:
                madeForKidsChannelsCount += 1
                madeForKidsList.append(channel)
            else:
                notMadeForKidsList.append(channel)

            madeForKidsVideosCount += channel["madeForKidsVideosCount"]
            madeForKidsDisturbingCount += channel["madeForKidsDisturbing"]

        madeForKids01 = [0] * 2
        for channel in madeForKidsList:
            madeForKids01[0] += channel["madeForKidsDisturbing"]
        for channel in notMadeForKidsList:
            madeForKids01[1] += channel["madeForKidsDisturbing"]

        madeForKidsDisturbingRatio = (madeForKidsDisturbingCount / madeForKidsVideosCount)
        
        print("'madeForKids' videos: ", madeForKidsVideosCount)
        print("'Disturbing madeForKids' videos: ", madeForKidsDisturbingCount, \
                "\nRatio 'madeForKids': ", madeForKidsDisturbingRatio)
        
        print("madeForKids channels: ", madeForKidsChannelsCount)
        print("madeForKids channels mean disturbing records: ", madeForKids01[0] / len(madeForKidsList))
        print("not madeForKids channels mean disturbing records: ", madeForKids01[1] / len(notMadeForKidsList))

        
    
    def printRemovedMadeForKidsStats(self, videosFile):  
        """
        Counts and prints removed videos that are madeForKids.
        """      
        self.parseChannelsFile()
        videosList = self.readFile(videosFile)
        removedVideosCount = 0
        removedVideosTotal = 0
        for video in videosList:
            if video["simpleText"]:
                removedVideosTotal += 1
                if video["madeForKids"] == True:
                    removedVideosCount += 1  
                    
        print("Total videos removed: {0}" .format (removedVideosTotal))
        print("Disturbing 'madeForKids' videos removed: {0}, {1}%" .format ( removedVideosCount, \
            (removedVideosCount / removedVideosTotal)*100))
        
        
    def createSimpleTextFile(self):
        """
        Extracts reason why a channel is banned/removed
        and adds it to current dictionaries. 
        Writes new dictionaries to destination file.
        """
        self.parseChannelsFile()       
        with open(self.dstFile, "w", encoding ='utf-8') as df:  
            for channel in self.buffer:
                channelID = channel['id']
                request = self.youtube.channels().list(part = 'id', id = channelID)
                response = request.execute()    

                if 'items' not in response  or 'id' not in json.dumps(response['items']):         
                    channel["simpleText"] = beauSoupMessage.getChannelRemovedReason(channelID)
                else:
                    channel["simpleText"] = ""

                df.write(json.dumps(channel))    
                df.write('\n')


    def createConditionalChannelsFile(self, availability = False):  
        """
        Create file with available channels or not available channels.
        """
        print("Inside function")
        with open(self.dstFile, "w", encoding = 'utf-8') as df: 
            if not self.buffer:
                self.parseChannelsFile()
            if availability:
                for channel in self.buffer:
                    if not channel["simpleText"]:
                        df.write(json.dumps(channel))    
                        df.write('\n')
            else:
                for channel in self.buffer:
                    if "simpleText" in channel:
                            df.write(json.dumps(channel))    
                            df.write('\n')


    def extractResults(self, csvFile = None):
        """
        Prints in details reasons of channel removal.
        """
        if not self.buffer:
            self.parseChannelsFile()

        BCallRemoved = []
        BCuknownReason = []
        NBCallRemoved = []
        NBCsomeRemoved = []
        NBCnoneRemoved = []
        NBCnoDisturbing = []        
        ignoreCase = 0

        for channel in self.buffer:
            disturbing = 0
            removed = 0            
            videoIds = channel["videoIds"]
            for video in videoIds:
                if video["simpleText"]:
                    removed += 1
                if video["classification_label"] == "disturbing":
                    disturbing +=1

            if not channel["simpleText"]:   
                if removed == disturbing != 0:
                    NBCallRemoved.append(channel)
                elif removed == 0 and disturbing > 0:
                    NBCnoneRemoved.append(channel)
                elif removed < disturbing:
                    NBCsomeRemoved.append(channel)
                elif disturbing == 0 :
                    NBCnoDisturbing.append(channel)
                else:
                    ignoreCase += 1               
            else:  
                if removed == disturbing != 0:
                    BCallRemoved.append(channel)
                else:
                    BCuknownReason.append(channel)
                
        print("Channels/users that are not suspended and  have uploaded disturbing videos(according to the groundtruth set), with some of them removed for violating Youtube rules or being unavailable or private. : " + str(len(NBCsomeRemoved)))
        print("Channels/users that are not suspended and  have uploaded disturbing videos(according to the groundtruth set), with all of them removed for violating Youtube rules or being unavailable or private. : " + str(len(NBCallRemoved)))
        print("Channels/users that are suspended for violating Youtube rules and  their recorded disturbing content has been successfully removed. : " + str(len(BCallRemoved)))
        print("Channels/users that are suspended for violating Youtube rules even though there has been no sample of disturbing content (not recorded in the set). : " + str(len(BCuknownReason)))
        print("Channels/users that are not suspended and have uploaded disturbing videos(according to the groundtruth set), with none of them removed for violating Youtube rules or being unavailable or private. : " + str(len(NBCnoneRemoved)))
        print("Channels/users that are not suspended and have not uploaded disturbing videos. :" + str(len(NBCnoDisturbing)))
        print("Ignore case: " + str(ignoreCase))



    def getPublishedDetails(self, gdFile):
        """
        Adds published details and disturbing videos to disturbing.json channels.
        """
        self.parseChannelsFile()
        channelIds = [jsonObj["id"] for jsonObj in self.buffer]
      
        with open(gdFile, mode="r", encoding="utf-8") as sf:
            for videoObj in sf:
                video = json.loads(videoObj)
                position = [index for index, channel in enumerate(channelIds) if video["snippet"]["channelId"] == channel]
                if position and video["classification_label"] == "suitable":
                    newInfo = {"id" : video["snippet"]["channelId"], "classification" : video["classification_label"],\
                            "publishedAt" : video["snippet"]["publishedAt"]}
                    if "videoList" in self.buffer[position[0]]:
                        self.buffer[position[0]]["videoList"].append(newInfo)
                    else:
                        self.buffer[position[0]]["videoList"] = [newInfo]
               
        self.dumpFile()



    def simpleTextToCsv(self, csvFile):
        """
        Creates csvFile with simpleText info.
        """
        self.parseChannelsFile()
        data = []
        head, tail = os.path.split(self.srcFile)
        totalCount = 0

        for channel in self.buffer:
            totalCount += 1
            simpleText = channel["simpleText"]
            if simpleText:
                index = [index for index, message in enumerate(possibleMessages) if message == simpleText][0]
                self.messageCounts[index] += 1
        
        for i in range(0, len(possibleMessages)):
            data.append([self.messageCounts[i], self.messageCounts[i] / totalCount])

        dstCsv = pandas.DataFrame(data, columns = ["Count", "Percentage"], index=reasons)
        dstCsv.insert(loc=0, column="Reasons", value=reasons)
        dstCsv.to_csv(head + "//" + csvFile, index=False)     
       
    def addSimpleTextVideos(self, simpleTextVideos):
        """
        Replaces videoIds with simpleText on each channel.
        """        
        if not self.buffer:
            self.parseChannelsFile()
        channelList = []
        with open(simpleTextVideos, mode="r", encoding="utf-8") as hf:
            for jsonObj in hf:
                channel = json.loads(jsonObj)
                channelList.append(channel)
        
        print(len(channelList), len(self.buffer))
        
        for index, channel in enumerate(channelList):
            self.buffer[index]["videoIds"] = channel["videoIds"] 
