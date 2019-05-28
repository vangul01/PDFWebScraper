READ ME

This is a PDF web scraper that scrapes Song Index Billboard information from links in this format: https://www.billboard.com/files/index/songindex_01_19_2019.pdf

It is meant to collect alternative data to supplement company song data in order to figure out growth and decay rates of how long certain songs are on the billboard charts and what ranks they hold throughout the weeks. The billboard song index URLs are sometimes invalid even if it falls on a Saturday, sometimes there isn't a new song index out every week. The basic flow of fresh_script is:

1. choose whether you want all saturdays for a certain year (per_year = True) or a block of years (per_year = False)
	I recommend per_year = True since there are apparently bugs and even choosing 1 (for 2018-2019) is too much data for the server apparently...not sure but didnt want to risk it

2. Based on your decision above, either input a block of years (x_years) or a specific year (year)

3. allsaturdays will populate a list with all the saturdays for year(s) requested. For the current year, all saturdays up to the most recent will be collected

4. these saturdays are inserted in the song index URL and the URL's are then scraped with convert_pdf, formatted with clean_my_string and then added to a result string. All invalid links will be printed out so that you can verify that.

5. Finally, the string is converted into a dataframe which does some other modifications and gives you a csv as an output.

Thats it! In the end you'll have clean, well formatted 3rd party data in a csv that you can then merge with the songs from the downtown catalog.

For the downtown songs I included the script I used to cleanup/modify the results from the DataGrip IDE and included the largest csv I was able to get from the data pulled.
