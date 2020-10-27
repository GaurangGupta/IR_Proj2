try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

"""
	DESCRIPTION:
		Implementing Locality Sensitive Hashing by constructing buckets for storing hash values


	Methods:
		band_to_bucket()  : Breaks the signature matrix column into bands and puts the 
							hash value of the band values into the corresponding bucket

	Variables:
		numOfHashFns 	  : Number of unique hash functions taken (of the form (ax+b)%p)
		numOfDocs   	  : Number of question in the data set

	INPUT:
		signature_matrix.json

	OUTPUT:
		buckets.json

"""

#Load the signature matrix 
signature_matrix = json.load(open('signature_matrix.json','r'))

numOfHashFn = len(signature_matrix["1"])		#Number of hash functions
numOfDocs = len(signature_matrix)				#Number of questions


b = 30						#number of bands
r = numOfHashFn//b  		#number of rows
k = 10000000097				#number of buckets (chosen prime)

#Initialize empty bucket for each band
buckets = {band_no: {} for band_no in range(b)}		

def band_to_bucket(b,r,MOD):
	"""
	Populate the buckets dictionary with hash values for each band in each document/question

    Parameters:
	b (int) : Number of bands
	r (int) : Number of rows per band
	MOD(int): Number of buckets (taken large and prime)
 
   	"""

   	#Find the signature matrix column for every document
	for doc_no in range(1,numOfDocs+1):
		#Signature matrix column of the current doc
		doc_signature = signature_matrix[str(doc_no)]

		#Partition into bands
		for band_no in range(b):	

			#list of values in the band
			s = []
			s.extend(doc_signature[band_no*r:(band_no+1)*r])		

			try:
				#Add to the bucket if bucket is not empty
				buckets[band_no][(hash(tuple(s))%MOD)].add(doc_no)
			except KeyError:
				#Initialize the bucket set with the current hash value
				buckets[band_no][(hash(tuple(s))%MOD)] = {doc_no}

#Call the band_to_bucket function with appropriate parameters
band_to_bucket(b,r,k)


#Type casting bucket set to list for dumping into json
for band_no in range(b):
	for key in buckets[band_no].keys():
		buckets[band_no][key] = list(buckets[band_no][key])

#Dumping the buckets dictionary into a json file
with open('buckets.json', 'w') as write_file:
	json.dump(buckets, write_file)
