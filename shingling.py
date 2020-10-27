import json
"""
	DESCRIPTION:
		Creating shingles set for the question bank, assigning them ids and thus
		constructing the dense document-shingle matrix.

	Variables:
    	shingles          : Set containing all the unique shingles
    	shingle_size 	  : Length of each shingle
    	shingle_id 		  : Dictionary containing shingles with ids
		doc_shingle_dense : Dictionary containing the shingle ids each doc contains

	INPUT:
		Questions.json

	OUTPUT:
		shingles_id.json
		doc_shingle_dense.json

"""

start = time.time()

shingles = set()

shingle_size = 6

shingle_id = {}

#Load question bank
questions = json.load(open('Questions.json','r'))

#For each question, add shingles of length "shingle_size" to the set (shingles) 
for question in questions.values():
	for j in range(len(question)-shingle_size):
		shingles.add(question[j:j+shingle_size])


#Assigning ids to shingles
ind = 1
for shingle in shingles:
	shingle_id[shingle] = ind 
	ind += 1

#Dumping the shingle_id dictionary into a json file
with open('shingles_id.json', 'w') as write_file:
	json.dump(shingle_id, write_file)


#Constructing the dense document-shingle matrix
doc_shingle_dense = {}

#For each question, construct set of ids of all the shingles present in the question
doc_id = 1
for question in questions.values():
	ques_shingles = set()								#set of shingle ids in the question
	for j in range(len(question)-shingle_size):
		ques_shingles.add(shingle_id[question[j:j+shingle_size]])

	ques_shingles = list(ques_shingles)					#Converting the set to a list
	doc_shingle_dense[doc_id] = ques_shingles	
	doc_id += 1

#Dumping the doc_shingle_dense dictionary into a json file
with open('doc_shingle_dense.json', 'w') as write_file:
	json.dump(doc_shingle_dense, write_file)
