"""
Author : Anonymous
Date : 08/02/2021
Description : This class produces TF-IDF vector from sampled texts.
"""

import json
import os
from collections import Counter

import emoji
import langdetect
import num2words
import numpy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer


class TF_IDF:

    langdetect.DetectorFactory.seed = 0
    acceptedOptions = ["about", "post", "keywords"]

    # 'az', 'kk', 'tg', 'so' are not available  
    languagePairs = {"ar" : "arabic", "az" : "azerbaijani", "da" : "danish", "nl" : "dutch", "en" : "english", "fi" : "finnish",
     "fr" : "french", "de" : "german", "gr" : "greek", "hu" : "hungarian", "id" : "indonesian", "it" : "italian", "kk" : "kazakh", 
     "ne" : "nepali", "nn" : "norwegian", "pt" : "portugish", "ro" : "romanian", "ru" : "russian",
     "sl" : "slovene", "sp": "spanish", "sw" : "swedish", "tg" : "tajik", "tr" : "turkish", "so" : "somali"}
    # The functions apply to English only texts

    def __init__(self, path = None, option = "about"):     
        """
        Accepted Options:
        1. about
        2. post
        3. keywords
        """   
        self.dirList = self.listDocuments(path)
        if option in self.acceptedOptions:
            self.option = option 
        else:
            raise ValueError
        self.textList = []
        self.channelIds = []
        self.TF = self.DF = self.IDF  = None
        self.TF_IDF = {}
        self.totalLength = 0
        

    def listDocuments(self, path):
        """        
        Returns list of .json files in the path directory.
        """  
        dirList = os.listdir(path)  
        isJson = all (doc.endswith(".json") for doc in dirList)             
        return None if not isJson else [path + doc for doc in dirList]


    def readDocumentsContent(self):
        """
        Reads contents of directory files.
        """ 
        textSamples = []
        for doc in self.dirList:        
            if self.option == "about":
                self.readChannelFiles(doc)
            elif self.option == "post":
                self.readPostFiles(doc)
   

    def readChannelFiles(self, srcFile):  
        """
        Reads files ignoring errors in decoding. - description.
        """
        print(srcFile)
      
        with open(srcFile, mode="r", encoding="utf-8") as sf:
            for obj in sf:               
                try:
                    channel = json.loads(obj)
                    if (langdetect.detect(channel["description"]) == "en"):
                        self.textList.append(channel["description"].encode('ascii', errors='ignore').decode('ascii'))  
                    else:
                        self.textList.append("")                      
                except langdetect.lang_detect_exception.LangDetectException as e:
                    self.textList.append("")
                    print("Error: ", e, channel["description"])
                self.channelIds.append(channel["id"])
        print(len(self.textList))

    def readPostFiles(self, srcFile):  
        """
        Reads files ignoring errors in decoding. - post description.
        """          
        with open(srcFile, mode="r", encoding="utf-8") as sf:            
            for obj in sf:
                postList = []
                channel = json.loads(obj)
                self.channelIds.append(channel["id"])
                for post in channel["Community Tab"]["posts"]:
                    try:
                        if (langdetect.detect(post["description"]) == "en"):
                            postList.extend(post["description"].encode('ascii', errors='ignore').decode('ascii'))
                    except KeyError as e:
                        print("Error: ", e, post, "\nPost is unavailable.") 
                    except langdetect.lang_detect_exception.LangDetectException as e:
                        print("Error: ", e, post["description"])
                if postList:                           
                    self.textList.append(' '.join(postList))
                else:
                    self.textList.append(" ")
                    

    def removePunctuation(self):
        """
        Removes punctuation symbols from text.
        """
        punctList = "!\"#$%&()*+-./:;,<=>?@[\]^_`{|}~\n"        
        for index, text in enumerate(self.textList):
            for punct in punctList:  
                self.textList[index]  = [token.replace(punct, "") for token in self.textList[index]]        
              

    def docToLowerCase(self):
        """
        Documents to lowercase. 
        Each document is a list of words.
        """
        for index, text in enumerate(self.textList):
            self.textList[index] = [token.lower() for token in text]         

    def isEmoji(self, text):
        """
        Returns True if there is an emoji in the text.
        """
        return any(char in emoji.UNICODE_EMOJI for char in text)


    def removeEmojis(self):
        """
        Removes emojis from each text.
        """
        for index, text in enumerate(self.textList):            
            textTokens = text.split()
            notEmoji = lambda x: not self.isEmoji(x)          
            self.textList[index] = [token for token in textTokens if notEmoji(token)]           
             

    def removeURL(self):
        """
        Removes URLs from each text.
        """        
        for index, text in enumerate(self.textList):  
            
            notURL = lambda x: "http" not in x and "www" not in x and ".com" not in x          
            self.textList[index] = [token for token in text if notURL(token)]             
            

    def removeSingleCharacters(self):
        """
        Removes single characters from each text.
        """ 
        for index, text in enumerate(self.textList):
            try:            
                isSingleChar = lambda x: len(x) == 1            
                self.textList[index]  = [token for token in text if not isSingleChar(token)]            
            except TypeError as e:
                print("Error: ", e)  
                print("text: ", text) 
                exit()        
        

    def removeStopWords(self): 
        """
        Removes stop words from each text.
        """    
        for index, text in enumerate(self.textList):            
            try:                             
                isStopWord = lambda x: x in stopwords.words("english")             
                self.textList[index] = [token for token in text if not isStopWord(token)]                 
            except OSError as e:
                print("Error: ", e, "text: ", text)
                exit()


    def removeApostrophe(self):
        """
        Removes apostrophe from each text.
        """ 
        for index, text in enumerate(self.textList):                    
            self.textList[index]  = [token.replace("'", "") for token in text] 


    def stemWords(self):
        """
        Stem words of each text. 
        """ 
        for index, text in enumerate(self.textList):                          
            snowStemmer = SnowballStemmer(language = "english")            
            self.textList[index] = [snowStemmer.stem(token) for token in text]
            
       
    def processTextList(self): 
        """
        Pipeline of text processing
        """       
        self.removeEmojis()
        self.docToLowerCase()   
        self.removeURL()     
        self.removePunctuation()
        self.removeStopWords()
        self.removeApostrophe()
        self.removeSingleCharacters()
        self.removeStopWords()
        # self.lemmatizeWords()
        self.stemWords()
        # self.printTextList("/Results/text")


    def printTextList(self, logfile = None):
        """
        Prints text list.
        """
        if logfile: logfile = open(logfile, "w")
        for text in self.textList:            
            print(''.join(text), file = logfile)
        logfile.close()


    def inDocsTerm(self, word):
        """
        Returns number of documents a word is in.
        """ 
        inDocs = 0       
        for text in self.textList:                    
            for token in text:
                if token == word:
                    inDocs +=1
                    break        
        return inDocs

    def calculatedTFIDF(self):
        """
        Calculatse tf-idf for each word in textList.
        """  
        for text, id in zip(self.textList, self.channelIds):
            TF_IDF = {}             
            counter = Counter(text)
            for token in numpy.unique(text):                
                try:
                    TF = counter[token]/len(text)                
                    IDF = numpy.log(len(self.textList) / self.inDocsTerm(token))
                    TF_IDF[token] = TF * IDF
                except ZeroDivisionError as e:
                    print("Error: ", e)
                    TF_IDF[token] = -1   

            self.TF_IDF[id] = TF_IDF
            # print(id, self.TF_IDF[id])
        with open("post_description.json", "w", encoding = "utf-8") as df:
            df.write(json.dumps(self.TF_IDF))
