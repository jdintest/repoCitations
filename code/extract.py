import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import quote

### Assorted extraction and parsing Functions 


def callGrobid(filename):
    '''
    takes a pdf bitstream and processes it with Grobid, returns a grobid TEI/xml bitstream

    bytes -> bytes

    '''
    
    url = "http://localhost:8080/api/processReferences"
    files = {"input": filename}

    r = requests.post(url,files=files)
    if r.status_code == 200:
        return r.content
    else:
        return "failed"


def filterCitations(citations):

	'''
	
	takes a list of citations from grobid, allows user input to filter incorrectly identified citations, returns updated list
	
	list -> list
	
	'''
	
	startIndex = 0
	stopIndex = 0

	# iterates forward until a good citation is found
	for citation in citations:
		print(" ")
		print(citation)
		print(" ")

		reply = None
		
		while reply not in ["y","n"]:
			reply = input("Is this a citation? (y/n) ")
			print(reply)

		if reply =="y":
			break

		startIndex = startIndex + 1


	#iterates backward until a good citation is found
	for citation in reversed(citations):
		print(" ")
		print(citation)
		print(" ")

		reply = None
		
		while reply not in ["y","n"]:
			reply = input("Is this a citation? (y/n) ")
			print(reply)

		if reply =="y":
			break

		stopIndex = stopIndex - 1
		
	if stopIndex < 0:
		citations = citations[:stopIndex]
	if startIndex > 0:
		citations = citations[startIndex:]
		
		
	return citations

def correctType(citation):

    '''
    receives a dictionary for a citation, returns a dictionary with citation['type'] error corrected
    dict -> dict

    '''
    fieldsToCheck = ['titleArticle','titleMono']
    internetMatches = ["Retrieved from", "retrieved from", "Available at", "available at","Available from", "available from"]

    for field in fieldsToCheck:
        if field in citation:
            for match in internetMatches:
                if citation.get(field).find(match) != -1:
                    citation['type'] = "internet"
                    break
    return citation

def callCrossRef(citation):

    '''
    takes citation from grobid, calls Crossref for doi and ISSN data

    dict -> dict
    '''

    if citation.get("type") == "journal" or citation.get("type") == "monograph":
            payload = quote(str(citation.get("payload")))
            r = requests.get("https://api.crossref.org/works?query=" + payload + "&mailto=jdingle@brocku.ca")
            if r.status_code == 200:
                firstResponse = r.json()
                if len(firstResponse['message']['items']) > 0:
                    response = r.json()['message']['items'][0]
                    citation['confidenceScore'] = response['score']
                    #this error threshold of 60 was determined by trial and error. It can be adjusted to be more or less conservative.
                    if response['score'] > 60:
                        citation['doi'] = response['DOI']
                        if response.get("ISSN") != None:
                            citation['issn'] = response.get("ISSN")

    citation.pop("payload")

    return citation



