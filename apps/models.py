import pymysql
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

pymysql.install_as_MySQLdb()

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, autoincrement=True, unique=True, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

#    change_records = db.relationship('Change_record', backref='change_records')

    @property
    def password(self):
        raise AttributeError('尚未设置密码')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=108000):
        s = Serializer('default', expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    def cancel_auth_token(self, expiration=108000):
        s = Serializer('default', expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('default')
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        records = []
        if Change_record.query.filter_by(change_userid=self.id).all():
            records = Change_record.query.filter_by(change_userid=self.id).all()
        json_user = {
            'id': self.id,
            'username': self.username,
            'change_records': [ record.change_description for record in records]
        }
        return json_user

class Repair_record(db.Model):
    __tablename__ = 'repair_records'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    content = db.Column(db.Text)
    production_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Repair_record %r>' % self.content

    def to_json(self):
        production_name = None
        if self.production_id:
            production_name = Production.query.filter_by(id=self.production_id).first().name
        json_repair_record = {
            'id': self.id,
            'content': self.content,
            'production_id' : self.production_id,
            'production_name': production_name
        }
        return json_repair_record

class Production(db.Model):
    __tablename__ = 'productions'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=True)
    count = db.Column(db.Integer)
    date_in = db.Column(db.DateTime)
    date_out = db.Column(db.DateTime)
    location = db.Column(db.String(128))

    product_type_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)

#    repair_records = db.relationship('Repair_record', backref='repair_records')
#    iids = db.relationship('Iid', backref='pids')

    def __repr__(self):
        return '<Production %r>' % self.name

    def to_json(self):
        product_type = None
        customer_name = None
        iids = []
        repair_records = []
        if self.product_type_id:
            product_type = Product_type.query.filter_by(id=self.product_type_id).first().name
        if self.customer_id:
            customer_name = Customer.query.filter_by(id=self.customer_id).first().customer_name
        if Repair_record.query.filter_by(production_id=self.id).all():
            repair_records = Repair_record.query.filter_by(production_id=self.id).all()
        if Iid.query.filter_by(production_id=self.id).all():
            iids = Iid.query.filter_by(production_id=self.id).all()
        json_production = {
            'id': self.id,
            'name': self.name,
            'count': self.count,
            'date_in':  str(self.date_in)[0:10],
            'date_out': str(self.date_out)[0:10],
            'location': self.location,
            'product_type': product_type,
            'customer': customer_name,
            'records': [{'record_id':record.id, 'record_content': record.content} for record in repair_records],
            'iids': [{'iid_id':iid.identifier_id, 'iid_name':Identifier.query.filter_by(id=iid.identifier_id).first().item, 'iid_product_id':iid.product_id, 'iid_serial_number':iid.serial_number} for iid in iids]
        }
        return json_production

class Pt_i(db.Model):
    __tablename__ = 'pt_is'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)

    identifier_id = db.Column(db.Integer)
    product_type_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Pt_i %r>' % self.id

    def to_json(self):
        identifier_name = None
        product_type_name = None
        if self.identifier_id:
            identifier_name = Identifier.query.filter_by(id=self.identifier_id).first().item
        if self.product_type_id:
            product_type_name = Product_type.query.filter_by(id=self.product_type_id).first().name
        json_pt_i = {
            'id': self.id,
            'identifier_name': identifier_name,
            'product_type_name': product_type_name

        }
        return json_pt_i

class Product_type(db.Model):
    __tablename__ = 'product_types'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(64))

    #productions = db.relationship('Production', backref='product_type')
    #pt_is = db.relationship('Pt_i', backref='pt_i')


    def __repr__(self):
        return '<Product_type %r>' % self.name

    def to_json(self):
        productions = []
        pt_is= []
        if Production.query.filter_by(product_type_id=self.id).all():
            productions = Production.query.filter_by(product_type_id=self.id).all()
        if Pt_i.query.filter_by(product_type_id=self.id).all():
            pt_is = Pt_i.query.filter_by(product_type_id=self.id).all()
        json_product_type = {
            'id': self.id,
            'name': self.name,
            'productions': [{'id':production.id, 'name':production.name} for production in productions],
            'pt_is': [{'id':pt_i.id,'name':Identifier.query.filter_by(id=pt_i.identifier_id).first().item} for pt_i in pt_is]

        }
        return json_product_type

class Iid(db.Model):
    __tablename__ = 'iids'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    product_id = db.Column(db.String(64), nullable=True)
    serial_number = db.Column(db.String(64), nullable=True)

    production_id = db.Column(db.Integer)
    identifier_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Iid%r>' % self.product_id

    def to_json(self):
        identifier_name = None
        identifier_type = None
        production_name = None
        production_type = None
        if self.identifier_id:
            identifier_name = Identifier.query.filter_by(id=self.id).first().item
            identifier_type = None
            if Identifier.query.filter_by(id=self.identifier_id).first().identifier_type_id:
                identifier_type = Identifier_type.query.filter_by(id=Identifier.query.filter_by(id=self.identifier_id).first().identifier_type_id).first().name
        if self.production_id:
            production_name = Production.query.filter_by(id=self.production_id).first().name
            production_type = None
            if Production.query.filter_by(id=self.production_id).first().product_type_id:
                production_type = Product_type.query.filter_by(id=Production.query.filter_by(id=self.production_id).first().product_type_id).first().name
        json_iid= {
            'id': self.id,
            'product_id': self.product_id,
            'serial_number': self.serial_number,
            'identifier_name': identifier_name,
            'identifier_type': identifier_type,
            'production_name': production_name,
            'production_type': production_type
        }
        return json_iid

class Identifier(db.Model):
    __tablename__ = 'identifiers'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    item = db.Column(db.String(64), nullable=False)

    identifier_type_id = db.Column(db.Integer)

    #iids =  db.relationship('Iid', backref='iids')
    #pt_is = db.relationship('Pt_i', backref='i_pt')

    def __repr__(self):
        return '<Identifier %r>' % self.item

    def to_json(self):
        identifier_type_name = None
        pt_is = []
        iids = []
        if self.identifier_type_id:
            identifier_type_name = Identifier_type.query.filter_by(id=self.identifier_type_id).first().name
        if Iid.query.filter_by(identifier_id=self.id).all():
            iids = Iid.query.filter_by(identifier_id=self.id).all()
        if Pt_i.query.filter_by(identifier_id=self.id).all():
            pt_is = Pt_i.query.filter_by(identifier_id=self.id).all()
        #if Pt_i.query.filter_by(identifier_id=self.id).all():
            #pt_is = Pt_i.query.filter_by(identifier_id=self.id).all()
        json_identifier  = {
            'id': self.id,
            'item': self.item,
            'identifier_type': identifier_type_name,
            'iids': [{'iid.product_id':iid.product_id, 'iid.serial_number':iid.serial_number} for iid in iids],
            'pt_is':[{'id':pt_i.id,'name':Product_type.query.filter_by(id=pt_i.product_type_id).first().name} for pt_i in pt_is]
            ##pt_i的id, product_type的name
        }
        return json_identifier


class Identifier_type(db.Model):
    __tablename__ = 'identifier_types'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(64))

    #identifiers = db.relationship('Identifier', backref='identifier_type')

    def __repr__(self):
        return '<Identifier_type %r>' % self.name

    def to_json(self):
        identifiers = []
        if Identifier.query.filter_by(identifier_type_id=self.id).all():
            identifiers = Identifier.query.filter_by(identifier_type_id=self.id).all()
        json_identifier_type  = {
            'id': self.id,
            'name': self.name,
            'identifiers': [{'id':identifier.id,'item':identifier.item} for identifier in identifiers]
        }
        return json_identifier_type

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    customer_name = db.Column(db.String(64))
    contacts= db.Column(db.String(64))
    phone = db.Column(db.String(64))

    adress_id = db.Column(db.Integer)
    #productions = db.relationship('Production', backref='bought')

    def __repr__(self):
        return '<Customer %r>' % self.customer_name

    def to_json(self):
        adress_name = None
        f_adress_name =None
        adress_adcode = None
        f_adress_adcode=None
        productions = []
        if self.adress_id:
            adress_name = Adress.query.filter_by(id=self.adress_id).first().name
            adress_adcode = Adress.query.filter_by(id=self.adress_id).first().adcode
            f_adress_adcode = Adress.query.filter_by(id=self.adress_id).first().adcode - Adress.query.filter_by(id=self.adress_id).first().adcode%10000
            f_adress_name= Adress.query.filter_by(adcode=f_adress_adcode).first().name
        if Production.query.filter_by(customer_id=self.id).all():
            productions = Production.query.filter_by(customer_id=self.id).all()

        json_customer = {
            'id': self.id,
            'customer_name': self.customer_name,
            'contacts': self.contacts,
            'phone': self.phone,
            'f_adress': {'adcode': f_adress_adcode, 'name': f_adress_name},
            'adress': {'adcode': adress_adcode, 'name': adress_name},
            'productions': [{'id': production.id, 'name': production.name} for production in productions]
        }
        return json_customer

class Adress(db.Model):
    __tablename__ = 'adress'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    adcode = db.Column(db.Integer, nullable=False, unique=True)
    #customers = db.relationship('Customer', backref='customer')

    def __repr__(self):
        return '<adress %r>' % self.name

    def to_json(self):
        json_adress  = {
            'name': self.name,
            'adcode': self.adcode
        }
        return json_adress

class Change_record(db.Model):
    __tablename__ = 'change_record'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    change_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_description = db.Column(db.Text, nullable=False)

    change_userid = db.Column(db.Integer)

    def __repr__(self):
        return '<change_record %r>' % self.change_description

    def to_json(self):
        change_userid = None
        if self.change_userid:
            change_userid = User.query.filter_by(id=self.change_userid).first().username
        json_change_record  = {
            'id': self.id,
            'change_user': change_userid,
            'change_time': str(self.change_time),
            'change_description': self.change_description
        }
        return json_change_record
