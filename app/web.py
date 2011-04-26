from flask import *
from werkzeug.wrappers import Response

from flaskext.wtf import (Form, SelectField as BaseSelectField, DateField,
        Required, TextField)

from model import *

# flask configuration
SECRET_KEY = "not so secret"

# flask initialisation
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BOOKCLUB_SETTINGS', silent=True)

# choices to be used in forms
def members():
    return lambda :[(m.foaf_givenName.first,) *2 for m in Member.all()]

def books():
    return lambda :[(b.dcterms_identifier.first, b.dcterms_title.first) for b in Book.all()]

# Forms

# need to redefine a field to handle dynamic loading of values
class SelectField(BaseSelectField):

    def _call_choices(self):
        if callable(self.choices):
            self.choices = self.choices()

    def iter_choices(self, *args, **kwargs):
        self._call_choices()
        return super(SelectField, self).iter_choices(*args, **kwargs)

    def pre_validate(self, *args, **kwargs):
        self._call_choices()
        return super(SelectField, self).pre_validate(*args, **kwargs)


class BookForm(Form):
    title = TextField("Title", validators=[Required()])
    authors = TextField("Authors", validators=[Required()])
    publisher = TextField("Publisher", validators=[Required()])
    year = TextField("Publication year")
    subject = TextField("What the book is about ? (separated by commas")
    owner = SelectField("Who owns this book ?", choices=members())

    def save(self):
        book = create_book(None, self.title.data, self.authors.data,
                self.publisher.data, self.year.data, self.subject.data)

        # get back the member resource
        owner = Member.get_by(foaf_givenName=self.owner.data).one()
        owner.book_ownsCopyOf.append(book)
        owner.update()
        flash("The book %s have been added" % self.title.data)

class MemberForm(Form):
    given_name = TextField("Given name", validators=[Required()])
    family_name = TextField("Family name", validators=[Required()])
    email = TextField("Email address", validators=[Required()])

    def save(self):
        create_member(None, self.given_name.data, self.family_name.data, self.email.data)
        flash("%s %s have been added" % (self.given_name.data, self.family_name.data))


class LoanForm(Form):
    owner = SelectField("Book owner", validators=[Required()], choices=members())
    borrower = SelectField("Book borrower", validators=[Required()], choices=members())
    book = SelectField("Book", validators=[Required()], choices=books())
    date = TextField("Date of the loan", validators=[Required()])

    def save(self):
        owner = Member.get_by(foaf_givenName=self.owner.data).one()
        borrower = Member.get_by(foaf_givenName=self.borrower.data).one()
        book = Book.get_by(dcterms_identifier=self.book.data).one()
        create_loan(owner, borrower, book, self.date.data)
        book_title = dict(self.book.choices)[self.book.data]
        flash("%s have successfully borrowed %s" % (self.borrower.data, book_title))


class FriendForm(Form):
    person1 = SelectField("First person", validators=[Required()], choices=members())
    person2 = SelectField("Seconf person", validators=[Required()], choices=members())

    def save(self):
        p1 = Member.get_by(foaf_givenName=self.person1.data).one()
        p2 = Member.get_by(foaf_givenName=self.person2.data).one()
        p1.foaf_knows.append(p2)
        p1.update()
        flash("%s and %s are now friends" % (self.person1.data, self.person2.data))

class BookOwningForm(Form):
    member = SelectField("Member", validators=[Required()], choices=members())
    book = SelectField("Book", validators=[Required()], choices=books())

    def save(self):
        member = Member.get_by(foaf_givenName=self.member.data).one()
        book = Book.get_by(dcterms_identifier=self.book.data).one()
        member.book_ownsCopyOf.append(book)
        member.update()
        flash("%s now owns %s" % (member.foaf_givenName.first, book.dcterms_title.first))


# utils for controllers
def deal_with_form(formClass, template):
    form = formClass()
    if request.method == "POST":
        if form.validate():
            form.save()
            return redirect(url_for("index"))
        else:
            flash("An error occured, please fill the form correctly")

    return render_template(template, form=form)

# Controllers
@app.route("/")
def index():
    if 'application/rdf+xml' == request.accept_mimetypes.best:
        return xml()
    else:
        return render_template("index.html",
                books = Book.all(),
                members = Member.all(),
                loans = Loan.all()
                )

@app.route("/populate")
def reset():
    populate()
    return redirect(url_for("index"))

@app.route("/debug")
def upload():
    from ipdb import set_trace; set_trace()
    return redirect(url_for("index"))

@app.route("/xml")
def xml():
    response = Response(persist())
    response.headers['content-type'] = "application/rdf+xml"
    return response

@app.route("/n3")
def n3():
    response = Response(persist('n3'))
    response.headers['content-type'] = "text/n3"
    return response

@app.route("/books/add", methods=["POST", "GET"])
def add_book():
    return deal_with_form(BookForm, "add_book.html")

@app.route("/members/add", methods=["POST", "GET"])
def add_member():
    return deal_with_form(MemberForm, "add_member.html")

@app.route("/books/borrow", methods=["POST", "GET"])
def add_loan():
    return deal_with_form(LoanForm, "borrow.html")

@app.route("/members/addfriend", methods=["POST", "GET"])
def add_friend():
    return deal_with_form(FriendForm, "add_friend.html")

@app.route("/books/addowner", methods=["POST", "GET"])
def add_bookowner():
    return deal_with_form(BookOwningForm, "add_bookowner.html")


@app.route("/loans/return/<book>/<owner>/<borrower>")
def return_loan(book, owner, borrower):

    # get the book with a SPARQL query
    answer = query('SELECT ?loan WHERE { \
            ?loan bc:borrowedBook ?book . \
            ?book dct:title "%s" . \
            ?loan bc:borrower ?borrower . \
            ?borrower foaf:givenName "%s" . \
            ?loan bc:bookOwner ?bookOwner . \
            ?bookOwner foaf:givenName "%s"}' % (book, borrower, owner))
    # TODO handle error

    # get the loan from the triple store
    loan = [l for l in Loan.all() if str(l.subject)==answer[0][0]][0]

    # and delete it
    loan.remove()
    flash('The book have been returned')
    return redirect(url_for('index'))

@app.route("/<email>/books")
def user_books(email):
    """List of books a user have copies of"""
    result = query('SELECT ?title ?id WHERE {\
                           ?user foaf:mbox "%s" .\
                           ?user book:ownsCopyOf ?book .\
                           ?book dct:title ?title .\
                           ?book dct:identifier ?id\
                    }' % email)
    books = [{'id': i[1], 'title': i[0]} for i in result]
    member = Member.get_by(foaf_mbox=email).one()
    return render_template("user_books.html", member=member, books=books)

@app.route("/books/<id>")
def show_book(id):
    #details about a book + list of people having this book
    owners = query('SELECT ?mbox WHERE{\
                        ?user book:ownsCopyOf ?book .\
                        ?book dct:identifier "%s" .\
                        ?user foaf:mbox ?mbox\
                    }' % id)
    return render_template("show_book.html", owners=owners, 
            book=Book.get_by(dcterms_identifier=id).one())

@app.route("/requests")
def requests():
    """The requests that are asked in the coursework"""

    # 1. return all the people who own a book with a particular title
    title = "A Semantic Web Primer"
    q1 = 'SELECT ?name WHERE { _:member book:ownsCopyOf _:book .\
             _:book dct:title "%s" .\
             _:member foaf:givenName ?name }' % title

    # 2. Return all books, and the people who have borrowed them, which were
    # borrowed earlier than a given date.

    # FIXME Consider using a real date comparison
    # FILTER ( xsd:dateTime(?date) < xsd:dateTime("2005-01-01T00:00:00Z") )
    q2 = 'SELECT ?bookTitle ?borrowerName\
            WHERE { _:loan bc:borrowedBook _:book .\
            _:loan bc:borrower _:borrower .\
            _:borrower foaf:givenName ?borrowerName .\
            _:book dct:title ?bookTitle .\
            _:loan bc:borrowedOn ?date .\
            FILTER (?date < "2006-02-20")\
            }'

    # 3. Identify the names and emails of people that have borrowed books from
    # a person identified by an email address.
    email = "al@bookclub.org"
    q3 = 'SELECT ?name ?email\
            WHERE { _:loan bc:bookOwner _:owner .\
                    _:loan bc:borrower _:borrower .\
                    _:borrower foaf:givenName ?name .\
                    _:borrower foaf:mbox ?email .\
                    _:owner foaf:mbox "%s"\
            }' % email

    # 4.A person "A" say, knows a set of people P. Find all the titles of the
    # books belonging to the people in P and those who are known to the people
    # in P, not including the books of "A" (this represents the set of books which
    # "A" can borrow!)
    # FIXME FILTER (NOT EXISTS {_:a book:ownsCopyOf ?book})\
    q4 = 'SELECT DISTINCT ?title WHERE \
            { ?book dct:title ?title .\
                    ?a foaf:mbox "%s" .\
                    ?a foaf:knows ?p .\
                    { ?p book:ownsCopyOf ?book }\
                    UNION { ?p foaf:knows ?p2 .\
                            ?p2 book:ownsCopyOf ?book }\
            }\
            ' % (email)

    # SPARQL 1.1 MINUS { ?a foaf:mbox "%s" . ?a book:ownsCopyOf ?book }}\

    return render_template("requests.html",
            q1=q1, q1_results=query(q1),
            q2=q2, q2_results=query(q2),
            q3=q3, q3_results=query(q3),
            q4=q4, q4_results=query(q4)
            )

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
