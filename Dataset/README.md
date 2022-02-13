# Datasets

This file marks down the datasets collected.

## Videos

- 	Removed videos with error 'simpleText':
	-	simpleTextDisturbingVideos.json
	-	simpleTextSuitableVideos.json
	
-	Suitable and disturbing videos
	-	suitableVideos.json
	-	disturbingVideos.json

## Channels

-	Featured:
	
	-	FTU_suitable.json
	-	FTU_disturbing.json
	
	Features:
	> id, videoCount, hiddenSubscriberCount, viewCount,
	> description, descriptionCharCount, keywords, keywordsCount,
	> topicCategories, topicCount, featuredChannels(deprecated),
	> featuredChannelsCount(deprecated), country, madeForKids,
	> publishedAt, videoIds, disturbingCount, suitableCount,
	> suitableRation, madeForKidsRatio, madeForKidsVideosCount, madeForKidsDisturbing,
	> simpleText, subscriptionCount, subscriptionList, postCount

- 	Status:

	-	suitableChannelsSimpleText.json
	-	disturbingChannelsSimpleText.json	
	-	videosChannelsDisturbingSimpleText.json
	-	videosChannelsSuitableSimpleText.json
	
- 	Links(About Tab):

	 -	suitable_links.json
	 -	disturbing_links.json
	
- 	Subscriptions:
	
	-	suitableSubscriptions.json
	-	disturbingSubscriptions.json

- 	Posts:	
	-	suitable_posts.json
	-	disturbing_posts.json
	
## .csv

-	Suitable-Disturbing.csv: all columns of features

-	Other .csv
	
	- Channel status (%, #)
		-	statusChannelSuitable.csv
		-	statusChannelDisturbing.csv		
	- Videos status (%, #)
		-	statusVideosSuitable.csv
		-	statusVideosDisturbing.csv
	- Keywords (columns)		
		-	keywords.csv	
	- emotions
		-	emotions.csv
		
			
## Other :

-	logfile (stats gnuplot)

- 	R non parametric tests results:

-	outfile.txt(Suitable-Disturbing Kolmogorov-Smirnov test)

- 	Columns

	-	/FTU_suitable
	-	/FTU_disturbing
	
	*(files: country, descriptionCharCount, keywordsCount, postCount, subscriberCount,*
	*subscriptionCount, topicCount, videoCount, viewCount)*

