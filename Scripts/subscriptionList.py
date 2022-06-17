"""
Author : Myrsini Gkolemi
Date : 08/02/2021
Description : This file includes functions to collect subscriptions for 
each channel using Youtube Data API v3.
"""

import json
import os

import pandas
import requests
from apiclient.discovery import build
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

# File to authenticate credentials.
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("INPUT_JSON_PATH")

class subscriptionList:

    def __init__(self, srcFile, dstFile, apiKey):

        self.subList = []
        self.srcFile = srcFile
        self.dstFile = dstFile
        self.apiKey = apiKey       
        self.youtube = build('youtube', 'v3', developerKey = self.apiKey)
    

    def createSubscriptionsJson(self, mode):
        """
        Gets the subscriptions of all channels in self.srcFile
        """
        with open(self.srcFile, "r", encoding = "utf-8") as sf, open(self.dstFile, mode, encoding = "utf-8") as df:

            for channel in sf:
                channelId = (json.loads(channel))["id"]                
                subItems = self.getSubscriptionsList(channelId)                 
                subscriptions  = []

                for item in subItems:
                    subscriptions.append(item["snippet"]["resourceId"]["channelId"])
                df.write(json.dumps({"id": channelId, "subscriptionList":subscriptions, "subscriptionCount" : len(subscriptions)}))    
                df.write('\n')      
    

    def getSubscriptionsList(self, channelId):
        """
        Get subscriptions channelIds with Youtube v3 API.
        """
        response = []
        try:
            request = self.youtube.subscriptions().list(part="snippet", channelId = channelId, maxResults = 100)
            response = request.execute()       

            while response and "nextPageToken" in response:
                    
                nextPage = response["nextPageToken"]
                request = self.youtube.subscriptions().list(part="snippet", channelId = channelId, maxResults=100, pageToken = nextPage)
                prevResponse = response["items"]            
                response = request.execute()
                response["items"].extend(prevResponse)
        
        except HttpError: 
            print("Warning: No public subscriptions.")

        return response["items"] if response else response
    

    @staticmethod
    def appendSubscriptionCount(csvFile, subscriptionFiles):     
        """
        Append to the end of .csv an extra column that contains the subscriptionCount.
        """
        subscriptionCountList = []                        
        try:
                dataCsv = pandas.read_csv(csvFile)     
        except IOError as e:
                print("Error: Something went wrong with reading the csvFile. Check your file path and format." + str(e)) 
                return
        
        for subFile in subscriptionFiles:
            with open(subFile, "r", encoding="utf-8") as sf:
                    for jsonObj in sf:
                            channel = json.loads(jsonObj)
                            try:  
                                subscriptionCount = len(channel["subscriptionList"])                                      
                                subscriptionCountList.append(subscriptionCount)
                            except KeyError as e:
                                print("Error: Key " + str(e) + " does not exist.")
                                exit()
        dataCsv["subscriptionCount"] = subscriptionCountList            
        dataCsv.to_csv("all_updated.csv", index = False)

            