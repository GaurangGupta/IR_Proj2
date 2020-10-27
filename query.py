try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

import time

"""
	DESCRIPTION:
		Finding duplicates/near duplicate questions based on user query


	Methods:
		hash_val() 		     : Returns the value (ax+b)%p 
		clean_query() 	     : Retains alphanumeric and spaces in the query
		shingling_query()    : Creates shingles for the query 
		min_hash_query()     : Constructs the signature matrix for the query
		lsh_query()          : Partitions query signature matrix into bands and computes the bucket
		jaccard_similarity() : Calculates the jaccard similarity of the query with each matches document of lsh

	Variables:
		numOfHashFns 		 : Number of unique hash functions taken (of the form (ax+b)%p)
		MOD 			     : Number of buckets

	INPUT:
		Questions.json
		shingles_id.json
		doc_shingle_dense.json
		hashFunctions.json
		buckets.json
		signature_matrix.json
		query (str) : User input
	
	OUTPUT:
		Top 5 matched documents based on Jaccard Similarity	

"""

#assigned in min_hash_query function
numOfHashFn   = 120 

#Number of buckets (taken large and prime)
MOD = 10000000097



def hash_val(a, b, val, p):
	"""
	Computes the hash value with given parameters

    Parameters:
    a (int) : 'a' value of the hash function
    b (int) : 'b' value of the hash function
    val(int):  shingle_id
    p (int) :  numOfShingles
 
    Returns:
	int: Hash value from given parameters

   	"""
	return (a*val + b)%p


def clean_query(query):
	"""
	Cleans the query by removing special characters 

    Parameters:
    query (str)         : User query
   
    Returns:
	cleaned_query(str)  : Cleaned query

   	"""
	cleaned_query = ''.join([ch.lower() if (ch.lower().isalnum() or ch.isspace()) else "" for ch in query])
	cleaned_query = ' '.join(cleaned_query.split())

	return cleaned_query


def shingling_query(query, shingles):
	"""
	Constructs document-shingle matrix for the cleaned query

    Parameters:
    query (str)         : User query
	shingles  		    : Shingle ids
 
    Returns:
	numOfShingles		: Number of unique shingles in the data set
	query_shingle_dense : Document-shingle matrix of the query

   	"""
	SHINGLE_SIZE = len(next(iter(shingles.keys())))
	numOfShingles = len(shingles)

	query_shingle_dense = set()

	#Taking shingles of length SHINGLE_SIZE from the query and adding it to the set
	for j in range(len(query)-SHINGLE_SIZE):
		try:
			#If shingle exists in the shingle set of dataset
			query_shingle_dense.add(shingles[query[j:j+SHINGLE_SIZE]])
		except KeyError:
			#Ignore if shingle not present
			pass

	#Typecast set to list
	query_shingle_dense = list(query_shingle_dense)
	return numOfShingles,query_shingle_dense


def min_hash_query(query_shingle_dense, numOfShingles, hashFunctions):	#return signature matrix
	"""
	Constructs signature matrix for the query 

    Parameters:
    query_shingle_dense : Doc-shingle matrix for the query
    numOfShingles		: Number of unique shingles in the dataset
    hashFunctions       : List of hash function coefficients 
 
    Returns:
    signature_matrix_query  : Signature matrix of the query

   	"""
	numOfHashFn = len(hashFunctions)

	signature_matrix_query = []

	#For each hash function
	for h in range(1,len(hashFunctions)+1):

		#Load the hash function coefficients from the stored json file
		a = hashFunctions[str(h)][0]
		b = hashFunctions[str(h)][1]
		min_hash_val = 1000000000

		#Finding the minimum hash value from all the shingles in the query
		for shingle_id in query_shingle_dense:
			min_hash_val = min(min_hash_val,hash_val(a,b,shingle_id,numOfShingles))

		#Add the minimum hash value to the signature matrix
		signature_matrix_query.append(min_hash_val)


	return signature_matrix_query



def lsh_query(signature_matrix_query, buckets):
	"""
	Constructing buckets for storing hash values of the query

    Parameters:
	signature_matrix_query  : Signature matrix of the query
	buckets				    : Buckets of the dataset signature matrix
 
    Returns:
	querySimilar 		    : Set containing the doc ids of the docs similar to the query

   	"""

	b = len(buckets)		#Number of bands
	r = numOfHashFn//b  	#Number of rows per band

	querySimilar = set()	#Set of docs similar to the query

	#For each band
	for band_no in range(b):

		#list of values in the band
		s = []
		s.extend(signature_matrix_query[band_no*r:(band_no+1)*r])

		#Hash value of the list
		query_bucket = hash(tuple(s))

		try:
			#Add to the bucket if bucket exists
			for doc in buckets[str(band_no)][str(query_bucket%MOD)]:
				querySimilar.add(doc)
		except KeyError:
			pass


	return querySimilar


def jaccard_similarity(signature_matrix_query, similar_docs, signature_matrix):
	"""
	Computes the Jaccard Similarity of each doc in list of similar docs with the query

    Parameters:
	signature_matrix_query  : Signature matrix of the query
	similar_docs		    : Set containing the doc ids of the docs similar to the query
	signature_matrix 		: Signature matrix of the dataset 
 
    Returns:
	similarities			: A list of Jaccard similarity corresponding to each doc in similar_docs

   	"""
	similarities = {}

	#For each similar document
	for doc in similar_docs:

		intersection = 0
		union = numOfHashFn

		for h in range(numOfHashFn):
			#If the Hash values match, increase intersection by 1
			if signature_matrix_query[h]==signature_matrix[str(doc)][h]:
				intersection += 1

		#Jaccard similarity = (Intersection)/(Union)
		similarities[doc] = intersection/union

	return similarities



if __name__ == '__main__':

	st = time.time()
	print("Loading. Please wait ... ")

	#Loading the neccessary json files

	buckets = json.load(open('buckets.json','r'))
	signature_matrix = json.load(open('signature_matrix.json','r'))
	hashFunctions = json.load(open('hashFunctions.json','r'))
	shingles = json.load(open('shingles_id.json','r'))
	docs = json.load(open('Questions.json','r'))

	print(time.time()-st)

	#User response
	repeat = 1

	while(repeat):
		#Take input
		query = input("Enter query: ")

		start = time.time()
		print("Input query accepted")

		#Clean the query
		query = clean_query(query)

		print("Query Cleaned")

		#Make shingles from the query
		numOfShingles,query_shingle = shingling_query(query,shingles)

		print("Shingling done")

		#Construct the signature matrix of the query
		signature_matrix_query = min_hash_query(query_shingle, numOfShingles, hashFunctions)

		print("Min hashing done")

		#Find the list of documents similar to the query
		similar_docs = lsh_query(signature_matrix_query, buckets)

		#Calculate the Jaccard Similarity with each of the similar docs
		jaccard_similarity_docs = jaccard_similarity(signature_matrix_query,similar_docs,signature_matrix)
		
		#Sort docs in decreasing order of jaccard similarity values
		jaccard_similarity_docs = {k: v for k, v in sorted(jaccard_similarity_docs.items(), key=lambda item: item[1], reverse = True)}
		

		#Output 5 results
		results = 0

		#Print the top 5 jaccard sim. docs
		for doc,score in jaccard_similarity_docs.items():
			if(len(docs[str(doc)])<=45):
				print(docs[str(doc)]," "*(45-len(docs[str(doc)])),"   Jaccard Similarity =",score*100)
			else:
				print(docs[str(doc)][0:42],"...    Jaccard Similarity =",score*100)

			results += 1
			if results == 5:
				break

		#In case no document matches the query
		if results ==0:
			print("No results to show")
		elif(results < 5):
			print("No more results to show")


		print("time taken =",time.time()-start)

		print("")
		#Continue searching?
		repeat = ""
		while repeat!='1' and repeat!='0':
			repeat = input("Search again? (1,0) ")
		
		repeat = int(repeat)
		print("")