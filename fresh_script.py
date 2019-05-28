#!/usr/bin/env python
# coding: utf-8

# # My Song Index PDF Scraper/Cleaner/Dataframe creator!

# ~ This code lets you input a number representing the number of years you want the weekly billboard song index pdfs for, scrapes the PDF from the song indec URL, cleans and formats the pdf into a string and puts the string containing x years worth of billboard song indexes into a pandas dataframe, exporting it as a csv full of gold ~
# 

# TO DO:
# 1.  Datetime error!!! Caused by missing a regex pattern in Aug 18, 2018, where the \n after -D- gets deleted and the next song is placed on same row as previous song
#     This is the song that gets moved to previous row: \n\n-D-  \n\nDAME TU COSITA  
#     To fix: use regex sub to deal with this case and make sure output ends up like 
#     \nDAME TU COSITA  
# 2.  get rid of weird column 
#     To do this: in df form search for ;) and delete all except for end [0-9]*[A-Z]*
#     #001HUCLA

# In[66]:


import io
import os
import re
import csv 
import datetime
import pandas as pd
from datetime import datetime as dtime

import requests
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


# # Scrape and format PDF text

# In[67]:


#FORMAT PDF STRING FOR CSV
def clean_my_string(mystring):
    val = mystring
    val = val.replace(',', ' --')
    #separate first title from data
    #Case1: JAN\n\n2019 SONG INDEX\n\n19\n\n
    #Case2: FEB\n23\n\n 2019 SONG INDEX\n\n
    val = re.sub(r'(\n\n[0-9]+)(\n\n)', r' \1,|', val)
    val = re.sub(r'(SONG INDEX)(\n\n)', r' \1,|', val)    
    #separate titles from chart placements
    val = re.sub(r'  ([0-9]+)(\n)', r'  \1,|', val)
    #weird issue: ), HL, H100 100\nAMANECE #100AMANECE,(Not Listed) LT  12
    val = re.sub(r'(H100 [0-9]+)(\n)', r'\1,|', val)
    #takes out alphabetical headers
    val = re.sub(r'([\n]*-[A-Z]-  )', r'\n', val)
    #takes out all new lines
    val = re.sub(r'\n', r'', val)
    #separate title from publishers
    val  = re.sub(r'  \(',r',(', val)
    #adds new line right before song title
    val = re.sub(r'(,\|)', r'\n', val)
    #TO SEPARATE THE SHEET MUSIC CODE FROM BILLBOARD AND PUBLISHERS
    val = re.sub(r'\) -- ([A-Z]+[/]*[A-Z]*) -- ', r'),\1,', val)
    #TO SEPARATE BILLBOARDS FROM WHATEVERS PRIOR, ',,' if the prior doesnt exist
    val = re.sub(r'\) ([A-Z0-9]+[ ]+[0-9]+)', r'),,\1', val)
    #reformat date string (first line)
    #Case1: JAN\n\n2019 SONG INDEX\n\n19\n\n
    #Case2: FEB\n23\n\n 2019 SONG INDEX\n\n
    val = re.sub(r'([A-Z]{3})[ \n]*([0-9]{4}) [A-Z ]+[ \n]*([0-9]{1,2})', r'\1,\3,\2', val)
    val = re.sub(r'([A-Z]{3})[ \n]*([0-9]{1,2})[ \n]*([0-9]{4})[A-Z ]+', r'\1,\2,\3', val)
    #search for datestring in whole pdf text and match it
    match = re.search('([A-Z]{3},[0-9]{1,2},[0-9]{4})', val)
    #save date in variable
    getdate = match.group(1) if match else None
    val = re.sub(r'([A-Z]{3},[0-9]{1,2},[0-9]{4})\n', r'', val)
    #make datestring for new column
    datestr = ',' + getdate + '\n'
    val = val.replace('\n', datestr)
    #make new line after weird publisher line/key
    val = re.sub(r'ELTTI\x0c', r'\n', val)
    #fix weird incs. -- Inc. --
    val = re.sub(r'-- Inc. --',r' Inc. --', val)
    #change -- to ;
    #val = val.replace('--',';')
    return val


# In[68]:


#source = https://gist.github.com/terencezl/61fe3f28c44a763dd1e9f060b8ff6f2e
## SCRAPE TEXT FROM DOWNLOADED PDF 
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

def convert_pdf(path, format='text', codec='utf-8', password=''):
    r = requests.get(path)
    f = io.BytesIO(r.content)
    
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = io.BytesIO(f.getvalue())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text


# # Get ya list of Saturdays!

# In[69]:


#return all saturdays of a given year in ascending order (jan --> dec)
def allsaturdays(year):
    my_year = dtime.now().year
    if (year == my_year): 
        mydates = 'https://billboard.com/files/index/songindex' + pd.date_range(start=str(year), end= dtime.today(), 
                             freq='W-SAT').strftime('_%m_%d_%Y').astype(str) + '.pdf'
        return mydates
    else:
        mydates = 'https://billboard.com/files/index/songindex' + pd.date_range(start=str(year), end=str(year+1), 
            freq='W-SAT').strftime('_%m_%d_%Y').astype(str) + '.pdf'
        return mydates


# # Modify Result string using Pandas

# In[70]:


def df_my_string(mystring,myyear):
    
    data = result
    dt = pd.DataFrame([x.split(',') for x in data.split('\n')])
    dt.head()
    dt = dt.rename(columns={0: 'title', 1: 'publishers', 2: 'sheet_music', 3: 'chart', 4: 'month', 5: 'day', 6: 'year'})
    dt = dt.dropna(subset=['chart'])

    months = {
        "JAN" : '01',
        "FEB" : '02',
        "MAR" : '03',
        "APR" : '04',
        "MAY" : '05',
        "JUN" : '06',
        "JUL" : '07',
        "AUG" : '08',
        "SEP" : '09',
        "OCT" : '10',
        "NOV" : '11',
        "DEC" : '12'
    }


    #maybe we dont have to fill if its not in date format?
    #turn month to numerical
    dt.month = dt.month.map(months)
    #turn day to int and pad with 0
    dt.day = pd.DataFrame(dt.day, dtype='int')
    dt.day = dt.day.astype(str)
    dt.day = dt.day.str.zfill(2)
    #turn year to int to string
    dt.year = pd.DataFrame(dt.year, dtype='int')
    dt.year = dt.year.astype(str)
    #make new date column, turn to datetime for convenient filtering
    dt['date'] = dt.month + "-" + dt.day + "-" + dt.year
    dt['date'] = pd.to_datetime(dt['date'])  
    #drop separate dates
    #dt = dt.drop(['month', 'day', 'year'], axis = 1)
    #move charts to the end
    dt = dt[['title','publishers','sheet_music','date','month', 'day', 'year','chart']]
    #remove -- from titles
    dt.title = dt.title.str.replace(' --','')

    #csv!
    dt.to_csv('{}_billboard_data.csv'.format(myyear))  
    


# # Main

# In[73]:


#53 pdfs per year * 369 rows per pdf  = 19,557 rows * x years = ? 
#For 10 years of historical billboard song indexes expect 195,570 rows of data
##ACTUALS for 2019! (as of 5/7/019)
#invalid link:  https://billboard.com/files/index/songindex_01_12_2019.pdf
#invalid link:  https://billboard.com/files/index/songindex_02_16_2019.pdf
#invalid link:  https://billboard.com/files/index/songindex_03_30_2019.pdf

##Issues: some are counted as not working even though they are
#This issue is with the cleaning, some cases not caught

####~*ma main*~####
if __name__ == '__main__':

    #boolean value for collecting data per year or per x years
    #yearly = true means collecting data per year, cleaning and exporting to csv
    per_year = True 
    
    #df_my_string(mystring):
    #all saturdays for the past x years 
    x_years = 0
    year = 2018
    saturdays = []
   
    if (per_year == False):
        current_year = dtime.now().year
        start_year = current_year - x_years
        for i in range(x_years + 1):
            saturdays.extend(allsaturdays(start_year + i).tolist())
    else:
        saturdays.extend(allsaturdays(year).tolist())
        
        
    result = ''
    for pdf_path in saturdays:#(all the URLs in the saturdays list):
        #handles weeks that dont have a song index
        try:
            #scrape pdf and put into string
            pdfstring = convert_pdf(pdf_path)
            #preprocess string
            cleanpdfstring = clean_my_string(pdfstring)
            #add that clean string to a result string!
            result += cleanpdfstring
        except:
            print('invalid link: ', pdf_path)
            pass

    #change this if block of years
    df_my_string(result,year)


# In[74]:


result


# In[75]:



data = result
dt = pd.DataFrame([x.split(',') for x in data.split('\n')])
dt.head()
dt = dt.rename(columns={0: 'title', 1: 'publishers', 2: 'sheet_music', 3: 'chart', 4: 'month', 5: 'day', 6: 'year'})
dt = dt.dropna(subset=['chart'])

months = {
    "JAN" : '01',
    "FEB" : '02',
    "MAR" : '03',
    "APR" : '04',
    "MAY" : '05',
    "JUN" : '06',
    "JUL" : '07',
    "AUG" : '08',
    "SEP" : '09',
    "OCT" : '10',
    "NOV" : '11',
    "DEC" : '12'
}


#maybe we dont have to fill if its not in date format?
#turn month to numerical
dt.month = dt.month.map(months)
#turn day to int and pad with 0
dt.day = pd.DataFrame(dt.day, dtype='int')
dt.day = dt.day.astype(str)
dt.day = dt.day.str.zfill(2)
#turn year to int to string
dt.year = pd.DataFrame(dt.year, dtype='int')
dt.year = dt.year.astype(str)
#make new date column, turn to datetime for convenient filtering
dt['date'] = dt.month + "-" + dt.day + "-" + dt.year
dt['date'] = pd.to_datetime(dt['date'])  
#drop separate dates
#dt = dt.drop(['month', 'day', 'year'], axis = 1)
#move charts to the end
dt = dt[['title','publishers','sheet_music','date','month', 'day', 'year','chart']]
#remove -- from titles
dt.title = dt.title.str.replace(' --','')

#csv!
dt.to_csv('{}_billboard_data.csv'.format(2018))  


# In[ ]:


dt.dtypes


# In[72]:


#IOPub data rate exceeded.
#The notebook server will temporarily stop sending output
#to the client in order to avoid crashing it.
#To change this limit, set the config variable
#`--NotebookApp.iopub_data_rate_limit`. jupyter notebook --NotebookApp.iopub_data_rate_limit=1.0e10

#Current values:
#NotebookApp.iopub_data_rate_limit=1000000.0 (bytes/sec)
#NotebookApp.rate_limit_window=3.0 (secs)

#print(result)


# Edits for DF:
# 
# WEIRD VALUES!!!!
# 
# 735	X	(Sony/ATV Sounds LLC -- SESAC/La Industria Music -- ASCAP/Universal Musica Unica Publish-ing -- BMI/Universal Music Columbia S.A.S. -- SAYCO/Musical All Star -- BUMA/WB Music Corp. -- ASCAP/BMG Sapphire Songs -- BMI/These Are Pulse Songs -- BMI)	AMP/HL	2019-01-19	1	19	2019	LT   7
# 
# 736	;)001 toHdraob lliB ehT( 001HUCLA	(Turtle Ate My Homeworks -- BMI/KMR II GT Publishing Limited -- BMI/Songs Of Kobalt Music Publishing America  Inc. -- BMI/you:made publishing -- KODA/These Are Pulse Songs -- BMI/Rex Kudo Publishing Designee -- ASCAP/For You Smokes -- ASCAP/Brought To You By Heavy Duty -- ASCAP)		2019-01-19	1	19	2019	DES  36
# 
# 
# Supposed to be...
# 
# UCLA (Turtle Ate My Homeworks, BMI/KMR II GT Publishing Limited, BMI/Songs Of Kobalt Music Publishing America, Inc., BMI/you:made publishing, KODA/These Are Pulse Songs, BMI/ Rex Kudo Publishing Designee, ASCAP/For You Smokes, ASCAP/B
# 
# This is ok I think… Its an issue with the scraper
# I could try to regex this out better

# In[ ]:




