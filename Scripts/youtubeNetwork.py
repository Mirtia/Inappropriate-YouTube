"""
Author : Myrsini Gkolemi
Date : 15/01/2021
Description : This file contains functions that examine the relations between
channels. Those include tags, featured sections e.t.c.
"""

import json
import os
import re

import networkx as nx
import numpy
import pandas
import requests
from apiclient.discovery import build
from googleapiclient.errors import HttpError

import beauSoupMessage

# File to authenticate credentials.

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<PATH>.json"

class youtubeNetwork:

    commonPair = [("subscribesTo", "commonSub"), ("tagsChannel", "commonTag"), \
            ("featuresChannel","commonFeatured"), ("postsVideoOf", "commonVideoPost"), (" ","commonDifferent")]

    def __init__(self, mainFile, postFile, subFile,  apiKey = None, graphFile = None, mode = None):

        self.mainFile = mainFile
        self.postFile = postFile
        self.subFile = subFile
        self.graphFile = graphFile
        self.apiKey = apiKey
        self.mode = mode
        self.youtube = build('youtube', 'v3', developerKey = self.apiKey, cache_discovery=False)
        self.postChannels = []
        self.youtubeGraph = self.initGraphfromFile() if self.graphFile and self.mode=="r" else nx.MultiDiGraph()
        self.commonGraph = nx.Graph()
                  
        
    def generateGraphFile(self, category, path):
        """
        Generate graph of specific category.
        """
        self.setChannels(category)  
        self.setFeaturedChannels(category) 
        self.setSubscriptions(category)        
        self.setTags(category)           
        self.readVideostoChannelFromFile(path, category) 
 
    
    def initGraphFromFile(self):
        """
        Initialize graph from pickle file.
        """
        try:
           self.youtubeGraph = nx.read_gpickle(self.graphFile) 
        except FileNotFoundError as e:
            print("Error:" + self.graphFile + "not found.( " + str(e) + ")")            
        
   
    def dumpGraphToFile(self):
        """
        Write graph to pickle file.
        """
        try:
           nx.write_gpickle(self.youtubeGraph, self.graphFile)
        except TypeError as e:
            print("Error:" + type(self.youtubeGraph) + "is not the correct type.( " + str(e) + ")")      
        except FileNotFoundError as e:
            print("Error:" + self.graphFile + "not found.( " + str(e) + ")")            
        
    
    def setFeaturedChannels(self, category):
        """
        Add featuredChannel ids to graph. 
        Set node type as secondary.
        """
        try:
            with open(self.mainFile, mode = "r", encoding = "utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    featuredChannelsList = channel["featuredChannels"]

                    if(type(featuredChannelsList)!= int):  
                        for fchannel in featuredChannelsList:
                            if not self.youtubeGraph.has_node(fchannel):                            
                                self.youtubeGraph.add_node(fchannel, type="secondary", set=category)   
                            self.youtubeGraph.add_edge(channel["id"], fchannel, relation="featuresChannel",  weight=1)
                    
        except FileNotFoundError as e:
            print("Error:" + self.mainFile + "not found.( " + str(e) + ")")   
        except json.JSONDecodeError as e:
            print("Error: Something went wrong with the JSON file." + self.mainFile +".( " + str(e) + ")")           

    
    def setTags(self, category):
        """         
        If the tag corresponds to a different channel, 
        it adds an edge with relation "tagsChannel".
        """        
        self.postChannels.clear()      
        self.readPostFile()
        for channel in self.postChannels:            
            channelPosts = channel["Community Tab"]["posts"]
            for post in channelPosts:
                try:
                    channelTags = post["channelLinks"]                    
                    for tag in channelTags:
                        _id = tag.replace('/channel/','') 
                        key = None 

                        if not self.youtubeGraph.has_node(_id):                            
                            self.youtubeGraph.add_node(_id, type="secondary", set=category)                           
                        
                        if channel["id"] != _id:                   
                            if self.youtubeGraph.has_edge(channel["id"], _id):
                                key = {key for (key,value) in self.youtubeGraph.get_edge_data(channel["id"], _id).items() if value["relation"]=="tagsChannel"} 
                            if key:                                    
                                # print("Channel:", channel["id"], _id, "Previous weight:", self.youtubeGraph[channel["id"]][_id][next(iter(key))]["weight"], category)
                                self.youtubeGraph[channel["id"]][_id][next(iter(key))]["weight"] += 1                            
                                print("Tags: Found edge. Incrementing weight...")                       
                            else:
                                # print("Channel:", channel["id"], _id, "One weight", category)
                                self.youtubeGraph.add_edge(channel["id"], _id, relation="tagsChannel", weight=1) 
                except KeyError as e:
                        print("Error: Post information is unavailable." + channel["id"] +".( " + str(e) + ")") 

    
    def setVideosToChannel(self, category, hpFile=None):
        """
        YoutubeLinks and thumbnailVideo may be used to promote other 
        channels. This function uses Youtube Data API v3 (or page source) 
        to get the channelId from video posted. If it is not of the same id, 
        it adds an edge with relation "postsVideosOf".
        """
        if hpFile:
            with open(hpFile + category + ".json", mode = "w", encoding = "utf-8") as hp:
                for channel in self.postChannels:
                               
                    channelPosts = channel["Community Tab"]["posts"]
                    videosToChannel = []
                    for post in channelPosts:                        
                        try:
                            ytLinks = post["youtubeLinks"]
                            thumbnailVideoId = post["thumbnailVideo"]                           
                            thumbnailChannel = None

                            if thumbnailVideoId:
                                # thumbnailChannel= self.getChannelofVideo(thumbnailVideoId)
                                thumbnailChannel = beauSoupMessage.getChannelId(thumbnailVideoId)
                                if thumbnailChannel and thumbnailChannel not in videosToChannel:
                                    videosToChannel.append(thumbnailChannel)                    
                            
                            for link in ytLinks:
                                videoId = re.sub(r'https://.*/','',link)
                                # channelVideo = self.getChannelofVideo(id)
                                channelVideo = beauSoupMessage.getChannelId(videoId)
                                if channelVideo and channelVideo not in videosToChannel:
                                    videosToChannel.append(channelVideo)

                            for vChannel in videosToChannel:
                                if not self.youtubeGraph.has_node(vChannel):                            
                                    self.youtubeGraph.add_node(vChannel, type="secondary", set=category)   

                                if channel["id"] != vChannel:                                                                       
                                    key = None                    
                                    if self.youtubeGraph.has_edge(channel["id"], vChannel):
                                        try:
                                            key = {key for (key,value) in self.youtubeGraph.get_edge_data(channel["id"], vChannel).items() if value["relation"]=="postsVideoOf"} 
                                        except AttributeError as e: 
                                            print(videosToChannel)                                                        
                                            exit()
                                    if key:      
                                        self.youtubeGraph[channel["id"]][vChannel][next(iter(key))]["weight"] += 1                            
                                        print("setVideosChannel: Found edge. Incrementing weight...")                       
                                    else:
                                        self.youtubeGraph.add_edge(channel["id"], vChannel, relation="postsVideoOf", weight=1)
                                else: 
                                    videosToChannel[:] = (value for value in videosToChannel if value != channel["id"])
                    
                        except KeyError as e:
                            print("Error: Post information is unavailable." + channel["id"] +".( " + str(e) + ")") 
                       
                        except AttributeError as e:
                            print("Error: Attribute error." + channel["id"] +".( " + str(e) + ")")
                            print("Thumbnail video id: " + thumbnailVideoId)
                            exit()

                    hp.write(json.dumps({"id" : channel["id"], "videosToChannel": videosToChannel}))
                    hp.write("\n")
        
   
    def getChannelofVideo(self, videoId):
        """
        Uses YouTube API to get channelId from video.
        """
        request = self.youtube.videos().list(part = 'snippet', id = videoId)
        response = request.execute()        
        return response["items"][0]["snippet"]["channelId"] if response["items"] else None      

        
    def readPostFile(self):
        """
        Reads file with posts from Community Tab.
        Saves the objects to buffer.
        """
        try:
            
            with open(self.postFile, mode = "r", encoding = "utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    self.postChannels.append(channel)
                                        
        except FileNotFoundError as e:
            print("Error:" + self.postFile + "not found.( " + str(e) + ")")   
            exit() 
        except json.JSONDecodeError as e:
            print("Error: Something went wrong with the JSON file." + self.postFile +".( " + str(e) + ")")    
        
    
    def readVideostoChannelFromFile(self, hpFile, category):
        """
        Reads file with posts from Community Tab.
        Saves the objects to buffer.
        """        
        try:
                        
            with open(hpFile, mode = "r", encoding = "utf-8") as hf:
                for jsonObj in hf:
                    channel = json.loads(jsonObj)
                    videosToChannel = channel["videosToChannel"]
                    for vChannel in videosToChannel:
                        if not self.youtubeGraph.has_node(vChannel):                            
                                self.youtubeGraph.add_node(vChannel, type="secondary", set=category)   

                        if channel["id"] != vChannel:                                                                       
                            key = None                    
                            if self.youtubeGraph.has_edge(channel["id"], vChannel):
                                key = {key for (key,value) in self.youtubeGraph.get_edge_data(channel["id"], vChannel).items() if value["relation"]=="postsVideoOf"} 
                            
                            if key:      
                                self.youtubeGraph[channel["id"]][vChannel][next(iter(key))]["weight"] += 1                            
                                print("readVideosToChannelFromFile: Found edge. Incrementing weight...")                       
                            else:
                                self.youtubeGraph.add_edge(channel["id"], vChannel, relation="postsVideoOf", weight=1)
        
        except FileNotFoundError as e:
            print("Error: readVideosToChannelFromFile " + hpFile + " not found.( " + str(e) + ")")  
            exit() 
        except json.JSONDecodeError as e:
            print("Error: Something went wrong with the JSON file." + hpFile +".( " + str(e) + ")")    
            exit() 

  
    def setChannels(self, category):
        """
        Add channel ids to graph. 
        Set node type as main (unique nodes).
        """
        try:
            with open(self.mainFile, mode = "r", encoding = "utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    self.youtubeGraph.add_node(channel["id"], type="main", set=category)
        except FileNotFoundError as e:
            print("Error:" + self.mainFile + "not found.( " + str(e) + ")")   
        except json.JSONDecodeError as e:
            print("Error: Something went wrong with the JSON file." + self.mainFile +".( " + str(e) + ")")  
                         
      
    def setSubscriptions(self, category):        
        """
        Adds subscription ids to graph.
        Adds edge with type "subscribesTo".
        """
        try:
            with open(self.subFile, mode = "r", encoding = "utf-8") as sf:
                for jsonObj in sf:
                    channel = json.loads(jsonObj)
                    subscriptionList =  channel["subscriptionList"] 
                    for sub in subscriptionList:
                        if not self.youtubeGraph.has_node(sub):                                                   
                            self.youtubeGraph.add_node(sub, type="secondary", set=category)   
                        self.youtubeGraph.add_edge(channel["id"], sub, relation="subscribesTo", weight=1)

        except FileNotFoundError as e:
            print("Error:" + self.mainFile + "not found.( " + str(e) + ")")   
        except json.JSONDecodeError as e:
            print("Error: Something went wrong with the JSON file." + self.mainFile +".( " + str(e) + ")")    

        
    def findNodes(self, graph, attribute, value):
        """
        Finds nodes with specific data attribute and value.
        """
        try:            
            foundNodes = [n for n,v in graph.nodes(data=attribute) if v == value]  
            return foundNodes
        except KeyError as e:
            print("Error: " + attribute + "key does not exist.( " + str(e) + ")") 

        
    def findEdges(self, graph, attribute, value):
        """
        Finds edges with specific data attribute and value.
        """
        try:
            foundEdges = [(u, v, t) for u,v,t in graph.edges(data=attribute) if t == value]  
            return foundEdges
        except KeyError as e:
            print("Error: " + attribute + "key does not exist.( " + str(e) + ")") 

        
    def isIsolatedFromMain(self, graph, nodeV):
        """
        Finds isolated main nodes.
        """
        try:
            neighbors = graph.neighbors(nodeV)
            for n in neighbors:            
                if graph.nodes[n]["type"] == "main":
                    return False
            return True
        except KeyError as e:
            print("Error: Key " + str(e) + " does not exist.( " + str(graph.nodes[n]) + str(n) + ")") 
            exit()

        
    def getIsolatedNumber(self, graph):
        """
        Finds # of isolated main nodes.
        """
        isolatedNodes = [(v,t) for v,t in graph.nodes(data="type") if (t == "main" and self.isIsolatedFromMain(graph, v))]
        return len(isolatedNodes)

    
    
    def getMeanOutDegree(self, graph):
        """
        Get mean out-degree of graph.  
        """
        degrees = []
        for node in graph.nodes():
            degrees.append(graph.out_degree(node))
        try:
            return sum(degrees)/len(degrees)
        except ZeroDivisionError as e:
            print("Error: Zero denominator. ", e)
          

    def getMeanInDegree(self, graph):
        """
        Get mean out-degree of graph.
        """
        degrees = []
        for node in graph.nodes():
            degrees.append(graph.in_degree(node))
        try:
            return sum(degrees)/len(degrees)
        except ZeroDivisionError as e:
            print("Error: Zero denominator. ", e)
  

    def degreesToCsv(self, graph, category = None, filterFlag = False):
        """
        Append columns in-degree and out-degree to csv.
        """
        inDegree = []
        outDegree = []
        ids = []  
        if filterFlag:
            graphNodes = self.findNodes(graph, "type", "main")
        else:
            graphNodes = graph.nodes() 

        for node in graphNodes:          
            inDegree.append(graph.in_degree(node))
            outDegree.append(graph.out_degree(node))
            ids.append(node)

        data = pandas.DataFrame({"id":ids, "in-degree":inDegree, "out-degree":outDegree})
        if category:
            data.to_csv(category + "_degrees.csv", index=False) 
        else:            
            data.to_csv("degrees.csv",index=False)
    
   
    def getDensity(self, graph):
        """
        Returns density of the graph.
        """
        numNodes = graph.number_of_nodes()
        potentialConn = numNodes * (numNodes - 1) / 2
        actualConn = graph.number_of_edges()
        return actualConn / potentialConn

     
    def printYoutubeGraph(self):   
        """
        Prints graph with its type ( main or secondary) and number of nodes.
        """
        print("Graph Size: "+ "(Number of nodes = "+ str(self.youtubeGraph.number_of_nodes()) + ")\n" +
        str(self.youtubeGraph.nodes(data="type")) + "(Number of nodes = "+ str(self.youtubeGraph.number_of_nodes()) + ")\n")

    
    def printMainMetrics(self, graph, logfile):
        """
        Prints some basic statistics about the graph.
        """
        logfile = open(logfile, "a")
        print("-------------Main Metrics-------------", file = logfile)
        print("Number of nodes:",graph.number_of_nodes(), file = logfile)
        print("Number of edges:", graph.number_of_edges(), file = logfile)
        print("Main nodes:", len(self.findNodes(graph, "type", "main")), file = logfile)
        print("Secondary Nodes:", len(self.findNodes(graph, "type", "secondary")), file = logfile)
        print("tagsChannel:", len(self.findEdges(graph, "relation", "tagsChannel")), file = logfile)
        print("postsVideoOf:", len(self.findEdges(graph, "relation", "postsVideoOf")), file = logfile)
        print("featuresChannel:", len(self.findEdges(graph, "relation", "featuresChannel")), file = logfile)
        print("subscribesTo:", len(self.findEdges(graph, "relation", "subscribesTo")), file = logfile)
        print("Isolated nodes ('secondary' nodes are excluded):", self.getIsolatedNumber(graph), file = logfile)
        print("Mean in-degree:", self.getMeanInDegree(graph) ,"\nMean out-degree:", self.getMeanOutDegree(graph), file = logfile)
        print("Network Density:", self.getDensity(graph), file = logfile)
        print("--------------------------------", file = logfile)
        logfile.close()

    
    def printCommonMetrics(self, graph, logfile):
        """
        Prints some basic statistics about the commonGraph.
        """
        logfile = open(logfile, "a")
        print("------------- Common Metrics-------------", file = logfile)       
        print("Number of nodes:",graph.number_of_nodes(), file = logfile)
        print("Number of edges:", graph.number_of_edges(), file = logfile)
        print("commonTag: ", len(self.findEdges(graph, "common", "commonTag")), file = logfile)
        print("commonVideoPost: ", len(self.findEdges(graph, "common", "commonVideoPost")), file = logfile)
        print("commonFeatured: ", len(self.findEdges(graph, "common", "commonFeatured")), file = logfile)
        print("commonSub: ", len(self.findEdges(graph, "common", "commonSub")), file = logfile)
        print("Isolated nodes: ", len(list(nx.isolates(graph))), file = logfile)
       
        print("--------------------------------", file = logfile)
        logfile.close()
      
    
    def findRelationsGroup(self, graph):
        """
        Checks if any main node from each set is connected to another category. 
        Filters main nodes that have non-zero out-edges.
        Prints list that holds the number of relationships between the categories.
        Prints numpy array that consists of each category and the relations with other
        nodes.
        """
        categories = [("suitable", 0), ("disturbing", 1), ("popular", 2), ("random",3)]
        relationships = [("subscribesTo",  0), ("tagsChannel", 1), ("featuresChannel", 2), ("postsVideoOf", 3)]
        connections = []    
        relations = []  
        outNodes = []
        for i in range(0,4):
            relations.append(numpy.zeros((4, 4), dtype=numpy.int32))
        for c in categories:
            nodes = self.filterOutNodes("main", graph, c[0])
            print("Length: ", len(nodes))
            outNodes.append(nodes)            
 
        for category, nodeList in zip(categories, outNodes):
            cVector = [0]*4           
            otherCategories = [(x, y) for (x, y) in categories if x != category[0]]        
            try:
                for node in nodeList:                
                    outEdges = graph.out_edges(node[0])               
                    neighbors = [y for x,y in outEdges]   
                    neighborData = [graph.get_edge_data(x,y) for x,y in outEdges]                    
                    for n, data in zip(neighbors, neighborData):                                                 
                        node_ =  graph.nodes[n]                                             
                        nodeCategory = node_["set"] 

                        if node_["type"] == "main":
                            if category[0] != nodeCategory:                                                                                                                                                  
                                index = next(c[1] for c in otherCategories if c[0] == nodeCategory) 
                                cVector[index] += data[0]["weight"] 
                                indexArray = next(r[1] for r in relationships if r[0] == data[0]["relation"])                                                                                     
                                relations[category[1]][indexArray][index] +=1                                
                                           
            except KeyError as e:
                print("Error: " + str(node) + "key does not exist.( " + str(e) + ")")
            connections.append(cVector)
        print("Relations with other groups")
        print("-----------", " | s   d   r   p |")
        print("Suitable  : ", connections[0])
        print("Disturbing: ", connections[1])
        print("Popular   : ", connections[2]) 
        print("Random    : ", connections[3])
        print("Relations with other groups (details)")
        print(" | s   d   r   p |")        
        for r in relations:
            print(r)         


    def printEgoNetworkMetrics(self, graph, logfile):
        """
        Prints ego network statistics.
        """
        logfile = open(logfile, "a")
        print("------------- EgoNetwork Metrics-------------", file = logfile)
        weakCC = self.getWeaklyConnectedComponents(graph)
        print("Number of weak components:", weakCC[1], file = logfile)          
        print("---------------------------------------------", file = logfile)
        logfile.close()


    def getRelationStats(self, graph, nodes, restCategories):        
        raise NotImplementedError


    def getWeaklyConnectedComponents(self, graph):        
        return (nx.weakly_connected_components(graph), nx.number_weakly_connected_components(graph))


    def getLocalCentrality(self, node, graph):
        return nx.local_reaching_centrality(graph, node)


    def filterInNodes(self, attribute, graph, category = None):   
        """
        Returns specific category nodes with in-degree > 0.
        """
        try:
            if category:
                return [(x,y) for x,y in graph.nodes(data=True) if y["type"] == attribute and y["set"] == category and graph.in_degree(x) > 0]
            else:
                return [(x,y) for x,y in graph.nodes(data=True) if y["type"] == attribute and graph.in_degree(x) > 0]
        except KeyError as e:
            print("Error: This should never happen. Problem with loaded file. ",e)
            exit()


    def filterOutNodes(self, attribute, graph, category = None): 
        """
        Returns specific category nodes with out-degree > 0.
        """  
        try:
            if category:
                return [(x,y) for x,y in graph.nodes(data=True) if y["type"] == attribute and y["set"] == category and graph.out_degree(x) > 0]
            else:
                return [(x,y) for x,y in graph.nodes(data=True) if y["type"] == attribute and graph.out_degree(x) > 0]
        except KeyError as e:
            print("Error: This should never happen. Problem with loaded file. ",e)
            exit()

           
    def composeFullGraph(self, objects, categories, hpFile):
        """
        Composes a graph with all categories.
        """        
        funcCalls = ["setChannels", "setFeaturedChannels", "setSubscriptions", \
            "setTags", "readVideostoChannelFromFile"]
        for f in funcCalls:            
            for o,c in zip(objects, categories):              
                self.mainFile = o.mainFile
                self.postFile = o.postFile
                self.subFile = o.subFile                   
                method = getattr(self, f)                
                if f == "readVideostoChannelFromFile":
                    method(hpFile + c + ".json", c)
                else:
                    method(c)
                

    def getStronglyConnectedComponents(self, graph):        
        maxComp = max(nx.strongly_connected_components_recursive(graph), key=len)
        return maxComp
       

    def findSecondLevelRelations(self):
        """
        List of secondary nodes
        Checks if there is a secondary node that has two ingoing edges of main nodes.
        If so, it adds an edge:
        1. commonSub
        2. commonTag
        3. commonChannelFromVideo
        4. commonFeaturedChannel
        5. commonDifferent
        The edges are not directed. We add the edges to the commonGraph.
        """
        self.commonGraph = nx.MultiGraph()
        secondaryNodes = self.filterKeyNodes("type", "secondary", self.youtubeGraph)
        
        for node_ in secondaryNodes:
            inNodes = list(self.youtubeGraph.in_edges(node_, data="relation"))
            
            for n in inNodes:
                self.commonGraph.add_node(n[0])

            sortedEdges = sorted(inNodes, key = lambda x: x[2])  
                       
            iterEdgeList =  iter(sortedEdges)
                        
            currentIter = "dummyIter"
            while currentIter:                 
                nodesCommon = []       
                currentIter = next(iterEdgeList, None)                
                if currentIter:
                    nextIter = next(iterEdgeList, None)
                    if nextIter:
                        while nextIter and currentIter[2] == nextIter[2]: 
                            nodesCommon.append(nextIter) 
                            nextIter = next(iterEdgeList, None)                       
                        if nodesCommon:
                            for n in nodesCommon:                           
                                self.commonGraph.add_edge(currentIter[1], n[1], common=self.returnCommon(currentIter[2]))
            for u in inNodes:
                if self.commonGraph.degree(u) == 0:                                
                    for v in inNodes:
                        if v!=u:
                            self.commonGraph.add_edge(u, v, common="commonDifferent")
    
            
    def filterKeyNodes(self, key, attribute, graph):
        try:          
            return [x for x,y in graph.nodes(data=key) if y == attribute]
        except KeyError as e:
            print("Error: This should never happen. Problem with loaded file. " + e)
            exit()
        
   
    def getAverageClustering(self, graph):
        try:
            return nx.average_clustering(graph, weight="weight", count_zeros=False)
        except ZeroDivisionError as e:
            print("Error: Something went wrong with calculating average clustering. " + e)


    def getDiameter(self, graph):  
        return nx.diameter(graph)
        
                    
    def returnCommon(self, common): 
        return [pair[1] for pair in self.commonPair if pair[0] == common][0]
