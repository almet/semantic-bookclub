Vocabularies
============

I have reused some vocabularies, and defined a new one (bookclub). This
coursework made me realise how to reuse vocabularies.

I first have redefined all the properties in my RDF Schema, becaseu I wanted to
have in some place a definition of all the properties that could be added on
a specific object.

Finally, I just reused a lot the vocabularies introduced by FOAF and Dublin
code, as well as some concepts from the book vocabularies (defined below)

* dct, dublin core terms (http://purl.org/dc/terms/)
* foaf, friend of a friend (http://xmlns.com/foaf/0.1/)
* book, the book vocaublary (http://purl.org/NET/book/vocab)
* bc, the book club vocabulary, the vocabulary that have been defined for this exercise

The notion of `group` is not used here, mainly because the system we have to 
implement only refer to one group of people (the book club).

If some interaction between groups were required, we could have used the 
foaf:Group property (defined at http://xmlns.com/foaf/spec/#term_Group).

The content of the RDF Schema file (which is also available in the
archive, at `/app/bookclub.rdf`) is provided in the appendix A.

TODO: Add some more rationale behind the choices for the vocabularies. Which
are the alternatives for each property and so on.

bc:Book (subclass of dct:PhysicalResource)
------------------------------------------

A new class `Book` is introduced by the bookclub vocabulary. It extends the
dublincore terms `PhysicalResource` class, which is not exactly applicable in
this case.

A book is a resource with the following properties:

* dct:identifier
* dct:title
* dct:creator
* dct:publisher
* dct:issued
* dtc:subject

bc:Member (foaf:Person)
-----------------------

A member of the bookclub is a subclass of `foaf:Person`, (which is in turn a
subclass of foaf:Agent). This is needed because the `Person` concept introduced
by foaf is not really accurate in our case (a person can be a member of the
bookclub, but it is not mendatory)

A member have an identifier, a given name, a family name and a mailbox address.
A member can also owns `Book`.

Here are the properties of a member:

* foaf:givenName
* foaf:familyName.
* foaf:mbox
* foaf:knows
* book:ownsCopyOf

bc:Loan
-------

A Loan is a concept which is not defined by neither foaf or dublin-core, so it
is redefined here.

Only the date property is reused here, from dct:date. The other propertues are
redefined for this vocabulary.

* borrowedBook, the book which have been borrowed
* borrower, the user who have borrowed the book (the range is a `bc:Member`)
* bookOwner,  the owner of the book which have been borrowed (the range is
  a `bc:Member`)
* dct:date, the date of the loan in this case.

Technology
==========

For this coursework, I have chosen to use the python programming langage
instead of the Java language which was recommended. I have made this choice in
order to discover some python tools to work with the semantic web.

The solution have been done using the `SuRF <http://packages.python.org/SuRF/>`_
python library which is based on `rdflib <http://rdflib.googlecode.com>`_

`SuRF` is an RDF/Object mapper, so it is possible to work directly with python
classes instead of raw nodes, as proposed by `rdflib` per default.

The solution also contains a web application, which have been developped with
the `flask <http://flask.pocoo.org>`_ micro framework. It is especially useful
to build little web applications like this one.

`rdflib` allows to work with different backends and I have chosen to work with
an implementation of a triple store built on top of the berkley db.

Alternatives
------------

For the langages, I have chosed python because ...

* Ruby
* Java

Design alternatives:

An other approach could have been to not use `SuRF` and to rely only on rdflib.
This could have been tedious is some cases, and the work proposed by SuRF
allows to ease the development.

Some edge cases ?

Test of the solution
--------------------

    ???

Solution design
---------------

The solution is composed of three python modules:

* `models.py` defines the class that are used as well as some utilities such as
  a function to make SPARQL queries.

  This module also contains the necessary code to import the sample data which
  have been provided for this coursework.

* `web.py` contains all the needed source code which handles the web server
  request / responses and interaction with the models.

Requests
--------

TODO Definition of what is possible to do with the requests

All the requests can be seen by going at http://localhost:5000/requests. They
are explained in detail in the following paragraphs.

Request 1
~~~~~~~~~

Request 2
~~~~~~~~~

Request 3
~~~~~~~~~

Request 4
~~~~~~~~~

Talk about the possibilities of SPARQL 1.1, how to do the filter ?

Evaluation of the solution
==========================

What is good, what is not ?

Bibliography / References
=========================

Appendix A
==========

.. code-block:: xquery
    :include: ../xml/queries2.xquery
