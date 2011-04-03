import csv
import shutil
from datetime import datetime

import surf
from rdflib.plugins.sleepycat import Sleepycat

__all__ = ('create_book', 'create_member', 'create_loan', 'populate', 'query', 
        'persist_to_rdf', 'Book', 'Member', 'Loan', 'persist', 'raw_query')

# create the store
sc = Sleepycat()
sc.open("db")
store = surf.Store(reader="rdflib", writer="rdflib", rdflib_store=sc)
session = surf.Session(store)

# register the namespaces used here
surf.ns.register(bc="http://notmyidea.org/bookclub/")
surf.ns.register(book="http://purl.org/NET/book/vocab/")

# map class with namespaces
Book = session.get_class(surf.ns.BC.Book)
Member = session.get_class(surf.ns.BC.Member)
Loan = session.get_class(surf.ns.BC.Loan)

class BookRepository(object):
    """Manage basic CRUD operations on the resources"""

# Useful functions to create entities
def create_book(id=None, title=None, author=None, publisher=None, year=None, 
        subject=None):

    if not id:
        id = str(max([int(b.bc_bookId.first) for b in Book.all()]) + 1)

    b = Book(surf.ns.BC + id)
    b.bc_bookId = id

    if title:
        b.bc_bookTitle = title
    if author:
        b.bc_bookAuthor = author
    if publisher:
        b.bc_bookPublisher = publisher
    if year:
        b.bc_bookPublicationYear = year
    if subject:
        b.bc_bookSubject = subject

    b.save()
    return b

def create_member(id=None, name=None, surname=None, email=None):
    m = Member(surf.ns.BC + name)

    if not id:
        id = str(max([int(m.bc_memberId.first) for m in Member.all()]) + 1)
    m.bc_memberId = id

    if name:
        m.bc_memberName = name
    if surname:
        m.bc_memberSurname = surname
    if email:
        m.bc_memberEmail = email

    m.save()
    return m

def create_loan(owner, borrower, book, date):
    l = Loan()
    l.bc_bookOwner = owner
    l.bc_borrower = borrower
    l.bc_borrowedBook = book
    l.bc_borrowedOn = date #datetime.strptime(date, "%d/%m/%Y")
    l.save()
    return l


def populate():
    """Use the samples provided to populate the triple store"""

    def _csv_import(filename, resource_creator):
        """import items from a csv file"""
        items = []
        with open(filename) as f:
            rows = list(csv.reader(f, delimiter='\t'))
            for row in rows[1:]:
                items.append(resource_creator(*row))
        return items

    # Ensure that the db is empty
    #try:
    #    shutil.rmtree("db")
    #except Exception,e:
    #    from ipdb import set_trace; set_trace()
    #    pass

    # import books, users
    # FIXME books can have multiple authors
    books = _csv_import('samples/books.txt', create_book)
    people = _csv_import('samples/people.txt', create_member)

    # import friendships
    with open("samples/knows.txt") as f:
        for m1, knows, m2 in csv.reader(f, delimiter="\t"):
            memberA = Member.get_by(bc_memberName=m1).one()
            memberB = Member.get_by(bc_memberName=m2).one()
            memberA.foaf_knows.append(memberB)
            memberA.update()

    # import loans
    with open("samples/lendings.txt") as f:
        for row in csv.reader(f, delimiter='\t'):
            owner = Member.get_by(bc_memberName=row[0]).one()
            borrower = Member.get_by(bc_memberName=row[4]).one()
            book = Book.get_by(bc_bookId=row[2]).one()
            create_loan(owner, borrower, book, row[6])

    # import book owners
    with open("samples/owns.txt") as f:
        for m, owns, bookId in csv.reader(f, delimiter="\t"):
            member = Member.get_by(bc_memberName=m).one()
            book = Book.get_by(bc_bookId=bookId).one()
            member.bc_owns.append(book)
            member.update()

    session.commit()

def query(sparql):
    """Does a sparql query and return the list of values"""
    items = []
    head, results = raw_query(sparql)
    for result in results['bindings']:
        item = []
        for var in head['vars']:
            item.append(result[var]['value'])
        items.append(item)
    return items


def raw_query(sparql):
    """Do a sparql query and return the (head, result) tuple"""
    return store.execute_sparql('prefix bc: <http://notmyidea.org/bookclub/>\
            prefix foaf: <http://xmlns.com/foaf/0.1/>\
            %s' % sparql).values()

def persist_to_rdf(filename):
    """Shortcut to persist the graph to a rdf file"""
    store.writer.graph.serialize(filename)

def persist(format="xml"):
    return store.writer.graph.serialize(format=format)
