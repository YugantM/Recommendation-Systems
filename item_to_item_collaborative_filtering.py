'''time complexity of this code is not optimized'''
''' optimized code will be commited soon'''
''' dependencies '''
import pandas as pd
import numpy as np
import math
from scipy import spatial

Ratings=pd.read_csv('ratings.csv',encoding='ISO-8859-1')
Movies=pd.read_csv('movies.csv',encoding='ISO-8859-1')
#Tags=pd.read_csv('tags.csv',encoding='ISO-8859-1') # this file will be usefull for featured recommendations 

# unified list of users / for this case list is of first 5000 interactions
users=sorted(list(set(Ratings['userId'][:5000]))) 

# unified list of items
items=sorted(list(set(Ratings['movieId']))) 

# combined matrix of users vs items |cell values = ratings
matrix= pd.DataFrame(0,index=users,columns=items) 

# u2u is for user to user similarity matrix | index = usedId, column_1 = distance
u2u = pd.DataFrame(index=users,columns=['distance'])

# i2i is for item to item similarity matrix | index = itemId, column_1 = distance 
i2i = pd.DataFrame(index=items,columns=['distance'])

# daframe for items from simliar users
item_to_consider = pd.DataFrame(index=items,columns=['itemId','distance'])

# dataframe to store recommendation result
suggested_items = pd.DataFrame(index=items,columns=['distance'])


#fill the values in the matrix | 
#earch row represents a user vector which contains user's ratings for all items |
# 0 or default value for no rating
for i in range(len(Ratings['userId'][:5000])):
    matrix.loc[int(Ratings.loc[i][0]),int(Ratings.loc[i][1])]= Ratings.loc[i][2]
    
# you can use matrix = matrix.transpose()
item_matrix = matrix.transpose()  

#user to user similarities for a particular user | compare one to all
u_temp = 54114
for i in list(u2u.index):  
    y= (sum((matrix.loc[u_temp]-matrix.loc[i])**2)**0.5)
    u2u.loc[i]= y if y !=0 else None
    
# find the list of items which user have rated
users_items = Ratings[Ratings.userId==u_temp]

#for better view of items | print user_items to see details of items which are rated by the given user
users_items = pd.merge(users_items[['movieId','rating']],Movies[['movieId','title','genres']],on='movieId').sort_values(by='rating',ascending=False)


# list of users with the distance from given user
x=u2u.sort_values(by='distance',ascending=True)

# list of users who are similar to given one
users_to_consider=x.index.values.tolist()

# removing users from the list who have distance value as None 
x['distance']=x['distance'].apply(lambda v : v if v!=None else 0)


# updating values of matrix by introducing distance of users from the given user
matrix = matrix.loc[users_to_consider]
matrix = x.join(matrix,how='inner')

for each in users_to_consider:
    matrix.loc[each]=(matrix.loc[each]/(1+matrix.loc[each][0]))*10

matrix = matrix.drop('distance',axis=1)
matrix = matrix.transpose()

# creating a list of itesm which are rated by similar users
ctr =1 
for i in users_to_consider:
    if ctr!=1:
        item_to_consider.add(matrix[i]) # better sorting
    else :
        item_to_consider = matrix[i]
    ctr+=1
    
# put a threshold as per the below line
#item_to_consider=(item_to_consider.iloc[item_to_consider.nonzero()[0]].sort_values()[item_to_consider>0].index).tolist()
item_to_consider=(item_to_consider.iloc[item_to_consider.nonzero()[0]]).sort_values().index.tolist()[:20]


#for each item from the similar users find simalar items from whole data
ctr = 1
for i_temp in item_to_consider:
    for i in list(i2i.index):   
        tempu = (sum((item_matrix.loc[i_temp]-item_matrix.loc[i])**2)**0.5)
        i2i.loc[i] = tempu 
    if ctr != 1:    
        suggested_items = suggested_items.add(i2i.sort_values(by='distance',ascending=False))
    else :
        suggested_items = i2i
    ctr+=1

# joining item details with suggested item list
suggested_movies = Movies.join(suggested_items,on='movieId',how='inner').sort_values(by='distance',ascending=True)
print(suggested_movies)

# distinct counts of genres of suggested items
print((pd.DataFrame('|'.join(suggested_movies['genres'].values.tolist()).split('|'))[0]).value_counts())
