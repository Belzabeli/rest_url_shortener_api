from flask import Flask, render_template, request, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import SubmitUrlForm, PremiumUrlForm
import datetime
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()


class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String(250))
    short = db.Column("short", db.String(250))
    clicks = db.Column("clicks", db.Integer, default=0)
    date = db.Column("date", db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, long, short):
        self.long = long
        self.short = short

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class PremiumUrls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String(250))
    short = db.Column("short", db.String(250))
    clicks = db.Column("clicks", db.Integer, default=0)
    date = db.Column("date", db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, long, short):
        self.long = long
        self.short = short

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    while True:
        rand_letters = random.choices(letters, k=7)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters


@app.route('/', methods=['POST', 'GET'])
def home():
    form = SubmitUrlForm()
    if form.validate_on_submit():
        url = form.url.data
        found_url = Urls.query.filter_by(long=url).first()

        if found_url:
            return jsonify(url=found_url.to_dict())
        else:
            short_url = shorten_url()
            print(short_url)
            new_url = Urls(url, short_url)
            db.session.add(new_url)
            db.session.commit()
            return jsonify(url=new_url.to_dict())
    else:
        return render_template("url_page.html", form=form)


@app.route("/premium-clients", methods=["GET", "POST", "PATCH"])
def premium_clients():
    form = PremiumUrlForm()
    if form.validate_on_submit():
        url = form.url.data
        found_url = PremiumUrls.query.filter_by(long=url).first()

        if found_url:
            return jsonify(url=found_url.to_dict())
        else:
            short_url = form.short_custom_url.data
            print(short_url)
            new_url = PremiumUrls(url, short_url)
            db.session.add(new_url)
            db.session.commit()
            return jsonify(url=new_url.to_dict())
    else:
        return render_template("url_page.html", form=form)


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return "<h1>Url doesnt exist</h1>"



# HTTP UPDATE clicks


@app.route("/update-clicks/<int:url_id>", methods=["PATCH"])
def update_click(url_id):
    url = db.session.query(Urls).get(url_id)
    if request.method == "PATCH":
        url.clicks += 1
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the clicks."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry an url with that id was not found in the database."}), 404


@app.route("/premium-update-clicks/<int:url_id>", methods=["PATCH"])
def premium_update_click(url_id):
    premium_url = db.session.query(PremiumUrls).get(url_id)
    if request.method == "PATCH":
        premium_url.clicks += 1
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the clicks."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry an url with that id was not found in the database."}), 404


#delete URLs

@app.route("/delete-url/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        url = db.session.query(Urls).get(url_id)
        if url:
            db.session.delete(url)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the URL from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a URL with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@app.route("/premium-delete-url/<int:url_id>", methods=["DELETE"])
def premium_delete_url(url_id):
    api_key = request.args.get("api_key")
    if api_key == "PremiumTopSecretAPIKey":
        url = db.session.query(PremiumUrls).get(url_id)
        if url:
            db.session.delete(url)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the URL from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a URL with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(port=5000, debug=True)
