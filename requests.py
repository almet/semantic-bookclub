from model import *

if __name__ == '__main__':
    populate()
    books = query("SELECT ?s WHERE { ?s dct:title ?o }")
    titles = query("SELECT ?o WHERE { ?s dct:title ?o }")
    friends = query("SELECT ?o WHERE { ?s foaf:knows ?o }")
    bookOwners = query("SELECT ?s WHERE { ?s book:ownsCopyOf ?o }")

    tom_loans = query('SELECT ?title WHERE { _:loan bc:borrower _:tom .\
                                             _:tom foaf:givenName "Tom" .\
                                             _:loan bc:borrowedBook _:book .\
                                             _:book dct:title ?title }')

    # 1. return all the people who own a book with a particular title
    title = "A Semantic Web Primer"
    q1 = query('SELECT ?name WHERE { _:member book:ownsCopyOf _:book .\
                                     _:book dct:title "%s" .\
                                     _:member foaf:givenName ?name }' % title)

    # 2. Return all books, and the people who have borrowed them, which were 
    # borrowed earlier than a given date.

    # FIXME Consider using a real date comparison
    # FILTER ( xsd:dateTime(?date) < xsd:dateTime("2005-01-01T00:00:00Z") )
    q2 = query('SELECT ?book ?borrower\
                WHERE { _:loan bc:borrowedBook ?book .\
                        _:loan bc:borrower ?borrower .\
                        _:loan bc:borrowedOn ?date .\
                FILTER (?date < "2006-02-20")\
                }')

    # 3. Identify the names and emails of people that have borrowed books from 
    # a person identified by an email address. 
    email = "al@bookclub.org"
    q3 = query('SELECT ?name ?email\
            WHERE { _:loan bc:bookOwner _:owner .\
                    _:loan bc:borrower _:borrower .\
                    _:borrower foaf:givenName ?name .\
                    _:borrower foaf:mbox ?email .\
                    _:owner foaf:mbox "%s"\
            }' % email)

    # 4.A person "A" say, knows a set of people P. Find all the titles of the 
    # books belonging to the people in P and those who are known to the people 
    # in P, not including the books of "A" (this represents the set of books which 
    # "A" can borrow!)
    # FIXME FILTER (NOT EXISTS {_:a book:ownsCopyOf ?book})\
    q4 = query('SELECT DISTINCT ?title\
            WHERE { ?book dct:title ?title .\
                    _:a foaf:mbox "%s" .\
                    _:a foaf:knows ?p .\
                    { _:p book:ownsCopyOf ?book }\
              UNION { _:p foaf:knows _:p2 .\
                      _:p2 book:ownsCopyOf ?book }\
            }' % email)


    from ipdb import set_trace; set_trace()
