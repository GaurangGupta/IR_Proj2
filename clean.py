import pandas as pd 
import json

"""
	DESCRIPTION:
    	Cleans the raw data csv file into a json file containing the data we need 

	
	Variables:
    	test          : Set containing all the questions
    	questions 	  : Dictionary containing questions with their ids assigned

	INPUT:
		raw_data.csv

	OUTPUT:
		Questions.json


"""


#pandas dataframe to load raw_data
data = pd.read_csv('Raw_data.csv')

#Set of unique questions
test = set()

#Questions with their corresponding ids
questions = {}


#Iterating over the rows of the dataframe
for i in range(len(data)):
	if type(data.loc[i,'question1']) == str:	#Consider only string entries
		ques = ''.join([ch.lower() if (ch.lower().isalnum() or ch.isspace()) else "" for ch in data.loc[i,'question1'] ])
		ques = ' '.join(ques.split())
		test.add(ques)							#Add the question to test set


#List of questions
test_write = []


#Constructing the dictionary questions
j=0
for ele in test:
	if len(ele):
		test_write.append(ele)
		questions[j+1] = ele
		j += 1


#Dumping the resultant dictionary into a json file
with open('Questions.json', 'w') as write_file:
	json.dump(questions, write_file)
