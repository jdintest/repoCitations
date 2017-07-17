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


