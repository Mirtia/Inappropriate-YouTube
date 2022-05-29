"""
Author : Myrsini Gkolemi
Date : 15/01/2021
Description : Supporting functions and processing 
for data files. Generates .csv, .json files.
Generates single column files for each key 
presented to dictionary. 
"""

import ast
import itertools
import json
import linecache
import os
import re
import string
import sys
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher

import numpy
import pandas
from apiclient.discovery import build
from googleapiclient.errors import HttpError

import beauSoupMessage
import cloudApi


def createColumnFiles(srcFile, keyword, prefix, condition = None):    
    """
    Description:
    Takes a keyword / list of keywords and generates single column files 
    Parameters:
    prefix:  used for file naming
    srcFile: source File (json)
    keyword: keyword or list of keywords in json
    condition: optional function to select range of specific key-values 
    """
    base = os.path.basename(srcFile)
    sfName = os.path.splitext(base)[0] 
    if not os.path.isdir(sfName):
        os.mkdir(sfName)
    keywordLists = {}
    if isinstance(keyword, list):
        for key in keyword:
            keywordLists[key] = []
    else:
        keywordLists = { keyword : [] }

    print(keywordLists)

    with open(srcFile, "r", encoding = "utf-8") as sf:  
        for jsonObj in sf:
            objDict = json.loads(jsonObj)
            # print(jsonObj)
            if not condition or (condition.__code__.co_argcount == 1 and condition(objDict)):   
                for key in keywordLists.keys():
                    if objDict:  
                        if isinstance(objDict, list):
                            if isinstance(objDict[0], dict):
                                for item in objDict:
                                    keywordLists[key].append(item[key])
                            else:                        
                                keywordLists[key].extend(objDict[key])
                        else:
                            keywordLists[key].append(objDict[key])
        
                    with open(sfName + "\\" + key + prefix, "w", encoding = "utf-8") as df:                
                        for entry in keywordLists[key]:
                            df.write(json.dumps(entry))
                            df.write('\n')
    print(sfName + "\\" + keyword[0] + prefix)


def createCSVFile(srcFile):
    """
    Creates csv file from json file.
    """
    base = os.path.basename(srcFile)
    sfName = os.path.splitext(base)[0] 
    print(sfName + ".csv") 
    with open(srcFile, "r", encoding = "utf-8") as sf:
        jsonFile = pandas.read_json(sf, lines = True)
        jsonFile.to_csv(sfName + ".csv", encoding = "utf-8", index = False)


def getSocialMediaCSV(jsonFile, dstFile):
    """
    Reads jsonFile and extract social media.
    """
    # Well known social media
    columns = ["id","instagram",
    "twitter","facebook","spotify","twitch","patreon","vk",
    "plus.google","play.google","steam","myspace", "merchandise"]
    
    data = []
    head, tail = os.path.split(jsonFile)

    with open(jsonFile, mode="r", encoding="utf-8") as sf:
        for jsonObj in sf:
            channel =  json.loads(jsonObj)
            links = channel["links"]
            dataRow = [channel["id"]] + [0] * 12 
            for linkPair in links:                    
                position = [index for index, sm in enumerate(columns[1:11]) if sm in linkPair["href"]]
                if position:
                    dataRow[position[0] + 1] = 1
                if "merch" in linkPair["text"].lower():
                    dataRow[-1] = 1
            data.append(dataRow)
    
    dstCsv = pandas.DataFrame(data, columns = columns)
    dstCsv.to_csv(head + "//" + dstFile, index=False)

    
def splitColumnsCsv(csvFile):
    """       
    Extracts columns of a .csv file to multiple .txt files.
    """
    tail = re.split('\.',csvFile) 
    path = tail[0] +"\\"
    data = pandas.read_csv(csvFile)  

    if not os.path.exists(path):
        os.makedirs(path)      

    varLists = []        
    varLists.append({"name": "featuredChannelsCount" ,"list": data.featuredChannelsCount.tolist()}) 
    varLists.append({"name": "subscriberCount","list": data.subscriberCount.tolist()}) 
    varLists.append({"name": "videoCount","list": data.videoCount.tolist()}) 
    varLists.append({"name": "descriptionCharCount","list": data.descriptionCharCount.tolist()})         
    varLists.append({"name": "viewCount","list": data.viewCount.tolist()})  
    varLists.append({"name": "topicCount","list": data.topicCount.tolist()})  
    varLists.append({"name": "country","list": data.country.tolist()})  
    varLists.append({"name": "madeForKids","list": data.madeForKids.tolist()})
    varLists.append({"name": "keywordsCount", "list": data.keywordsCount.tolist()})   

    topicCategories = data.topicCategories.tolist()        
    topicCategoriesList = []
    for tp in topicCategories:
        topicCategoriesList.extend(tp.strip('][').split(', '))
    varLists.append({"name": "topicCategories", "list": topicCategoriesList}); 

    try:
        for varList in varLists:
            with open(path + varList["name"], "w", encoding = "utf-8") as df:
                for el in varList["list"]:
                    df.write(str(el))
                    df.write("\n")
    except TypeError as e:
        print("Error: TypeError. Expected <type> string.")
        exit()  


def findTenMostUsed(csvFile, columnName):
    """
    Chooses a column from a .csv file and find its ten most
    used tokens. Create a file with 0-1 encoding.

    Args:
        csvFile (file)
        columnName (file)
    """
    head, tail = os.path.split(csvFile)
    dataCsv = pandas.read_csv(csvFile)      
    nameList = list(dataCsv[columnName])
    fullList = [] 
    columnList = []
    mostUsed = []

    for kList in nameList:
        try:
            eVal = ast.literal_eval(kList)                
            if type(eVal) == list:
                # print(eVal, type(eVal))
                fullList.extend(eVal)
                columnList.append(ast.literal_eval(kList))
                continue
        except ValueError as e:                
            # print("Error: ValueError, possible N/A ", e)
            continue
        
        columnList.append([])           

    mostUsed = Counter(fullList).most_common(10) #could be list
    print(columnName, mostUsed)
    columnNames = [tupl[0] for tupl in mostUsed]
    data = []  
    print(len(columnList))
    for keyList in columnList:
        dataRow = [0 for i in range(10)]
        for key in keyList:
            index = [i for i,k in enumerate(columnNames) if k == key]
            if index:   
                for i in index:
                    dataRow[i] = 1 
        data.append(dataRow)
        
    newCsv = pandas.DataFrame(data, columns = columnNames)


def padList(extendedList, tLength):
    return extendedList[:tLength] + [{}]*(tLength - len(extendedList))


def createDatePublishedCsv(srcFile):
    channelDates = []
    videoDatesDifference = []
    maxLen = 0
    with open(srcFile, mode="r", encoding="utf-8") as sf:
        for jsonObj in sf:
            channel = json.loads(jsonObj)
            dateCreated = channel["publishedAt"]
            dateParsed = datetime.strptime(dateCreated[0:10], '%Y-%m-%d')
            channelDates.append(dateParsed)
            videoDates = []
            maxLen = max(len(channel["videoList"]) , maxLen)
    print("Maximum length: ", maxLen)   


def readFile(srcFile):
    buffer = []
    with open(srcFile, mode="r", encoding="utf-8") as sf:
        for jsonObj in sf:
            buffer.append(json.loads(jsonObj))
    return buffer


def appendBuffer(srcList, dstList):
    for channel in srcList:
        if not [ch for ch in dstList if ch["id"] == channel["id"]]:
            dstList.append(channel)
    return dstList


def splitGeneralFile(generalFile, srcFiles, oldFiles, dstFiles):
    """
    Splits *general.json to its categories: suitable and disturbing.
    Appends general files' objects to the correct category according to 
    srcFiles.
    Applies on posts and channel details.
    Appends videos and classification labels.
    """
    buffer = readFile(generalFile)          
    baseList = readFile(srcFiles[0])  
    disturbingList = readFile(srcFiles[1])   

    suitableOldList = readFile(oldFiles[0])     
    disturbingOldList = readFile(oldFiles[1])

    buffer = appendBuffer(buffer, suitableOldList) 
    buffer = appendBuffer(buffer, disturbingOldList)

    with open(dstFiles[0], "w", encoding="utf-8") as sf, open(dstFiles[1], "w", encoding="utf-8") as df:
        for channel in buffer:
            indexS = [index for index,ch in enumerate(baseList) if ch["id"] == channel["id"]]               
            indexD = [index for index,ch in enumerate(disturbingList) if ch["id"] == channel["id"]]
            if indexS:
                # channel.update(baseList[indexS[0]])
                sf.write(json.dumps(channel))
                sf.write("\n")                
            
            if indexD:
                # channel.update(disturbingList[indexD[0]])
                df.write(json.dumps(channel))
                df.write("\n")


def printSubscriberStats(suitable, disturbing):
    baseList = readFile(suitable)
    disturbingList = readFile(disturbing)
    suitableHiddenTrue = len([elem for elem in baseList if elem["hiddenSubscriberCount"] == True]) 
    disturbinHiddenTrue = len([elem for elem in disturbingList if elem["hiddenSubscriberCount"] == True]) 
    print("Suitable")
    print("True: ", suitableHiddenTrue, "False:", len(baseList) - suitableHiddenTrue)
    print("Disturbing")
    print("True", disturbinHiddenTrue, "False:",  len(disturbingList) - disturbinHiddenTrue)
    

def printException():
    """
    Prints exception details.    
    """
    excType, excObject, tb = sys.exc_info()
    f = tb.tb_frame
    lineNumber = tb.tb_lineNumber
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineNumber, f.f_globals)
    print ('Exception in ({}, line {} "{}"): {}'.format(filename, lineNumber, line.strip(), excObject))


def averageColumnRatio(column_1, column_2):
    """
    Computes average ratio of two lists(unsorted) from single column files.
    (e.g. ratio viewCount/videoCount)

    Args:
        column_1 (file)
        column_2 (file)

    Returns:
        Average ratio of two columns
    """
    list_1 = []
    list_2 = []
    with open(column_1, mode="r") as c_1, open(column_2, mode="r") as c_2:
        list_1 = numpy.array([int((line.rstrip()[1:-1])) for line in c_1])
        list_2 = numpy.array([int((line.rstrip()[1:-1])) for line in c_2])
    
    listDivision = list_1 / list_2
    filteredList = listDivision[numpy.isfinite(listDivision)]
    
    return numpy.average(filteredList)


def getDisturbingRatio(srcFile):
    """
    Generates column file with disturbingRatio of each channel.
    """
    ratioList = []
    with open(srcFile, mode="r", encoding="utf-8") as sf:
        try:
            for jsonObj in sf:                    
                    channel = json.loads(jsonObj)
                    try:
                        ratioList.append(int(channel["disturbingCount"]) / int(channel["videoCount"]))
                    except ArithmeticError as e:
                        print("Error: Undefined ratio.")
                        ratioList.append(0)

        except KeyError as e:
            print("Error: ", e, "Chose a correct file.")
    with open("disturbingRatio", mode="w") as df:
        df.write("\n".join(map(str, ratioList)))


def getIdColumn(id_, csvFile):
    emotions = pandas.read_csv(csvFile)    
    return emotions.loc[emotions["id"] == id_].values.flatten().tolist()


def mergeEmotionsCsv(suitableJson, disturbingJson, oldCsv, newCsv):
    baseList = readFile(suitableJson)
    disturbingList = readFile(disturbingJson)
    baseList.extend(disturbingList)
    mergedListIds = [elem["id"] for elem in baseList]
    oldEmotions = pandas.read_csv(oldCsv)
    newEmotions = pandas.read_csv(newCsv)
    mergedEmotions = []
    for channel in baseList:
        value = getIdColumn(channel["id"], oldCsv)
        if not value:
            value = getIdColumn(channel["id"], newCsv)
        mergedEmotions.append(value)
    df = pandas.DataFrame(mergedEmotions, columns=["id", "Anger", "Anticipation", "Disgust", "Fear", "Joy", "Sadness", "Surpise", "Trust"])
    dfIds = [elem[0] for elem in mergedEmotions]
    if dfIds != mergedListIds:
        raise ValueError
    df.to_csv("merged_emotions.csv", index=False)


def getSocialMediaCount(baseCsv, socialMediaFiles, jsonFiles):
    """
    Adds linksCount column to .csv file and rewrites it.
    """
    baseChannelList = readFile(jsonFiles[0])
    baseChannelList.extend(readFile(jsonFiles[1]))
    socialMediaList = readFile(socialMediaFiles[0])
    socialMediaList.extend(readFile(socialMediaFiles[1]))
    
    
    socialMediaCol = [0] * len(baseChannelList)
    for index, channel in enumerate(socialMediaList):
        socialMediaCol[index] = len(channel["links"])
    
    df = pandas.read_csv(baseCsv)           
    df["linksCount"] = socialMediaCol            
    df.to_csv("all_updated.csv")
        

def fillColumns(csvFile):
    """
    Fills empty values with None, UKNOWN, 0.
    """
    df = pandas.read_csv(csvFile)
    df["madeForKids"].fillna("UNKNOWN", inplace=True)
    df["descriptionCharCount"].fillna(0, inplace=True)
    df["keywordsCount"].fillna(0, inplace=True)
    df["emojiDescriptionScore"].fillna("None", inplace=True)
    df["emojiPostsScore"].fillna("None", inplace=True)
    df.to_csv("updated.csv")
    

def extractDateColumn(srcFile):
    """
    Extracts date only (no time and Timezone).
    """
    channelList = readFile(srcFile)
    dates = []
    dstFile = "<FILE>"

    base = os.path.basename(srcFile)
    sfName = os.path.splitext(base)[0]

    with open(sfName + "_date", "w", encoding = "utf-8") as df:
        for channel in channelList:
            df.write(channel["publishedAt"][0:4])
            df.write('\n')
