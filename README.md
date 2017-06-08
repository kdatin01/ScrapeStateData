# ScrapeStateData
What(is this?): This script's intent is to scrape data on all states tax system.  Currently, it scrapes exemption/tax credit amounts from an excel file which contains data for all 50 US states.  It also scrapes data from individual state income tax form and instruction PDF documents.  Currently it is oinly verified to work for 4 states (Alabama, Arkansas, California, Delaware), but as the script develops more and more state data should be successfully scraped automatically. 

Why(am I doing this?): I've actually built bits and pieces of this throughout the years to answer the age old question: Where should I live?  As a software engineer, I can live pretty much anywhere in the US and have a job, so the deciding factors for me when it comes to deciding where to settle down are cost and availability of delicious foods.  This scraper is intended to fully map out how much a person would pay in taxes to live in a certain state(and eventually the tax amount for a certain town in a certain state).  Maybe one day I will include a yelp module so that I can determine the absolute perfect location to live, someplace with relatively low taxes and delicious food nearby.

How: Python!  specifically python 2.7.

What's Next:  
1.  Add comparison of scraped pdf data to scraped excel data for verification purposes
2.  Adding in additional functionality to scrape all state PDFs
3.  Conquer county, municipal, town, burrow, ect taxes that each state may or may not have.
4.  Add Matlab plotting tools for fun visualizations.

