
"""
Author : Myrsini Gkolemi
Date : 15/01/2021
Description : This file includes fucntions
that perform analysis with deep categorization model using
MeaningCloud API.
"""

import json
import os
import socket
import sys

import meaningcloud
import pandas
import requests

def jsonToCsv(jsonFile):
    """
    Description analysis with deep categorization model Emotion analysis
    Response example: [{'code': 'Anger', 'label': 'Anger', 'abs_relevance': '1', 'relevance': '100'}, {'code': 'Joy', 'label': 'Joy', 'abs_relevance': '1', 'relevance': '100'}]
    .json to .csv format
    """
    data = []
    head, _ = os.path.split(jsonFile)   
    dstFile = head + "\\emotions.csv"

    with open(jsonFile, mode = "r", encoding = "utf-8") as sf:
        try:
            for jsonObj in sf:
                channelObj = json.loads(jsonObj)   
                emotions = channelObj["response"]
                valuesList = [channelObj["channel"],0,0,0,0,0,0,0,0]
                for emotion in emotions:
                    if emotion["code"] == "Anger":
                        valuesList[1] = 1
                    elif emotion["code"] == "Anticipation":
                        valuesList[2] = 1
                    elif emotion["code"] == "Disgust":
                        valuesList[3] = 1
                    elif emotion["code"] == "Fear":
                        valuesList[4] = 1
                    elif emotion["code"] == "Joy":
                        valuesList[5] = 1
                    elif emotion["code"] == "Sadness":
                        valuesList[6] = 1
                    elif emotion["code"] == "Surprise":
                        valuesList[7] = 1
                    elif emotion["code"] == "Trust":
                        valuesList[8] = 1
                    else:
                        print("Error: No such emotion exists. Exiting...")
                        sys.exit()
                data.append(valuesList)
        except json.JSONDecodeError as e:
            print(jsonObj)
            exit()
    
    dataCsv = pandas.DataFrame(data, columns = ["id", "Anger", "Anticipation", "Disgust", "Fear", "Joy", "Sadness", "Surpise","Trust"])
    dataCsv.to_csv(dstFile, index = False)


def getEmotionsCsv():
    """
    Call deepCategorization API to get Emotions detected for each channel's description.
    """
    dstFile = "emotions.json"
    mode = "w"
    key = "<KEY>"
    model = 'Emotion_en'
    polarity = 'n'

    if len(sys.argv) >= 3:
        csvData = pandas.read_csv(sys.argv[1], skipinitialspace = True, usecols = id)
        lineNumber = int(sys.argv[2]) 
        print(lineNumber) 
        descriptionList = csvData.description.to_list()
        channelList = csvData.id.to_list()
    else:
        print("Error: Not enough arguments. Exiting...")
        sys.exit()

    with open(dstFile, mode = mode, encoding="utf-8") as df:  
        for i in range(lineNumber, len(channelList)):
            try:        
                re = meaningcloud.DeepCategorizationResponse(meaningcloud.DeepCategorizationRequest(key, model=model, txt=descriptionList[i], polarity=polarity).sendReq())
                categories = re.getCategories()
            except socket.timeout as e:
                print("Error: Session Time out!", e)
                categories = []
            except requests.ReadTimeout as e:
                print("Error: Read Timeout! Too long txt.", e)
                categories = []
            objJson = {"channel" : channelList[i], "description": descriptionList[i], "response" : categories}        
            df.write(json.dumps(objJson))
            df.write('\n')
