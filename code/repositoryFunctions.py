import requests
import dateutil.parser
import pytz
import pymongo

baseDSpaceUrl = "https://dr.library.brocku.ca/rest"
conn = pymongo.MongoClient()
db = conn.citations



#list of all recpository communities that contain theses, as of June 2017.
communitiesList=[4,22,23]

def getCollections(community):

    headers = {"accept":"application/json"}
    r = requests.get(baseDSpaceUrl + "/communities/" + str(community) + "/collections",headers=headers)
    theses = r.json()
    collectionArray=[]
    for item in theses:
        collectionArray.append(item['id'])

    return collectionArray

def getTheses(collection):
    headers = {"accept":"application/json"}
    r = requests.get(baseDSpaceUrl + "/collections/" + str(collection)+ "/items?limit=1500",headers=headers)
    theses = r.json()
   
    theses = sorted(theses, key=lambda k:k['id'], reverse=True)
    
    return theses
    
def getBitstream(item):
    
    bitstreams = []
    r = requests.get(baseDSpaceUrl + "/items/" + str(item) + '/bitstreams')
    bitstreamList = r.json()
    for bitstream in bitstreamList:
        if bitstream['mimeType'] == 'application/pdf':
            bitstreams.append(bitstream['id'])

    if len(bitstreams) > 0:
        return bitstreams[0]
    else:
        return "not found"

def downloadBitstream(bitstream):

    r= requests.get(baseDSpaceUrl + "/bitstreams/" + str(bitstream) + "/retrieve")

    return r.content

def getMetadata(item):
    metadata = {}
    r = requests.get(baseDSpaceUrl + "/items/" +str(item) + '/metadata')
    if r.status_code == 200:
        response = r.json()
        metadata['item'] = str(item)
        for field in response:
            if field['key'] == "dc.identifier.uri":
                metadata['handle'] = field['value']
            if field['key'] == "dc.degree.name":
                metadata['degree']= field['value']
            if field['key'] =="dc.date.accessioned":
                metadata['thesisDate'] = field['value']
    return metadata
    
        
def getSinceDate(theses,date):

    collection = db.toProcess
    for thesis in theses:
        thesisMetadata = getMetadata(str(thesis['id']))
        if dateutil.parser.parse(thesisMetadata['thesisDate']) >= dateutil.parser.parse(str(date) + "-01-01T00:00:00Z "):
            doc = {"handle":thesisMetadata['handle'],'item':thesisMetadata['item']}
            print("Writing to Mongo ....")
            collection.insert(doc)
            print(doc)
        else:
            return

def getThesisToProcess():

    collection = db.toProcess
    item = collection.find_one()['item']

    return item


def deleteProcessedThesis(item):

    collection = db.toProcess
    collection.remove({"item":item})

    print(item + " deleted")

def moveToFailedCollection(citationResponse):

    collection= db.failed
    collection.insert({"item":citationResponse['item'], "handle":citationResponse['handle']})

    print(citationResponse['handle'] + " moved to failed collection")


def moveToProcessedCollection(citationResponse):

    collection= db.processed
    collection.insert({"item":citationResponse['item'], "handle":citationResponse['handle']})

    print(citationResponse['handle'] + " moved to processed collection")


def writeHandlesToMongo(communities,year):

    for community in communities:
        collections = getCollections(community)
        for collection in collections:
            theses = getTheses(collection)
            getSinceDate(theses,year)




