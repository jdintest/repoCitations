import update
import extract
import repositoryFunctions
import requests
import mongoSetup
from pymongo import MongoClient

##########Config#############

communitiesList = [4,22,23] #the list of DSpace Communities which contain theses.
yearToProcess = 2017 # All theses submitted after Jan.1 of this year will be processed. Ex. setting 2014 means all theses 2014-present will be processed.


############################

client = MongoClient()
db = client.citations
citations = db.citations
journals = db.journals
toProcess = db.toProcess


def processThesis():
    #gets one thesis (by DSpace item number) from MongoDB toProcess collection
    item = repositoryFunctions.getThesisToProcess()
    #gets metadata for thesis via DSpace API
    citationResponse = repositoryFunctions.getMetadata(item)
    #locates bitstream of thesis via DSpace API
    bitstreams=repositoryFunctions.getBitstream(item)
    #tries to download pdf of thesis to process
    try:
        pdf = repositoryFunctions.downloadBitstream(bitstreams)
    except:
        repositoryFunctions.moveToFailedCollection(citationResponse)
        repositoryFunctions.deleteProcessedThesis(item)
        exit()
    #if pdf retrieved, send it to grobid for processing
    grobidResponse = extract.callGrobid(pdf)
    #checking if grobid fails
    if grobidResponse == "failed":
        repositoryFunctions.moveToFailedCollection(citationResponse)
        repositoryFunctions.deleteProcessedThesis(item)
    #if grobid doesn't fail, process the thesis and then move it to MongoDB processed collection
    else:
        citationFinal = update.extractCitations(grobidResponse, citationResponse)

        repositoryFunctions.moveToProcessedCollection(citationResponse)
        repositoryFunctions.deleteProcessedThesis(item)

####Processing####

# make sure grobid is running
try:
    r = requests.get("http://localhost:8080/isalive")
except:
    print("grobid not running")
    exit()

if r.text == "true":
    print("Grobid is working.")
else:
    print("Grobid not running. Start it and try again.")

# setup up indexes on Mongo Collections
mongoSetup.setupMongoCollections()


# search repository for theses to process and write to Mongo
repositoryFunctions.writeHandlesToMongo(communitiesList,yearToProcess)

# read from Mongo to process with Grobid

allTheses = toProcess.find().batch_size(20)

#for thesis in allTheses:

for i in range(0,20):
    processThesis() 
