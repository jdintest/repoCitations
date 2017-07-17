from pymongo import MongoClient

conn = MongoClient()
db = conn.citations
collection = db.journals



file = open("J_Entrez.txt","r")
text = file.read()
text_split=text.split("--------------------------------------------------------")
toProcess = text_split[1:]
response = []

for item in toProcess:
    text_dict = {}
    for line in item.splitlines():
        contents = line.split(":")
        if len(contents) > 1:
            text_dict[contents[0].rstrip()] = contents[1].strip()
    response.append(text_dict)


for item in response:
    if item.get('ISSN (Print)') != None:
        issn = item.get('ISSN (Print)')
        journalMatch = collection.find_one({"issn":issn})
        if journalMatch != None:
            collection.update({"id_journal":journalMatch['id_journal']},{"$set":{"abbreviation":item['IsoAbbr']}})
            print(item)
