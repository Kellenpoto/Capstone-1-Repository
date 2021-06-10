# Passing VS Running Success in the NLF

## The Face of the NFL is Changing
In recent years with the emergence of several young and talented quarterbacks, NFL pundits and coaches have advanced the claim that "This is a passing league". With the success of teams like Green Bay, Tampa Bay, and Kansas City, there is plenty of annecdotal evidence to support this. From a fan standpoint, the modern day high-flying NFL is absolutely captivating and more volitile than ever, but is there statistical evidence to support this league wide shift in offensive philsophy?

<div align="center">
<img width="1200" src="https://media.pff.com/2020/07/quarterback-rankings.png?w=956&h=538">
</div>

## Describing the Data
I gathered data from [NFLSavant.com](http://nflsavant.com/about.php) where open source NFL play by play data is stored in CSV format. The raw data contains about 46,000 rows with over 40 fields of descriptive data. Some significant features includes Yards, Yards Togo, Formation, Play Type, Game ID, and Team Name. Although there are many more, this analysis will focus mostly on using those features. I added a column to the data indicating if the play was a success or not based on [existing metrics](https://www.sharpfootballstats.com/basics-and-faq.html) for success. To summarize, a play is a success on first down if it gains 40% of yards to go for the first down. On second that increases to 60%. On third and fourth down the only way to succeed is to get the first down or touchdown. I cleaned up a few empty columns and adjusted the rush direction column to account for QB scramble plays as well.

## Exploring the Data
I began exploring the data by creating a few functions to help plot one stat against another for each team. For the sake of figuring out wether it is better to pass or run, the traditional method for determining success would compare yards against run attempts and pass attempts as seen below.
<div align="right">
  <img src="images/PassesVSYardsPerTeam.png">
  <img src="images/RushesVSYardsPerTeam.png">
</div>
Following this comparison, I broke down yards per run and pass further to explore the rate of success of per down. The example below demonstrates how different the two success statistics are by sampling the NFL as a whole. The graph in the center contextualizes the other two by giving an idea of sample size for each down.
<div align='center'>
  <img src='images/Three Graph Summary.png'>
</div>
Another way to vizualize the success of run and pass plays is to at the beta distributions for a few teams.  

**Top Four Offenses by Total Yards:**

<p float='center'>
<img width="400" src='images/RushPassDistributions/RushPassDistributionKC.png'><img width="400" src='images/RushPassDistributions/RushPassDistributionBUF.png'><img width="400" src='images/RushPassDistributions/RushPassDistributionTEN.png'><img width="400" src='images/RushPassDistributions/RushPassDistributionMIN.png'>
</p>
The top four offenses differ in offensive philosophy pretty significantly. The two teams on top utilize pass heavy offenses more common to todays game, while the lower two rely on workhorse runningbacks to propell their offenses.
