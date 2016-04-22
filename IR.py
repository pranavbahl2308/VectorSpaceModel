import codecs
import re
import os
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from array import array
from collections import defaultdict
import argparse
import math
import yaml

class CreateIndex:

	def __init__(self,args):
		self.inputFolder = args.i
	        self.index=defaultdict(list)
		self.currDoc = ""
		self.dictFile = args.d
		self.postingFile = args.p
		self.noOfDocs = 0
		self.vectors = defaultdict(list)

	def createIndex(self):
		self.readFile()
		self.writeIndexToFile()

	def readFile(self):
		documents = os.listdir(os.getcwd()+"/"+self.inputFolder)
		self.noOfDocs = len(documents)
		for i in documents:
			raw = BeautifulSoup(codecs.open(os.getcwd()+"/"+self.inputFolder+"/"+i,'r')).body.get_text().encode('ascii','ignore')
			stemmed = self.preProcessing(raw,i)
			for termpage, postingpage in self.buildIndex(stemmed,i).iteritems():
                		self.index[termpage].append(postingpage)
			self.vectors[re.sub('\.htm$', '', i)]

	def preProcessing(self,raw,fileName):
		cachedStopWords = stopwords.words("english")
		stemmer = PorterStemmer()
		text = ' '.join([word for word in raw.split() if word not in cachedStopWords])
		tokens = nltk.word_tokenize(text.lower())
		stemmed = []
		directory = os.getcwd()+"/pre-process/" 
		if not os.path.exists(directory):
			os.makedirs(directory)
		test = open(directory+re.sub('\.htm$', '', fileName)+".txt","w")
		for item in tokens:
			stemmed.append(stemmer.stem(item))
			test.write(stemmer.stem(item)+' ')
		test.close()
		return stemmed

	def buildIndex(self,stemmed,docName):
		termdictPage={}
		for position, term in enumerate(stemmed):
			try:
				termdictPage[term][1].append(position)
			except:
				termdictPage[term]=[re.sub('\.htm$', '', docName), array('I',[position])]
		return termdictPage

	def writeIndexToFile(self):
		'''write the inverted index to the file'''
		dictFile=open(os.getcwd()+"/"+self.dictFile, 'w')
		postFile=open(os.getcwd()+"/"+self.postingFile, 'w')
		idfFile=open(os.getcwd()+"/idf.txt", 'w')
		
		for term in self.index.iterkeys():
			postinglist=[]
			termCount = 0
			docCount = 0
			idf = 0
			terdocdict = defaultdict(int)
			for p in self.index[term]:
				docID=p[0]
				positions=p[1]
				posLen = len(positions)
				termCount += posLen
				terdocdict[docID]= posLen
				docCount += 1
				postinglist.append(':'.join([str(docID) ,str(posLen)]))
			idf = math.log(self.noOfDocs/docCount)
			for vec in self.vectors:
				if vec in terdocdict:
					self.vectors[vec].append(float(terdocdict[vec])*idf)
				else:
					self.vectors[vec].append(float(0))									
			print >> idfFile, ''.join((term,'|',str(idf)))
			print >> postFile, ''.join((term,'|',';'.join(postinglist)))
			print >> dictFile, ''.join((term,'|',str(docCount),'|',str(termCount)))
		yaml.dump(self.vectors,open(os.getcwd()+"/tf-idf.yaml", 'w'))
		dictFile.close()
		postFile.close()
		idfFile.close()

if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', help='Document folder name')
	parser.add_argument('-d', help='Dictionary file name')
	parser.add_argument('-p', help='Posting file name')
	args = parser.parse_args()
	c=CreateIndex(args)
	c.createIndex()
