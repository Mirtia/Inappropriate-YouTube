"""
Author : Anonymous
Date : 15/01/2021
Description : Used for post, emoticons and sentiment analysis (Sentistrength, 
emoji library).
"""

import json 
import pandas
import numpy 
import os
from os import listdir
import math
import emoji
from collections import Counter
import emosent
import statistics
import string
import warnings

class postsStats:

    def __init__(self, postFile):  
            self.postFile = postFile
            self.postsList = []
            self.postCountList = []
            

    def initPostsList(self):
        """
        Reads input from postFile.
        """
        try:
            with open(self.postFile, "r", encoding="utf-8") as sf:   
                for jsonObj in sf:
                    self.postsList.append(json.loads(jsonObj))                                        
        except IOError as e:
                print("Error: Something went wrong with reading the file. Check your file path and format." + str(e)) 
                exit()


    def initPostCountList(self):
        """
        Gets postCount list.
        """
        try:
            with open(self.postFile, "r", encoding="utf-8") as sf:   
                for jsonObj in sf:
                    self.postCountList.append(json.loads(jsonObj)["Community Tab"]["postCount"])                                        
        except IOError as e:
                print("Error: Something went wrong with reading the file. Check your file path and format." + str(e))
                exit() 


    def appendPostCount(self, csvFile):     
        """
        Appends postCount column to .csv.
        """                                    
        try:
            dataCsv = pandas.read_csv(csvFile)     
        except IOError as e:
            print("Error: Something went wrong with reading the csvFile. Check your file path and format." + str(e)) 
            exit() 
        
        with open(self.postFile, "r", encoding="utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    try:             
                        self.postsList.append(channel)                           
                        self.postCountList.append(channel["Community Tab"]["postCount"])
                    except KeyError as e:
                        print("Error: Key " + str(e) + " does not exist.")
                        exit()
        dataCsv["postCount"] = self.postCountList
        dataCsv.to_csv("postCount.csv", index = False)


    def getPostStats(self):
        """
        Prints table stats about posts.
        """
        if not self.postsList:
            self.initPostCountList()                
        meanCount = 0
        noCount = 0
        zeroCount = 0
        numCount = 0
        try:
            for count in self.postCountList:
                if count == -1:
                    noCount += 1
                elif count == 0:
                    zeroCount += 1
                else:
                    numCount += count       
        except TypeError as e:
            print("Error: TypeError." + str(e) + str(count))
        meanCount = numCount / len(self.postCountList)
        print("Average number of posts per channel: ", meanCount)
        print("Number of channels that have zero posts: ", zeroCount)
        print("Number of channels that do not have Community Tab available: ", noCount)


    def getMeanEmojiScore(self, emojiList):
        """
        Gets list of mean emoji score.
        """
        emojiScore = []
        meanScore = None
        for emo in emojiList:
            try:
                emojiIcon = emoji.emojize(emo)
                emojiScore.append(emosent.get_emoji_sentiment_rank(emojiIcon)["sentiment_score"])                      
            except KeyError as e:
                print("Error: Emoji not present in table. Skipping emoji...")                            
        try: 
            meanScore = statistics.mean(emojiScore)
        except statistics.StatisticsError as e:
            print("Error: Statistics error " + str(e) + ". Assigning invalid value. ")
            meanScore = None
        except TypeError as e:
            print("Error: Type Error " + str(e) + str(emojiScore))
        return meanScore


    def getMeanEmojiScoreAll(self, emojiList):
        emojiScores = []
        for nList in emojiList:
            emojiScores.append(self.getMeanEmojiScore(nList))
        return emojiScores

    
    def findTMUEmojis(self, emojiList):       
        """
        Finds ten most used emojis in given list.
        """     
        emojiCounter = Counter(emojiList) 
        return emojiCounter.most_common(10)

    
    def findTMUEmojisAll(self, emojiList):   
        """
        Finds ten most used emojis in given list 
        (for all lists).
        """   
        extendedList = []    
        for nList in emojiList:
            extendedList.extend(nList)  
        emojiCounter = Counter(extendedList)             
        return emojiCounter.most_common(10)

    
    def getEmojiListDescr(self, dscrFiles):
        """
        Returns all emojis found in description for each channel.
        """
        emojiList = []
        for dscrFile in dscrFiles:
            with open(dscrFile, mode="r", encoding="utf-8") as sf:
                for obj in sf:
                    tempList = []
                    description = json.loads(obj)["description"]
                    emojiList.append(self.findEmoticons(description))
        return emojiList  

    
    def getEmojiListPosts(self, postFiles):
        """
        Returns all emojis found in Community Tab's post for each channel.
        """
        emojiList = []
        for postFile in postFiles:
            with open(postFile, mode="r", encoding="utf-8") as sf:
                for obj in sf:
                    posts = json.loads(obj)["Community Tab"]["posts"]
                    tempList = []
                    for post in posts:
                        try:
                            emojis = self.findEmoticons(post["description"])                                
                            tempList.extend(emojis)
                        except KeyError as e:
                            print("Error: KeyError " + str(e) + ". Skip description of post.")
                    emojiList.append(tempList)          
        return emojiList
            
        
    def getDataRow(self, pairList):
        return [x for (x,y) in pairList]
        
    
    def getEmojisOneHotEncoding(self, text, keyEmojis):
        bitList = [0] * len(keyEmojis)
        for i, emoji_ in enumerate(keyEmojis):
            if emoji_ in text:
                bitList[i] = 1
        return bitList

    
    def printEmojiStats(self, dscrFile, postFile):
        emojiListDescr = self.getEmojiListDescr([dscrFile])
        emojiListPosts = self.getEmojiListPosts([postFile])
        descrScore = self.getMeanEmojiScoreAll(emojiListDescr)
        postScore = self.getMeanEmojiScoreAll(emojiListPosts)

        print(self.getDataRow(self.findTMUEmojisAll(emojiListDescr)))
        print(self.getDataRow(self.findTMUEmojisAll(emojiListPosts)))


    def addEmojiColumns(self, dscrFiles, postFiles, path=""):
        """
        Finds ten most used emojis in post description (for all categories)
        Finds then most used emojis in channel description (for all categories)
        Appends 0-1 emoji columns to current csv.
        [Description average emoji score -
        Post description average emoji score]

        Args:
            dscrFiles ([type]): files that contain description column
            postFiles ([type]): files that contain post descriptions
            path: path for csv source and destination file (str, optional): [description]. Defaults to "".
        """
        emojiListDescr = self.getEmojiListDescr(dscrFiles)
        emojiListPosts = self.getEmojiListPosts(postFiles)
        descrScore = self.getMeanEmojiScoreAll(emojiListDescr)
        postScore = self.getMeanEmojiScoreAll(emojiListPosts)

        emojisDescRow = self.getDataRow(self.findTMUEmojisAll(emojiListDescr))
        emojisPostRow = self.getDataRow(self.findTMUEmojisAll(emojiListPosts))
    
        data = []

        for description, posts in zip(emojiListDescr, emojiListPosts):
            row = []                
            row.extend(self.getEmojisOneHotEncoding(description, emojisDescRow))                              
            row.extend(self.getEmojisOneHotEncoding(posts, emojisPostRow))                
            data.append(row)
    
        df = pandas.DataFrame(data, columns = emojisDescRow + emojisPostRow)
        df["emojiDescriptionScore"] = descrScore
        df["emojiPostsScore"] = postScore
        srcCsv = path + "\\main\\all.csv"
        dstCsv = path + "\\main\\all_emoji.csv"
        cf = pandas.read_csv(srcCsv)  
        joinedDf = pandas.concat([cf, df], axis=1)
        joinedDf.to_csv(dstCsv, index=False)  
      
        
    def generateSentistrengthFormat(self, parentFolder):
        """
        Creates file with channelId and descriptions in each file.
        """    
        if not self.postsList:
            self.initPostsList()
        
        for channel in self.postsList:
            posts = channel["Community Tab"]["posts"]
            df = pandas.DataFrame(columns=["description"])
            index = 0
            for post in posts:
                try:
                    df.loc[index] = post["description"]                   
                except KeyError as e:
                    print("0 Error: KeyError." + str(e) + channel["id"])
                    df.loc[index] = ""
                    
                index = index + 1
                    
            df.to_csv(parentFolder + channel["id"] + ".txt", sep="\t", encoding="utf-8")
      

    def readSentistrengthResults(self, category, path):
        """
        Reads and interprets results generated by Sentistrength.
        """
        meanNegativePolarity = []
        meanPositivePolarity = []
        ids = []

        path = path + category + "\\"
        idsFile = path + "ids.txt"
        
        filesR = self.returnFolderFiles(path)               
        filesClass = self.sortIds(list(filesR), idsFile)
        
        for f in filesClass:
                
            numpyColumns = numpy.loadtxt(path + f, delimiter='\t', dtype='str')
            try:
                if numpyColumns.size != 0:
                    negativePolarity = numpyColumns[:,2].astype(numpy.int)
                    positivePolarity = numpyColumns[:,1].astype(numpy.int)
                    meanNegativePolarity.append(math.ceil(numpy.mean(negativePolarity)))
                    meanPositivePolarity.append(math.ceil(numpy.mean(positivePolarity)))
                else:
                    meanNegativePolarity.append(0)
                    meanPositivePolarity.append(0)
            except IndexError as e:
                negativePolarity = numpyColumns[2].astype(numpy.int)
                positivePolarity = numpyColumns[1].astype(numpy.int)
                meanNegativePolarity.append(negativePolarity)
                meanPositivePolarity.append(positivePolarity)
                    
            ids.append(f.replace("_ClassID.txt", ""))

        dfMean = pandas.DataFrame({'id': ids, 'postPositivePolarity': meanPositivePolarity, 'postNegativePolarity': meanNegativePolarity})
        dfMean.to_csv(path + category + "_sentistrength.csv", index=False)
            

    def returnFolderFiles(self, path):
        return (f for f in listdir(path) if f.endswith("_ClassID.txt"))


    def sortIds(self, filesToSort, idsFile):
        """
        Sorts ids from files.
        """    
        with open(idsFile, "r", encoding = "utf-8") as idf:           
            ids =  idf.read().splitlines() 
        sortedList = []
        for id_ in ids:                        
            try:
                matchId = [x for x in filesToSort if id_ in x]
                sortedList.append(matchId[0])           
            except KeyError as e:
                print("Error: Key " + str(e) + " does not exist.")
                print("Program exiting...")                                
                exit()
        return sortedList


    def analyzePostEmoticons(self):
        allEmojis = []
        emoticonsChannel = []
        for channel in self.postsList:
            emoticonsList = []
            posts = channel["Community Tab"]["posts"]
            res = None
            for post in posts:
                try:                        
                    res = self.findEmoticons(post["description"])                    
                except KeyError as e:
                    print("Error: KeyError " + str(e) + ". Skip description of post.")            
            if res:
                if type(res) == list:
                    emoticonsList.extend(res)
                else:
                    emoticonsList.append(res)
                allEmojis.extend(res)

            emoticonsChannel.append(emoticonsList)
            
        return (allEmojis, emoticonsChannel)


    def analyzeDescriptionEmoticons(self):
        allEmojis = []
        emoticonsChannel = []
        for channel in self.postsList:
            emoticonsList = []
            description = channel["description"]
            res = None
            try:    
                res = self.findEmoticons(description)
            except KeyError as e:
                print("Error: KeyError " + str(e) + ". Skip description of post.")
            
            if res:
                if type(res) == list:
                    emoticonsList.extend(res)
                else:
                    emoticonsList.append(res)
                allEmojis.extend(res)
            emoticonsChannel.append(emoticonsList)

        return (allEmojis, emoticonsChannel)


    def analyzeEmoticons(self, mode):
        """ 
        Analyzes emoticons        
        ranging from -1 to +1, calculated as the mean of the discrete sentiment distribution of negative (-1), 
        neutral (0) and positive (+1).
        mode: post or channel
        """
        if not self.postsList:
            self.initPostsList()
        
        emoticonsChannel = []       # emoticons per Channel (all posts)  
        meanEmoticonScore = []      # mean emoticon score per channel
        mostUsedEmoji = []          # most used emoji of each channel 
        tenMostUsedEmoji = []       # ten most used emojis per category (with their counts)
        allEmojis = []

        if mode == "post":
            allEmojis, emoticonsChannel = self.analyzePostEmoticons()
        elif mode == "description":
            allEmojis, emoticonsChannel = self.analyzeDescriptionEmoticons()
        # ===========================
        
        allCount  = Counter(allEmojis) 
        
        for emojiList in emoticonsChannel:
            
            listCount = Counter(emojiList)
            mostUsedEmoji.append(listCount.most_common(1))            
            emojiScore = []

            for emo in emojiList:
                try:
                    emojiIcon = emoji.emojize(emo)
                    emojiScore.append(emosent.get_emoji_sentiment_rank(emojiIcon)["sentiment_score"])                      
                except KeyError as e:
                    print("Error: Emoji not present in table. Skipping emoji...")                            
            try:                    
                meanEmoticonScore.append(statistics.mean(emojiScore))
            except statistics.StatisticsError as e:
                print("Error: Statistics error " + str(e) + ". Assigning invalid value. ")                
            except TypeError as e:
                print("Error: Type Error " + str(e) + str(emojiScore))
    
        with open("logfile.txt", "a", encoding="utf8") as f:
            f.write(str(statistics.mean(meanEmoticonScore)))
            f.write('\n')
        
        print(allCount.most_common(10))


    def findEmoticons(self, text):               
        """
        Finds emojis in text given.
        """
        emojiList = []
        regionalPrefix = []
        text = str(text)
        skin = False
        for index, word in enumerate(text):
            if skin:
                skin = False
                continue
            if any(char in emoji.UNICODE_EMOJI for char in word):                 
                emojiFound = emoji.demojize(word) 
                if "regional" in emojiFound:  
                    regionalPrefix.append(emojiFound)
                    if len(regionalPrefix) == 2:
                        emojiList.append(regionalPrefix[0] + regionalPrefix[1])
                        regionalPrefix.clear()
                elif "skin" in emojiFound:                    
                        emojiList.append(emojiFound + emoji.demojize(text[index - 1]))                                  
                        skin = True
                else:                     
                    emojiList.append(emojiFound)
        return emojiList