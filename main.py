from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sqlalchemy_utils
from random import choice

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return f'<Cafe {self.name}>'

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


if not sqlalchemy_utils.functions.database_exists('sqlite:///cafes.db'):
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

@app.route("/api/V1/cafes/random")
def get_random_cafe():
    cafes_list = db.session.query(Cafe).all()
    random_cafe = choice(cafes_list)
    return jsonify(cafe=random_cafe.to_dict()), 200


@app.route("/api/V1/cafes/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    cafes = []
    for cafe in all_cafes:
        cafes.append(cafe.to_dict())
    return jsonify(cafes=cafes), 200


@app.route("/api/V1/cafes/search")
def get_cafes_according_to_location():
    requested_location = request.args.get("loc")
    all_cafes_in_location = db.session.query(Cafe).filter(Cafe.location.like(f"%{requested_location}%")).all()
    if all_cafes_in_location:
        cafes = []
        for cafe in all_cafes_in_location:
            cafes.append(cafe.to_dict())
        return jsonify(cafes=cafes), 200
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"}), 404


# HTTP POST - Create Record

@app.route("/api/V1/cafes/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        has_sockets=bool(request.form.get("sockets")),
        can_take_calls=bool(request.form.get("calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added a new cafe"}), 200


# HTTP PUT/PATCH - Update Record

@app.route("/api/V1/cafes/update-price/<int:cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    new_price = request.args.get("new_price")
    requested_cafe = Cafe.query.get(cafe_id)
    if requested_cafe:
        requested_cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the coffee price"), 200
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record

@app.route("/api/V1/cafes/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="The cafe was deleted successfully"), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database"}), 404
    return jsonify(error="Sorry, that's not allowed. make sure you have the correct api_key"), 403


if __name__ == '__main__':
    app.run(debug=True)
