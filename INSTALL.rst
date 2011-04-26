Semantic Book Club
##################

To install the semantic book club you need to go through the following steps:

* Creating the virtual environement
* Installing the dependencies
* Running the web system
* Initialising it

Creating the virtual environmenet
=================================

The virtual environement can be created using virtualenv. This is an optional
step but it allows to avoid having python library installed system wide. This
can be annoying in some cases, for isntance if you want to have two
incompatible versions of the same software / library.

Here is how to create a virtualenv named "bookclub"::

    $ mkvirtualenv bookclub

Then, all your prompts will be prefixed by (bookclub)

Installing the dependencies
===========================

The Semantic Book Club have several dependencies, both python and non python.
To install the python dependencies, you can run::

    $ pip install -r app/requirements.txt

The only non python dependency is berkley DB, wich is used as a backend for
a pure python triple store.

On debian based systems, you can install it by doing::

    $ apt-get install libdb4.8

Running the application
=======================

To run the application, run::

    $ python app/web.py

You can then open your browser at localhost:5000

Populate
========

The first time, you need to populate the book club with some data. You can do
so by going to the http://localhost:5000/populate URL.
