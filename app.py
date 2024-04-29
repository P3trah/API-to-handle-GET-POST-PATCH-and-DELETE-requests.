from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bakeries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Bakery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    baked_goods = db.relationship('BakedGood', backref='bakery', lazy=True)

    def __init__(self, name):
        self.name = name

class BakedGood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float)
    bakery_id = db.Column(db.Integer, db.ForeignKey('bakery.id'), nullable=False)

    def __init__(self, name, price, bakery_id):
        self.name = name
        self.price = price
        self.bakery_id = bakery_id

class BakerySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

bakery_schema = BakerySchema()
bakeries_schema = BakerySchema(many=True)

class BakedGoodSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'price', 'bakery_id')

baked_good_schema = BakedGoodSchema()
baked_goods_schema = BakedGoodSchema(many=True)

@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    all_bakeries = Bakery.query.all()
    result = bakeries_schema.dump(all_bakeries)
    return jsonify(result)

@app.route('/baked_goods', methods=['GET'])
def get_baked_goods():
    all_baked_goods = BakedGood.query.all()
    result = baked_goods_schema.dump(all_baked_goods)
    return jsonify(result)

@app.route('/baked_goods', methods=['POST'])
def add_baked_good():
    name = request.form['name']
    price = request.form['price']
    bakery_id = request.form['bakery_id']

    new_baked_good = BakedGood(name, price, bakery_id)
    db.session.add(new_baked_good)
    db.session.commit()

    result = baked_good_schema.dump(new_baked_good)
    return jsonify(result)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    name = request.form['name']

    bakery.name = name
    db.session.commit()

    result = bakery_schema.dump(bakery)
    return jsonify(result)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    db.session.delete(baked_good)
    db.session.commit()

    return jsonify({'message': 'Baked good deleted'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)