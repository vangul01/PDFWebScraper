READ ME

Hey! So this is the web scraper I was working on, located in fresh_script.py but I would use the jupyter notebook to run it. I found some bugs during my last week and didn't get around to fixing them but they're due to some missing regex formatting cases. The year 2019 is good though and I included what the output should look like in this folder. I found formatting issues for 2018 though, and none of the Saturdays in 2010 are valid for some reason... 

Anyway, the billboard song index URLs are sometimes invalid even if it falls on a Saturday, sometimes there isn't a new song index out every week so I have that in the try except block. Everything else should have enough notes, but basically the flow is:

1. choose whether you want all saturdays for a certain year (per_year = True) or a block of years (per_year = False)
	I recommend per_year = True since there are apparently bugs and even choosing 1 (for 2018-2019) is too much data for the server apparently...not sure but didnt want to risk it

2. Based on your decision above, either input a block of years (x_years) or a specific year (year)

3. allsaturdays will populate a list with all the saturdays for year(s) requested. For the current year, all saturdays up to the most recent will be collected

4. these saturdays are inserted in the song index URL and the URL's are then scraped with convert_pdf, formatted with clean_my_string and then added to a result string. All invalid links will be printed out so that you can verify that.

5. Finally, the string is converted into a dataframe which does some other modifications and gives you a csv as an output.

Thats it! In the end you'll have clean, well formatted 3rd party data in a csv that you can then merge with the songs from the downtown catalog.

For the downtown songs I included the script I used to cleanup/modify the results from DataGrip and included the largest csv I was able to get from the data cause it takes like 1 hour to run the query on datagrip and then another hour to output a csv. Hopefully this helps!

Good luck and enjoy your internship! :)