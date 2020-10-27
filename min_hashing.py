import random 
import time
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

"""
	DESCRIPTION:
		Creating the signature matrix using multiple hash functions


	Methods:
		hash_val() 		  : Returns the value (ax+b)%p 
		gen_hash() 		  : Generates unique 'a' and 'b' values in the range (0,numOfShingles-1)
		signature_matrix(): Constructs the signature matrix
	

	Variables:
		numOfHashFns 	  : Number of unique hash functions taken (of the form (ax+b)%p)
		numOfShingles 	  : Number of unique shingles 
		numOfDocs   	  : Number of question in the data set

	INPUT:
		shingles_id.json
		doc_shingle_dense.json

	OUTPUT:
		hashFunctions.json
		signature_matrix.json

"""


#Load the shingles_id.json file to find number of shingles
shingles = json.load(open('shingles_id.json','r'))

#Load the document-shingle matrix 
doc_shingle_dense = json.load(open('doc_shingle_dense.json','r'))

numOfHashFn = 120
numOfShingles = len(shingles)
numOfDocs = len(doc_shingle_dense)



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


def gen_hash(numOfShingles, seed_val):
	"""
	Generates random a,b values

    Parameters:
	numOfShingles(int) : number of shingles
	seed_val (int)	   : seed to generate same values in each run
 
    Returns:
	a and b values
   	"""
	random.seed(seed_val)
	a = random.randint(0,numOfShingles-1)

	random.seed(time.time())
	b = random.randint(0,numOfShingles-1)

	return a,b



def signature_matrix():
	"""
	Constructs the signature matrix
 
    Returns:
	Signature matrix
   	"""

	signature_matrix = {}

	#Generating hash function
	hashFunctions = {}
	for h in range(1,numOfHashFn+1):
		a,b = gen_hash(numOfShingles,h)
		hashFunctions[h] = [a,b]

	#Dumping the hashFunctions dictionary into a json file
	with open('hashFunctions.json', 'w') as write_file:
		json.dump(hashFunctions, write_file)


	#Construction of signature matrix
	for doc_no in range(1,numOfDocs+1):
		local_time = time.time()
		doc_hash = []

		for h in range(1,numOfHashFn+1):
			a = hashFunctions[h][0]
			b = hashFunctions[h][1]

			min_hash_val = 1000000000

			#Finding the minimum hash value from all the shingles in the current doc
			for shingle_id in doc_shingle_dense[str(doc_no)]:
				min_hash_val = min(min_hash_val,hash_val(a,b,shingle_id,numOfShingles))

			doc_hash.append(min_hash_val)

		signature_matrix[doc_no] = doc_hash

	return signature_matrix

signMatrix = signature_matrix()

#Dumping the signMatrix dictionary into a json file
with open('signature_matrix.json', 'w') as write_file:
	json.dump(signMatrix, write_file)
