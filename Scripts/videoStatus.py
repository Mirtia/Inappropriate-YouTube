"""
Author : Myrsini Gkolemi
Date : 15/01/2021
Description : This class is responsible of extracting reasons why a video is no longer available 
and group videos according to their avalaibility.
"""

import json
import os
import time

import pandas
from apiclient.discovery import build

import beauSoupMessage
import versionFile

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<PATH>.json"

reasons = [ "YouTube's Community Guidelines",
            "Video unavailable",
            "Private video",  
            "YouTube's Terms of Service",
            "YouTube's policy on nudity or sexual content",
            "YouTube's policy on spam, deceptive practices, and scams",
            "Terminated account",
            "Removed by uploader",           
            "Terminated account due to copyright infringement"]

class videoStatus:
    
    def __init__(self, srcFile, dstFile, apiKey): 

        self.removedStatus = self.normalStatus = self.totalStatus = 0
        self.buffer = []
        self.srcFile = srcFile
        self.dstFile = dstFile
        self.communityStandards  = 0
        self.unavailableVideo = 0
        self.privateVideo = 0
        self.termsOfService = 0
        self.nuditysexualContent = 0
        self.spamDeceptScam = 0 
        self.terminatedAccount = 0   
        self.removedByUploader = 0
        self.accountRemovedCpRight = 0
        self.apiKey = apiKey
        self.youtube = build('youtube', 'v3', developerKey = self.apiKey)

    
    def dumpFile(self): 
        """
        Dumps buffer to the destination file.
        """   
        with open(self.dstFile,"w", encoding = "utf-8") as df:
            for jsonObj in self.buffer:
               df.write(json.dumps(jsonObj))    
               df.write('\n') 


    def changeSrcDstFiles(self, srcFile, dstFile):
        """
        Changes source and destination file.
        """
        self.__clearBuffer()
        self.srcFile = srcFile
        self.dstFile = dstFile


    def __clearBuffer(self):
        """
        Clears temporary buffer.
        """
        self.buffer.clear()
   

    def printBuffer(self):
        """
        Prints temporary buffer contents.
        """
        print('\n'.join(map(str, self.buffer)))  


    def parseVideosFile(self):  
        """
        Parses source file to temporary buffer.
        """
        if self.buffer:
            self.__clearBuffer()
        with open(self.srcFile) as fs:
            for jsonObj in fs:               
                self.buffer.append(json.loads(jsonObj))
                self.totalStatus += 1   


    def getTotalObjects(self):
        """
        Gets total number of json objects in source file.
        """
        if self.totalStatus == 0:
            self.totalStatus = len(open(self.srcFile).readlines())       
        return self.totalStatus


    def getNormalStatus(self):
        """
        Gets count of videos that are available.
        """
        if self.normalStatus == 0:
            self.normalStatus = self.totalStatus - self.removedStatus
        return self.normalStatus


    def videoStatusToCsv(self, csvFile):
        """
        Converts .json to .csv.
        Reasons | Category | Percentage       
        """
        self.parseVideosFile()
        if self.removedStatus == 0:
            self.getVideosStatus()
        head, tail = os.path.split(self.srcFile)
        
        data = []  
        data.append([self.communityStandards, self.communityStandards/self.totalStatus])
        data.append([self.unavailableVideo, self.unavailableVideo/self.totalStatus])
        data.append([self.privateVideo, self.privateVideo/self.totalStatus])
        data.append([self.termsOfService, self.termsOfService/self.totalStatus])
        data.append([self.nuditysexualContent, self.nuditysexualContent/self.totalStatus])
        data.append([self.spamDeceptScam, self.spamDeceptScam/self.totalStatus])
        data.append([self.terminatedAccount, self.terminatedAccount/self.totalStatus])
        data.append([self.removedByUploader, self.removedByUploader/self.totalStatus])
        data.append([self.accountRemovedCpRight, self.accountRemovedCpRight/self.totalStatus])
        
        dstCsv = pandas.DataFrame(data, columns = ["Count", "Percentage"], index=reasons)
        dstCsv.insert(loc=0, column="Reasons", value=reasons)
        dstCsv.to_csv(head + "//" + csvFile, index=False)


    def getVideosStatus(self, source = True):
        """
        Gets and counts reasons why videos are removed.
        """
        if source:        
            self.parseVideosFile()
        disturbingList = self.buffer
        for video in disturbingList:
            try:                         
                if video["simpleText"]:           
                    if video["simpleText"] == "Video unavailable":
                        self.unavailableVideo += 1
                    elif video["simpleText"] == "This video has been removed for violating YouTube's Community Guidelines.":
                        self.communityStandards += 1
                    elif video["simpleText"] == "Private video":
                        self.privateVideo += 1
                    elif video["simpleText"] == "This video has been removed for violating YouTube's Terms of Service.":
                        self.termsOfService += 1
                    elif video["simpleText"] == "This video has been removed for violating YouTube's policy on nudity or sexual content.":
                        self.nuditysexualContent += 1
                    elif video["simpleText"] == "This video has been removed for violating YouTube's policy on spam, deceptive practices, and scams.":
                        self.spamDeceptScam += 1       
                    elif video["simpleText"] == "This video is no longer available because the YouTube account associated with this video has been terminated.":
                        self.terminatedAccount += 1  
                    elif video["simpleText"] == "This video has been removed by the uploader":
                        self.removedByUploader += 1      
                    elif video["simpleText"] == "The YouTube account associated with this video has been terminated due to multiple third-party notifications of copyright infringement.":
                        self.accountRemovedCpRight +=1
                    else:
                        print(video["simpleText"])
                        raise  ValueError("Error: Unexpected simpleText.")
                    self.removedStatus += 1
                else: 
                    self.normalStatus += 1
            except ValueError as e:
                print("Error: value error.")
            except KeyError as e:
                print("Error: Key does not exist.( " + str(e) + " )")

        return self.removedStatus            
    
    
    def createSimpleTextVideosFile(self):
        """
        Extracts video reasons of being removed using Beautiful Soup.
        Writes videos to buffer.
        """               
        self.parseVideosFile() 
        for index, video in enumerate(self.buffer):
            try:
                
                request = self.youtube.videos().list(part = "id", id = video["id"])
                response = request.execute()   

                if "id" not in response["items"]:            
                    self.buffer[index]["simpleText"] = beauSoupMessage.getReasonRemovedVideo(video["id"])
                else:
                    self.buffer[index]["simpleText"] = " "
    
            except KeyError as e:
                print("Error: Key does not exist.( " + str(e) + " )")
        self.dumpFile()


    def createSafeVideosFile(self):  
        """
        Creates safe videos set (videos included in 
        groundtruth set).
        """
        head, tail =  os.path.split(self.srcFile) 
        with open(self.srcFile, "r", encoding ='utf-8') as sf, open(versionFile.generateFile(head) + "nonDisturbing.json", "w", encoding = 'utf-8') as df: 
            if not self.buffer:
                self.parseVideosFile()
            for video in self.buffer:
                try:
                    if any("id" in x for x in video['items']):
                        df.write(json.dumps(video))    
                        df.write('\n')
                except KeyError as e:
                     print("Error: Key does not exist.( " + str(e) + " )")


    def createLabelVideosFile(self, label):   
        """
        Creates disturbing videos set (videos included in 
        groundtruth set).
        """
        head, tail =  os.path.split(self.srcFile) 
        # versionFile.generateFile(head) + "disturbing.json"
        with open(self.srcFile, "r", encoding ='utf-8') as sf, open(self.dstFile, "w", encoding = 'utf-8') as df: 
            if not self.buffer:
                self.parseVideosFile()
            for video in self.buffer:
                try:
                    if video['classification_label'] == label:
                        df.write(json.dumps(video))    
                        df.write('\n')
                except KeyError as e:
                    print("Error: Key does not exist.( " + str(e) + " )")


    def createRandomVideosFile(self):
        """
        Creates random videos set (videos not included in 
        groundtruth set).
        """
        self.__clearBuffer()
        self.parseVideosFile()
        head, tail = os.path.split(self.srcFile)
        
        name = versionFile.generateFile(head)
        with open(name + "random_dataset.json", "w", encoding = 'utf-8') as df:
            for video in self.buffer:
                if not "isGroundTruthVideo" in video:
                    df.write(json.dumps(video))
                    df.write("\n")
        return name + "random_dataset.json"

    
    def createPopularVideosFile(self):
        """
        Creates popular videos set (videos not included in 
        groundtruth set).
        """
        self.__clearBuffer()
        self.parseVideosFile()
        head, tail = os.path.split(self.srcFile)
     
        name = versionFile.generateFile(head)
        with open(name + "popular_dataset.json", "w", encoding = 'utf-8') as df:
            for video in self.buffer:
                if not "isGroundTruthVideo" in video:
                    df.write(json.dumps(video))
                    df.write("\n")  
        return name + "popular_dataset.json"

    
    def createMadeForKidsGroundtruth(self):
        """
        Collects madeForKids label for each video in the source file  
        via the Youtube Data API.
        """           
        self.parseVideosFile()    
        with open(self.dstFile, "w", encoding ='utf-8') as df:  
            for video in self.buffer:
                request = self.youtube.videos().list(part = 'status', id = video["id"])
                jsonD = request.execute()
                if len(jsonD["items"]):
                    video.update({"madeForKids" : jsonD["items"][0]["status"]["madeForKids"]})
                else:
                    video.update({"madeForKids" : "uknown"})
                df.write(json.dumps(video))    
                df.write('\n') 

    
    def printResults(self):
        """
        Prints frequencies/count of each specific reason a video from the parsed set may have 
        been removed.  
        """
        print('\nNumber of total videos: ' + str(self.totalStatus) + '\n')
        print("Number of removed videos: " + str(self.removedStatus) + '\n')
        print("Percentage of removed videos: %.2f"%(self.removedStatus / self.totalStatus) + '\n')
        print("Number of videos removed for violating Youtube Community Standards: " + str(self.communityStandards) + "\n")
        print("Number of unavailable videos: " + str(self.unavailableVideo) + "\n")
        print("Number of private videos: " + str(self.privateVideo) + "\n")
        print("Number of videos removed for violating YouTube's policy on nudity or sexual content: " + str(self.nuditysexualContent) + "\n")
        print("Number of videos removed for violating YouTube's Terms of Service: " + str(self.termsOfService) + "\n")
        print("Number of videos removed for violating YouTube's policy on spam, deceptive practices, and scams: " + str(self.spamDeceptScam) + "\n")
        print("Number of videos that are no longer available because the YouTube account associated with this video has been terminated: " + str(self.terminatedAccount) + "\n")
        print("Number of videos that its account has been terminated due to multiple third-party notifications of copyright infringement: " + str(self.accountRemovedCpRight) + "\n")
        print("Number of videos that have been removed by uploader: ", str(self.removedByUploader) + "\n")


    def getMadeForKidsCount(self, category):
        return len([elem for elem in self.buffer if elem["classification_label"] == category and elem["madeForKids"]])


    def getNotMadeForKidsCount(self, category):
        return len([elem for elem in self.buffer if elem["classification_label"] == category and not elem["madeForKids"]])


    def generateMadeForKidsfile(self):
        """
        Generates .csv with madeForKids videos information.
        """
        if not self.buffer:
            self.parseVideosFile()
        categories = ["suitable", "disturbing"]    
        madeForKidsCount = []
        notMadeForKidsCount = []
        for category in categories:
            madeForKidsCount.append(self.getMadeForKidsCount(category)) 
            notMadeForKidsCount.append(self.getNotMadeForKidsCount(category))
        data = {"category" : categories, "madeForKids" : madeForKidsCount, "not madeForKids" : notMadeForKidsCount}
        df = pandas.DataFrame(data)
        df.to_csv("madeForKidsVideos.csv", index=False)