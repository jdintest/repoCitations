from pymongo import MongoClient

client = MongoClient()
db = client.citations
citations = db.citations
journals = db.journals
toProcess = db.toProcess


def setupMongoCollections():
    citations.create_index("id",unique=True)
    toProcess.create_index("handle",unique=True)

    print("Indexes created")


