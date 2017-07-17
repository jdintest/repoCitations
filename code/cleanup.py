from bs4 import BeautifulSoup, Comment
import requests
import extract
from pymongo import MongoClient
import dateutil.parser
import time


#MongoDB stuff
client = MongoClient()
db = client.citations
collection = db.finalCitations
journals = db.journals

def reconcileTitle(citation):

    if citation.get("issn") != None:
        issns = citation.get("issn")
        for issn in issns:
            journalMatch = journals.find_one({"issn":issn}) 
            if journalMatch != None:
                citation['journalID'] = journalMatch['id_journal']
                break
    elif citation.get("titleMono") != None:
        title = citation.get("titleMono")
        journalMatch = journals.find_one({"$or":[{"main_title":title},{"all_titles":title}]})
        if journalMatch != None:
            citation['journalID'] = journalMatch['id_journal']
        else:
            journalMatch = journals.find_one({"abbreviation":title})
            if journalMatch != None:
                citation['journalID'] = journalMatch['id_journal']
      
    return citation

'''

def reconcileISSN(citation):
       
        takes a citation dictionary, returns it with ISSNs if they are missing
       
#if citation.get("doi") == None and citation.get("titleMono") != None:

        r= requests.get("http://localhost:8000/reconcile?query=" + citation)
        if r.status_code == 200:
            response = r.json()['result']
            for title in response:
                reconciledISSN = None
                if title['score'] > 0.90:
                    reconciledISSN = title['id']
                    break

            return reconciledISSN


import requests


def reconcileISSN(citation):
        
        takes a citation dictionary, returns it with ISSNs if they are missing
       

        if citation.get("doi") == None and citation.get("titleMono") != None:
                r= requests.get("http://localhost:8000/reconcile?query=" + citation.get("titleMono"))
                if r.status_code == 200:
                        try:
                                response = r.json()['result']

                                for title in response:
                                        if title['score'] > 0.90:
                                                citation['issn'] =[title['id']]
                                                break
                        except:
                                pass
        return citation
'''

def callSFX(citation):

    '''
    takes the citation, calls SFX, returns the citation with access data included

    dict -> dict
    '''

    #sfx stuff:
    SFXbaseURL = "http://sfx.scholarsportal.info/brock?"

    if citation.get("date") != None and citation.get("allISSNs") != None:
        if citation.get("date").year < 1900: #error checking for bad dates from grobid, replaces them with a reasonable stand-in
               date = 2015
        else:
               date = citation.get("date").year

        r= requests.get(SFXbaseURL + "sid=dingle_test&issn=" + str(citation.get("allISSNs")[7]) + "&year=" + str(date))
        if r.status_code == 200:
               response = r.text

               soup = BeautifulSoup(response,"lxml")

               #SFX returns a perl object as a comment in the <head> of the response page with contains a has_full_text value
               #this section parses that object to return the value
               head = soup.head

               for comments in head(text = lambda text:isinstance(text, Comment)):
                   comments.extract()
               commentsSoup = BeautifulSoup(comments,"lxml")
               contextObj = commentsSoup.ctx_object_1.string
               #need to error check here b/c sometimes extra <> elements in the contextObj cause errors and mean no string is returned
               if contextObj != None:

                   #the string indices 23 and 26 were found by trial and error. They should remain consistent as long as SFX doesn't change.
                   hasFullText = contextObj[contextObj.rfind("sfx.has_full_text")+23 :(contextObj.rfind("sfx.has_full_text")+ 26)]

                   if hasFullText == "yes": #uses the SFX has_full_text value
                       citation['access'] = "electronic"
                   elif response.find("Print Collection at the Library") != -1: #searches the page as a whole for this phrase
                       citation['access'] = "print"
                   else:
                       citation['access'] = "none"
        else:
            citation['access'] = "unknown"
    else:
        citation['access'] = "unknown"

    return citation


def parseResponse(citation):

    '''
    takes the html return from an SFX call and outputs the type of access Brock has

    bytes -> str
    '''
    if "issn" in citation and citation.get("date") != None:
        if int(citation.get("date").year) < 1900:
               date = 2015
        else:
               date = citation.get("date").year
        r= requests.get(SFXbaseURL + "sid=dingle_test&issn=" + str(citation.get("issn")[0]) + "year=" + str(date))
        if r.status_code == 200:
               response = r.text

               soup = BeautifulSoup(response,"lxml")

               head = soup.head

               for comments in head(text = lambda text:isinstance(text, Comment)):
                   comments.extract()
               commentsSoup = BeautifulSoup(comments,"lxml")
               contextObj = commentsSoup.ctx_object_1.string
               hasFullText = contextObj[contextObj.rfind("sfx.has_full_text")+23 :(contextObj.rfind("sfx.has_full_text")+ 26)]

               if hasFullText =="yes":
                   citation['access'] = "electronic"
               elif response.find("Print Collection at the Library") != -1:
                   citation['access'] = "print"
               else:
                   citation['access'] = "none"
    else:
        citation['access'] = "unknown"

    return citation

