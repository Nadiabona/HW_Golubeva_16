from flask import Flask, request
import json
from flask_sqlalchemy import SQLAlchemy

import raw_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICASTIONS'] = False #зарезервированная переменная, тут ее лучше отключить

db = SQLAlchemy(app) #создаем базу данных и свызываем с нашим приложением

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    #пишем метод для преобразования json в словарь, чтобы потом писать представление
    #в значения попадают поля из бд
    def to_dict(self):
        return {
            "id": self.id,
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "age" : self.age,
            "email" : self.email,
            "role" : self.role,
            "phone" : self.phone
        }

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    #тип строка чтобы дата везде читалась или можно через секунды и их потом преобразовывать
    start_date = db.Column(db.String(100))
    end_date = db.Column(db.String(100))
    address = db.Column(db.Integer)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id")) #обращаемся к имени самой таблицы на случай замены ее имени
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "name" : self.name,
            "description" : self.description,
            "start_date" : self.start_date,
            "end_date": self.end_date,
            "address" : self.address,
            "customer_id" : self.customer_id,
            "executor_id" : self.executor_id,
        }

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    __tablename__ = "offer"
    user_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id" : self.order_id,
            "executor_id" : self.executor_id,
             }

@app.route("/users", methods = ["GET", "POST"])
def users():
    if request.method == "GET":
        result = []
        for user in User.query.all():
            result.append(user.to_dict())
        return json.dumps(result, indent = 4), 200, {'Content-type':'application/json'}

    if request.method == "POST":
        user_data = json.loads(request.data)  # то, что передаем в запросе, формируется в json
        db.session.add( #так же как добавляли юзера
            User(
                id=user_data.get("id"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                age=user_data.get("age"),
                email=user_data.get("email"),
                role=user_data.get("role"),
                phone=user_data.get("phone"),
                )
        )
        db.session.commit()
        return " ", 201 #возвращать ничего не должен но пустую строку мы должны прописать

@app.route("/users/<int:uid>", methods = ["GET", "PUT", "DELETE"])
def user_uid(uid:int):
    if request.method == "GET":
        return json.dumps(User.query.get(uid).to_dict(), indent = 4), 200, {'Content-type': 'application/json'}

    if request.method == "PUT":
        user_data = json.loads(request.data)
        new_user = User.query.get(uid) #получаем юзера по его айди и далее меняем ему поля

        new_user.first_name = user_data["first_name"] #то есьь мы берем из таблицы поле first name  даем ему данные из запроса
        new_user.last_name = user_data["last_name"]
        new_user.age = user_data["age"]
        new_user.email = user_data["email"]
        new_user.role = user_data["role"]
        new_user.phone = user_data["phone"]

        db.session.add(new_user)
        db.session.commit()
        return "", 201

    if request.method == "DELETE":
        u = User.query.get(uid) # получаем юзерва по его айди

        db.session.delete(u)
        db.session.commit()
        return "", 204



@app.route("/orders", methods = ["GET", "POST"])
def orders():
    if request.method == "GET":
        result = []
        for order in Order.query.all():
            result.append(order.to_dict())
        return json.dumps(result, indent = 4), 200, {'Content-type':'application/json'}

    if request.method == "POST":
        order_data = json.loads(request.data)  # то, что передаем в запросе, формируется в json
        db.session.add(  # так же как добавляли юзера
            Order(
                id = order_data.get("id"),
                name = order_data.get("name"),
                description = order_data.get("description"),
                start_date = order_data.get("start_date"),
                end_date = order_data.get("end_date"),
                address = order_data.get("address"),
                price=order_data.get("price"),
                customer_id = order_data.get("customer_id"),
                executor_id = order_data.get("executor_id"),
            )
        )
        db.session.commit()
        return " ", 201

@app.route("/orders/<int:uid>", methods = ["GET", "PUT", "DELETE"])
def order_uid(uid:int):
    if request.method == "GET":
        return json.dumps(Order.query.get(uid).to_dict(), indent = 4), 200, {'Content-type': 'application/json'}

    if request.method == "PUT":
        order_data = json.loads(request.data)
        new_order = Order.query.get(uid)  # получаем юзера по его айди и далее меняем ему поля

        new_order.name =order_data["name"]
        new_order.description = order_data["description"]
        new_order.start_date = order_data["start_date"]
        new_order.end_date = order_data["end_date"]
        new_order.address = order_data["address"]
        new_order.price = order_data["price"]
        new_order.customer_id = order_data["customer_id"]
        new_order.executor_id = order_data["executor_id"]

        db.session.add(new_order)
        db.session.commit()
        return "", 201

    if request.method == "DELETE":
        ordr = Order.query.get(uid)  # получаем юзерва по его айди

        db.session.delete(ordr)
        db.session.commit()
        return "", 204

@app.route("/offers", methods = ["GET", "POST"])
def offers():
    if request.method == "GET":
        result = []
        for offer in Offer.query.all():
            result.append(offer.to_dict())
        return json.dumps(result, indent = 4), 200, {'Content-type':'application/json'}

    if request.method == "POST":
        offer_data = json.loads(request.data)  # то, что передаем в запросе, формируется в json
        db.session.add(  # так же как добавляли юзера
            Offer(
                id = offer_data.get("id"),
                order_id = offer_data.get("customer_id"),
                executor_id = offer_data.get("executor_id"),

            )
        )
        db.session.commit()
        return " ", 201  # возвращать ничего не должен но пустую строку мы должны прописать

@app.route("/offers/<int:uid>", methods = ["GET", "PUT", "DELETE"])

def offer_uid(uid:int):
    if request.method == "GET":
        return json.dumps(Offer.query.get(uid).to_dict(), indent = 4), 200, {'Content-type': 'application/json'}

    if request.method == "PUT":
        offer_data = json.loads(request.data)
        new_offer = Offer.query.get(uid)  # получаем юзера по его айди и далее меняем ему поля

        new_offer.order_id = offer_data["order_id"]
        new_offer.executor_id = offer_data["executor_id"]

        db.session.add(new_offer)
        db.session.commit()
        return "", 201

    if request.method == "DELETE":
        ofr= Offer.query.get(uid)  # получаем оффер по его айди

        db.session.delete(ofr)
        db.session.commit()
        return "", 204

def init_database():
    for user_data in raw_data.users:
        new_user = User(
            id = user_data.get("id"),
            first_name = user_data.get("first_name"),
            last_name = user_data.get("last_name"),
            age = user_data.get("age"),
            email = user_data.get("email"),
            role = user_data.get("role"),
            phone = user_data.get("phone")
        )
        db.session.add(new_user)
        db.session.commit()

    for order_data in raw_data.orders:
        db.session.add(
            Order (
                id = order_data.get("id"),
                name = order_data.get("name"),
                description = order_data.get("description"),
                start_date = order_data.get("start_date"),
                end_date = order_data.get("end_date"),
                address = order_data.get("address"),
                price = order_data.get("price"),
                customer_id = order_data.get("customer_id"),
                executor_id = order_data.get("executor_id")
              )
        )
        db.session.commit()

    for offer_data in raw_data.offers:
        db.session.add(
            Offer (
                id = offer_data.get("id"),
                user_id = offer_data.get("order_id"),
                executor_id = offer_data.get("executor_id")
              )
        )
        db.session.commit()

with app.app_context():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    with app.app_context():
        init_database()
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
