#!/usr/bin/env python
# coding: utf-8

# TO DEBUG:
# 	duplicate values, some with different sums in DT song collection
#     
#     NO MORE! because no composers

# In[1]:


import pandas as pd
import numpy as np
import csv


# In[2]:


filename = 'dtFullSongs.csv'
df = pd.read_csv(filename, header = 0, delimiter= ',', index_col = False)
df = df.drop(['#'], axis = 1)


# In[3]:


df.head()


# In[4]:


df = df.rename(index =str, columns = {'Song Code' : 'song_code', 
                                      'Song Title' : 'song_title', 
                                      #'TUCOMP' : 'composer', 
                                      'MechCollectShare' : 'mech_share', 
                                      #'Unnamed: 5' : 'date_created',
                                      'TUDTCREATED' : 'date_created',
                                      'SumIncome' : 'sum_income'})


# In[5]:


df.head()


# DROPPIN DUPS 

# In[6]:


## Count duplicates of a Song Code ## THIS IS VERY IMPORTANT TO KNOW!!! :) 
# 19
df.duplicated(['song_code', 'song_title', 'mech_share']).sum()


# In[7]:


df.duplicated(['song_code']).sum()


# In[8]:


# all duplicated songs that have different sum incomes
df[df.duplicated(['song_code'], keep=False)]


# In[9]:


df = df.drop_duplicates(['song_code', 'song_title','mech_share', 'sum_income'])
df.duplicated(['song_code', 'song_title','mech_share', 'sum_income']).sum()


# In[10]:


#check the one thats kept
#df.iloc[80, 0:]


# In[11]:


## duplicate songs that don't match on sum_income = 4
# for these maybe i can add their sums together, I should do this before computing earnings tho
#df.duplicated(['Song Code', 'Song Title', 'MechCollectShare']).sum()


# In[12]:


# all duplicated songs that have different sum incomes
# df[df.duplicated(['Song Code'], keep=False)]


# In[13]:


#df.isnull().sum()


# CREATE NEW EARNINGS COLUMN

# In[14]:


# calc actual earnings
df['total_song_earnings'] = ((df['sum_income'] * 100) / df['mech_share'])
df = df.sort_values(by =['total_song_earnings'], ascending = False)


# In[15]:


df['song_title'] = df['song_title'].str.strip().str.upper()
#df['composer'] = df['composer'].str.strip().str.upper()

df.head()


# In[16]:


df.to_csv('full_songs.csv')


# In[17]:


#df['Total'] = df.groupby(['Song Code', 'Sum Income'])#['Sum Income'].transform('sum')
#df = df.groupby(['Song Code', 'Song Title', 'MechCollectShare']).sum()#['Sum Income'].transform('sum')

#df.groupby(['Fruit','Name']).sum()
#zoo.groupby('animal').mean()[['water_need']] (This returns a DataFrame object.)
#test = df.groupby(['Song Code', 'Song Title']).sum()[['Sum Income']].sort_values(['Sum Income'], ascending = False)


# In[ ]:




