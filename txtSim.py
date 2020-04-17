import binascii
import sys, getopt
import string
import random
import numpy as np
from array import *

if (len(sys.argv) != 4):
	print('Wrong number of arguments')
	print("python .\\ass1.py <number of Docs> <inputfile> <outputfile>")
	sys.exit()
#print('Argument List:', str(sys.argv))

numDocs = (int)(sys.argv[1])
dataFile = (str)(sys.argv[2])
ofile = (str)(sys.argv[3])
#print(numDocs, dataFile, ofile)

# create a dictionary of the articles, mapping the article identifier (e.g., 
# "t8470") to the list of shingle IDs that appear in the document
docSets = {};

docNames = []
totalHashes = 0

### function for set of hashes =============================================
def hashes(s, k):
	n = len(s)
	shinglesInDoc = set()
	
	for i in range(n-k-1):
		shingle = s[i:i+k]
		# compute the hash value of the shingle
		hashValue = binascii.crc32(shingle.encode('utf-8')) & 0xffffffff
		# add the hash value
		shinglesInDoc.add(hashValue)
	return shinglesInDoc

## Step 1 ===========================================================================
# open data file
f = open(dataFile)

for i in range(0, numDocs):
	words = f.readline().split(" ")
	# retrieve the article ID
	docID = words[0]
	# maintain a list of all document IDs
	docNames.append(docID)
	del words[0]

	# make them one String and remove ID and newline
	s = ''.join(word for word in words).replace('\n','')
	# strip punctuations
	exclude = set(string.punctuation)
	s = ''.join(ch for ch in s if ch not in exclude)

	# set k =7 && make all lower
	docSets[docID] = hashes(s.lower(),7)

	# count the number of hashes across all documents.
	totalHashes = totalHashes + len(docSets[docID])

# close the data file.  
f.close()  
print('\nAverage shingles per doc: %.2f' % (totalHashes / numDocs))

## Step 2 =========================================================================
# return a random hash function from a universal family
# p = prime number > m
def make_random_hash_function(p=2**33-355, m=2**32-1):
    a = random.randint(1,p-1)
    b = random.randint(0, p-1)
    return lambda x: ((a * x + b) % p) % m

M = []

# We will have 100 lines
for i in range(100):
	# chosse one hash function for every line
	h = make_random_hash_function()
	n = []
	for j in docNames:
		mni = sys.maxsize #sys.maxint
		artSet = docSets[j]
		# keep min for for each article
		for y in artSet:
			mni = min(h(y),mni)
		n.append(mni)
	M.append(n)
print("M table was computed successfully")

# transpose matrix to take the signature of article
Mt = np.array(M).transpose()

def findSim():
	inti = 0
	text_file = open(ofile, "w")
	for i in Mt:
		for j in range(inti+1,len(Mt)):
			# compute the fraction of entries in which two vectors are equal
			#f = np.mean(i == j)
			#print("Fraction of equal entries = %.4f" %f)
			jt = Mt[j]
			Js = (len(set(i).intersection(set(jt))) / len(set(i).union(set(jt))))
			if (Js > 0.85):
				# to typoma diaferei polu sthn akreibeia pou 8a baloume
				#print("Jaccard similarity of {},{} = {:.4f}" .format(docNames[inti],docNames[j],Js))
				text_file.write("Jaccard similarity of {},{} = {:.3f} \n" .format(docNames[inti],docNames[j],Js))
		inti += 1
	text_file.close()

# Compute JS and write in file those with js > 0.85 (optional in this step)
# Optional

#findSim()

## Step 3 =======================================================================
def cand(Mt, r, b):
	cnd = []
	for i in range(b):# for each band
		# Buckets hash value in pos == article's pos in M
		bucks = {};
		h = make_random_hash_function()
		for j in range(len(Mt)):# for each article
			sig = 0 # or make them to str and hash
			for q in Mt[j][i*r:i*r+5]:# make numbers of signature one
				sig += h(int(q))
			if sig in bucks:
				bucks[sig].append(j)
			else:
				#bucks[sig] = [docNames[j]]
				bucks[sig] = [j]
		for z in bucks:
			#print(bucks[z])
			if (len(bucks[z]) > 1):
				if bucks[z] not in cnd:
					cnd.append(bucks[z])
	return cnd

# r rows per band
# b bands
# b = 20 => r = 5
# k buckets (as large as possible)
# s threshold / s~(1/b)^(1/r)
# =>Prob at least 1 band identical = 1-(1-s^r)^b
b = 20
r = 5
s = 0.8 # Pr = .9996
candid = cand(Mt,r,b)
#print(candid)

text_file = open(ofile, "w")

for c in candid:
	if (len(c) == 2):
		#Js = (len(set(Mt[c[0]]).intersection(set(Mt[c[1]]))) / len(set(Mt[c[0]]).union(set(Mt[c[1]]))))
		Js = (len(docSets[docNames[c[0]]].intersection(docSets[docNames[c[1]]])) / len(docSets[docNames[c[0]]].union(docSets[docNames[c[1]]])))
		if (Js > 0.8):
			text_file.write("Jaccard similarity of {},{} = {:.3f} \n" .format(docNames[c[0]],docNames[c[1]],Js))
	if (len(c) > 2): # 3 or more similar articles
		for i in range(len(c)-1):
			for j in range(i+1,len(c)):
				#Js = (len(set(Mt[c[i]]).intersection(set(Mt[c[j]]))) / len(set(Mt[c[i]]).union(set(Mt[c[j]]))))
				Js = (len(docSets[docNames[c[i]]].intersection(docSets[docNames[c[j]]])) / len(docSets[docNames[c[i]]].union(docSets[docNames[c[j]]])))
				if (Js > 0.5):
					text_file.write("Jaccard similarity of {},{} = {:.3f} \n" .format(docNames[c[i]],docNames[c[j]],Js))
text_file.close()