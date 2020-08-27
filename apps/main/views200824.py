from flask import jsonify, g, request
from . import main
from ..models import db, User, Customer, Production, Product_type, Identifier_type,\
    Iid, Identifier, Change_record, Repair_record, Adress, Pt_i

##数据展示
@main.route('/users/', methods=['GET', 'POST'])
def users():
    users = User.query.all()
    return jsonify({'users' : [user.to_json() for user in users]})

@main.route('/productions/', methods=['GET', 'POST'])
def productions():
    customers = Customer.query.all()
    productions = Production.query.all()
    product_types = Product_type.query.all()
    return jsonify({'productions' : [production.to_json() for production in productions], 'product_types' : [product_type.to_json() for product_type in product_types], 'customers' : [customer.to_json() for customer in customers]})

@main.route('/product_types/', methods=['GET', 'POST'])
def product_types():
    product_types = Product_type.query.all()
    identifiers = Identifier.query.all()
    productions = Production.query.filter(Production.product_type_id.is_(None)).all()
    return jsonify({'product_types' : [product_type.to_json() for product_type in product_types], 'identifiers': [identifier.to_json() for identifier in identifiers],'productions': [production.to_json() for production in productions]})

@main.route('/identifier_types/', methods=['GET', 'POST'])
def identifier_types():
    identifier_types = Identifier_type.query.all()
    identifiers = Identifier.query.all()
    return jsonify({'identifier_types' : [identifier_type.to_json() for identifier_type in identifier_types],'identifiers': [identifier.to_json() for identifier in identifiers]})

@main.route('/iids/', methods=['GET', 'POST'])
def iids():
    productions = Production.query.all()
    iids = Iid.query.all()
    identifiers = Identifier.query.all()
    pt_is = Pt_i.query.all()
    return jsonify({'pt_is' : [pt_i.to_json() for pt_i in pt_is], 'productions' : [production.to_json() for production in productions], 'identifiers' : [identifier.to_json() for identifier in identifiers], 'iids' : [iid.to_json() for iid in iids]})

@main.route('/identifiers/', methods=['GET', 'POST'])
def identifiers():
    identifier_types = Identifier_type.query.all()
    identifiers = Identifier.query.all()
    product_types = Product_type.query.all()
    return jsonify({'product_types' : [product_type.to_json() for product_type in product_types], 'identifier_types' : [identifier_type.to_json() for identifier_type in identifier_types],'identifiers' : [identifier.to_json() for identifier in identifiers]})

@main.route('/customers/', methods=['GET', 'POST'])
def customers():
    productions = Production.query.filter(Production.customer_id.is_(None)).all()
    customers = Customer.query.all()
    first_adress = Adress.query.filter(Adress.adcode%10000==0)
    second_adress = Adress.query.all()
    return jsonify({'productions' : [production.to_json() for production in productions],
                    'customers' : [customer.to_json() for customer in customers],
                    'first_adress':[first.to_json() for first in first_adress],
                    'second_adress':[second.to_json() for second in second_adress]
                    })

@main.route('/change_records/', methods=['GET', 'POST'])
def change_records():
    change_records = Change_record.query.all()
    return jsonify({'change_records' : [change_record.to_json() for change_record in change_records]})

##数据编辑
@main.route('/production_edit/', methods=['GET', 'POST'])
def production_edit():
    item = request.get_json(silent=True)
    if not item:
        return 'production_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='产品信息更改')
    db.session.add(change_record)
    db.session.commit()

    production_id = item.get('production_id')
    production = Production().query.filter_by(id=production_id).first()

    production.name = item.get('production_name')
    production.count = item.get('production_count')
    production.date_in = item.get('production_date_in')
    production.date_out = item.get('production_date_out')
    production.location = item.get('production_location')
    cus = Customer().query.filter_by(customer_name=item.get('production_customer')).first()
    if cus:
        production.customer_id = cus.id
    production.product_type_id = Product_type().query.filter_by(name=item.get('production_type')).first().id
    db.session.add(production)
    db.session.commit()

    for production_repair_record in item.get('production_repair_record'):
        if not production_repair_record.get('record_id'):
            re = Repair_record(content=production_repair_record.get('record_content'),production_id=production.id)
            db.session.add(re)
            db.session.commit()
        else:
            repair_record = Repair_record().query.filter_by(id=production_repair_record.get('record_id')).first()
            repair_record.content = production_repair_record.get('record_content')
            db.session.add(repair_record)
            db.session.commit()
    for production_iid in item.get('production_iids'):
        if not production_iid.get('iid_id'):
            iid = Iid(production_id=production.id,product_id=production_iid.get('iid_product_id'),serial_number=production_iid.get('iid_serial_number'),identifier_id=Identifier().query.filter_by(item=production_iid.get('iid_name')).first().id)
            db.session.add(iid)
            db.session.commit()
        else:
            iid = Iid().query.filter_by(id=production_iid.get('iid_id')).first()
            iid.product_id = production_iid.get('iid_product_id')
            iid.serial_number = production_iid.get('iid_serial_number')
            iid.identifier_id = Identifier().query.filter_by(item=production_iid.get('iid_name')).first().id
            db.session.add(iid)
            db.session.commit()
    return 'production_edit susses!'

@main.route('/product_type_edit/', methods=['POST'])
def product_type_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'product_type_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='产品类型更改')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    type = Product_type.query.filter_by(id=item.get('id')).first()
    if not type:
        return 'product_type_edit error!'
    type.name = item.get('name')
    db.session.add(type)
    db.session.commit()
    productions = item.get('productions')
    for p in productions:
        if (not p.get('id')) and p.get('name'):
            production = Production.query.filter_by(name=p.get('name')).first()
            if production:
                production.product_type_id = type.id
                db.session.add(production)
                db.session.commit()
    pt_is = item.get('pt_is')
    for pt in pt_is:
        if (not pt.get('id')) and pt.get('name'):
            identifier = Identifier.query.filter_by(item=pt.get('name')).first()
            if identifier:
                if not Pt_i.query.filter_by(product_type_id=type.id, identifier_id=identifier.id).first():
                    pt_i = Pt_i(product_type_id=type.id, identifier_id=identifier.id)
                    db.session.add(pt_i)
                    db.session.commit()
    return 'product_type_edit susses!'

@main.route('/identifier_edit/', methods=['POST'])
def identifier_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件更改')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    id = item.get('id')
    identifier_name= item.get('identifier_name')
    type = item.get('production_type')
    production_name = item.get('production_name')
    product_id = item.get('product_id')
    serial_number = item.get('serial_number')

    identifier = Identifier.query.filter_by(item=identifier_name).first()
    production = Production.query.filter_by(name=production_name).first()
    product_type = Product_type.query.filter_by(name=type).first()
    production.product_type_id = product_type.id
    db.session.add(production)
    db.session.commit()
    iid = Iid.query.filter_by(id=id).first()
    iid.product_id = product_id
    iid.serial_number = serial_number
    iid.identifier_id = identifier.id
    iid.production_id = production.id
    db.session.add(iid)
    db.session.commit()
    return 'identifier_edit susses!'

@main.route('/identifier_name_edit/', methods=['POST'])
def identifier_name_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_name_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件名称编辑')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    id = item.get('id')
    identifier_type = item.get('identifier_type')
    name = item.get('item')
    pt_is = item.get('pt_is')
    identifier = Identifier.query.filter_by(id=id).first()
    if not identifier:
        return 'identifier_name_edit error cause no identifier!'
    type = Identifier_type.query.filter_by(name=identifier_type).first()
    identifier.item = name
    identifier.identifier_type_id = type.id
    db.session.add(identifier)
    db.session.commit()
    for pt in pt_is:
        if (not pt.get('id')) and pt.get('name'):
            p_type = Product_type.query.filter_by(name=pt.get('name')).first()
            if not Pt_i.query.filter_by(product_type_id=p_type.id,identifier_id=identifier.id).first():
                pt_i = Pt_i(product_type_id=p_type.id,identifier_id=identifier.id)
                db.session.add(pt_i)
                db.session.commit()
    return 'identifier_name_edit susses!'

@main.route('/identifier_type_edit/', methods=['POST'])
def identifier_type_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_type_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件类别更改')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    id = item.get('id')
    name = item.get('name')
    identifiers = item.get('identifiers')
    i_type = Identifier_type.query.filter_by(id=id).first()
    i_type.name = name
    db.session.add(i_type)
    db.session.commit()
    for one in identifiers:
        if (not one.get('id')) and one.get('item'):
            if not Identifier.query.filter_by(item=one.get('item'), identifier_type_id=i_type.id).first():
                identifier = Identifier.query.filter_by(item=one.get('item')).first()
                if identifier:
                    identifier.identifier_type_id = i_type.id
                else:
                    identifier = Identifier(item=one.get('item'), identifier_type_id=i_type.id)
                db.session.add(identifier)
                db.session.commit()
    return 'identifier_type_edit susses!'

@main.route('/customer_edit/', methods=['POST'])
def customer_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'customer_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='客户信息修改')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    id = item.get('id')
    customer_name = item.get('customer_name')
    adress = Adress.query.filter_by(adcode=item.get('adress').get('adcode')).first()
    contacts = item.get('contacts')
    phone = item.get('phone')
    productions = item.get('productions')
    customer = Customer.query.filter_by(id=id).first()
    customer.customer_name = customer_name
    customer.contacts = contacts
    customer.phone = phone
    if adress:
        customer.adress_id = adress.id
    else:
        customer.adress_id = None
    db.session.add(customer)
    db.session.commit()
    for pr in productions:
        if (not pr.get('id')) and pr.get('name'):
            production = Production.query.filter_by(name=pr.get('name')).first()
            production.customer_id = customer.id
            db.session.add(production)
            db.session.commit()
    return 'customer_edit susses!'

@main.route('/account_edit/', methods=['POST'])
def account_edit():
    items = request.get_json(silent=True)
    if not items:
        return 'account_edit change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='账号修改')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    if item.get('username'):
        user = User.query.filter_by(id=item.get('id')).first()
        user.username = item.get('username')
        db.session.add(user)
        db.session.commit()
    return 'account_edit susses!'


##数据新增
@main.route('/production_add/', methods=['GET', 'POST'])
def production_add():
    item = request.get_json(silent=True)
    if not item:
        return 'production_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='产品信息新增')
    db.session.add(change_record)
    db.session.commit()

    name = item.get('production_name')
    count = item.get('production_count')
    date_in = item.get('production_date_in')
    date_out = item.get('production_date_out')
    location = item.get('production_location')
    iids = item.get('production_iids')
    repair_records = item.get('production_repair_record')
    ty = Product_type.query.filter_by(name = item.get('production_type')).first()
    customer= Customer.query.filter_by(customer_name = item.get('production_customer')).first()

    if name:
        production = Production(name=name, count=count, date_in=date_in, date_out=date_out, location=location)
        if ty:
            production.product_type_id = ty.id
        if customer:
            production.customer_id = customer.id
        db.session.add(production)
        db.session.commit()

        if repair_records:
            for rr in repair_records:
                repair_record = Repair_record(content=rr.record_content, production_id=production.id)
                db.session.add(repair_record)
                db.session.commit()
        if iids:
            for one in iids:
                identifier = Identifier.query.filter_by(item=one.iid_name).first()
                iid = Iid(product_id=one.iid_product_id, serial_number=one.iid_serial_number, identifier_id=identifier.id, production_id=production.id)
                db.session.add(iid)
                db.session.commit()
    return 'production_add susses!'

@main.route('/product_type_add/', methods=['POST'])
def product_type_add():
    items = request.get_json(silent=True)
    if not items:
        return 'product_type_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='产品类型新增')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    if not item.get('name'):
        return 'product_type_add change error cause no name!'
    type = Product_type(name=item.get('name'))
    db.session.add(type)
    db.session.commit()
    productions = item.get('productions')
    for p in productions:
        if (not p.get('id')) and p.get('name'):
            production = Production.query.filter_by(name=p.name).first()
            if production:
                production.product_type_id = type.id
                db.session.add(production)
                db.session.commit()
    pt_is = item.get('pt_is')
    for pt in pt_is:
        if (not pt.get('id')) and pt.get('name'):
            identifier = Identifier.query.filter_by(item=pt.name).first()
            if identifier:
                if not Pt_i.query.filter_by(product_type_id=type.id, identifier_id=identifier.id).first():
                    pt_i = Pt_i(product_type_id=type.id, identifier_id=identifier.id)
                    db.session.add(pt_i)
                    db.session.commit()
    return 'product_type_add susses!'

@main.route('/identifier_add/', methods=['POST'])
def identifier_add():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件新增')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    identifier_name = item.get('identifier_name')
    type = item.get('production_type')
    production_name = item.get('production_name')
    product_id = item.get('product_id')
    serial_number = item.get('serial_number')

    identifier = Identifier.query.filter_by(item=identifier_name).first()
    production = Production.query.filter_by(name=production_name).first()
    product_type = Product_type.query.filter_by(name=type).first()
    production.product_type_id = product_type.id
    db.session.add(production)
    db.session.commit()
    if identifier_name:
        if not Iid.query.filter_by(product_id = product_id,serial_number = serial_number,identifier_id = identifier.id,production_id = production.id).first():
            iid = Iid(product_id = product_id,serial_number = serial_number,identifier_id = identifier.id,production_id = production.id)
            db.session.add(iid)
            db.session.commit()
    return 'identifier_add susses!'

@main.route('/identifier_name_add/', methods=['POST'])
def identifier_name_add():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_name_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件名称新增')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    identifier_type = item.get('identifier_type')
    name = item.get('item')
    pt_is = item.get('pt_is')
    type = Identifier_type.query.filter_by(name=identifier_type).first()
    if not Identifier.query.filter_by(item=name).first():
        identifier = Identifier(item=name, identifier_type_id = type.id)
        db.session.add(identifier)
        db.session.commit()
    for pt in pt_is:
        if (not pt.get('id')) and pt.get('name'):
            p_type = Product_type.query.filter_by(name=pt.get('name')).first()
            if not Pt_i.query.filter_by(product_type_id=p_type.id, identifier_id=identifier.id).first():
                pt_i = Pt_i(product_type_id=p_type.id, identifier_id=identifier.id)
                db.session.add(pt_i)
                db.session.commit()
    return 'identifier_name_add susses!'

@main.route('/identifier_type_add/', methods=['POST'])
def identifier_type_add():
    items = request.get_json(silent=True)
    if not items:
        return 'identifier_type_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='组件类型新增')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    name = item.get('name')
    identifiers = item.get('identifiers')
    if not Identifier_type.query.filter_by(name=name):
        i_type = Identifier_type(name = name)
        db.session.add(i_type)
        db.session.commit()
        for one in identifiers:
            if (not one.get('id')) and one.get('item'):
                if not Identifier.query.filter_by(item=one.get('item'), identifier_type_id=i_type.id).first():
                    identifier = Identifier.query.filter_by(item=one.get('item')).first()
                    if identifier:
                        identifier.identifier_type_id = i_type.id
                    else:
                        identifier = Identifier(item=one.get('item'), identifier_type_id=i_type.id)
                    db.session.add(identifier)
                    db.session.commit()
    return 'identifier_type_add susses!'

@main.route('/customer_add/', methods=['POST'])
def customer_add():
    items = request.get_json(silent=True)
    if not items:
        return 'customer_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='客户信息新增')
    db.session.add(change_record)
    db.session.commit()

    item = items.get('item')
    customer_name = item.get('customer_name')
    adress = Adress.query.filter_by(adcode=item.get('adress').get('adcode')).first()
    contact = item.get('contact')
    phone = item.get('phone')
    productions = item.get('productions')
    if customer_name:
        if adress:
            customer = Customer(customer_name=customer_name, contacts=contact, phone=phone, adress_id=adress.id)
        else:
            customer = Customer(customer_name=customer_name, contacts=contact, phone=phone)
        db.session.add(customer)
        db.session.commit()
        for pr in productions:
            if (not pr.get('id')) and pr.get('name'):
                production = Production.query.filter_by(name=pr.get('name')).first()
                production.customer_id = customer.id
                db.session.add(production)
                db.session.commit()
    return 'customer_add susses!'

@main.route('/account_add/', methods=['POST'])
def account_add():
    items = request.get_json(silent=True)
    if not items:
        return 'account_add change error!'
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='账号新增')
    db.session.add(change_record)
    db.session.commit()

    one = User.query.filter_by(username=items.get('username')).first()
    if (not one) and items.get('username') and items.get('password'):
        user = User(username = items.get('username'), password = items.get('password'))
        db.session.add(user)
        db.session.commit()
    return 'account_add susses!'


##数据删除
@main.route('/record_delete/', methods=['POST'])
def record_delete():
    items = request.get_json(silent=True)
    if not items:
        return 'record_delete error!'
    record_id = items.get('record_id')
    record = Repair_record.query.filter_by(id=record_id).first()
    if record:
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='维修记录删除:id:' + str(items.get('record_id')))
        db.session.add(change_record)
        db.session.delete(record)
        db.session.commit()
    return 'record_delete susses!'

@main.route('/iid_delete/', methods=['POST'])
def iid_delete():
    items = request.get_json(silent=True)
    if not items:
        return 'iid_delete error!'
    iid_id = items.get('iid_id')
    iid = Iid.query.filter_by(id=iid_id).first()
    if iid:
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='组件详情删除:id:' + str(items.get('iid_id')))
        db.session.add(change_record)
        db.session.delete(iid)
        db.session.commit()
    return 'iid_delete susses!'

@main.route('/pt_i_delete/', methods=['POST'])
def pt_i_delete():
    items = request.get_json(silent=True)
    if not items:
        return 'pt_i_delete error!'
    pt_i_id = items.get('pt_i_id')
    pt_i = Pt_i.query.filter_by(id=pt_i_id).first()
    print(pt_i_id)
    if pt_i:
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='组件_产品类型删除:id:' + str(items.get('pt_i_id')))
        db.session.add(change_record)
        db.session.delete(pt_i)
        db.session.commit()
    return 'pt_i_delete susses!'

##关系清除
@main.route('/p_pt_clear/', methods=['POST'])
def p_pt_clear():
    items = request.get_json(silent=True)
    if not items:
        return 'p_pt_clear error!'
    p_pt_id = items.get('p_pt_id')
    production = Production.query.filter_by(id=p_pt_id).first()
    if production:
        production.product_type_id = None
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='组件_产品类型清除:id:' + str(items.get('pt_i_id')))
        db.session.add(change_record)
        db.session.add(production)
        db.session.commit()
    return 'p_pt_clear susses!'

@main.route('/i_it_clear/', methods=['POST'])
def i_it_clear():
    items = request.get_json(silent=True)
    if not items:
        return 'i_it_clear error!'
    i_it_id = items.get('i_it_id')
    identifier = Identifier.query.filter_by(id=i_it_id).first()
    if identifier:
        identifier.identifier_type_id = None
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='组件_组件类型清除:id:' + str(items.get('i_it_id')))
        db.session.add(change_record)
        db.session.add(identifier)
        db.session.commit()
    return 'i_it_clear susses!'

@main.route('/p_c_clear/', methods=['POST'])
def p_c_clear():
    items = request.get_json(silent=True)
    if not items:
        return 'p_c_clear error!'
    p_c_id = items.get('p_c_id')
    production = Production.query.filter_by(id=p_c_id).first()
    if production:
        production.customer_id = None
        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='客户_产品清除:id:' + str(items.get('p_c_id')))
        db.session.add(change_record)
        db.session.add(production)
        db.session.commit()
    return 'p_c_clear susses!'

##page_delete
@main.route('/production_drop/<int:production_id>', methods=['POST'])
def production_drop(production_id):
    production = Production.query.filter_by(id=production_id).first()
    if production:
        iid = Iid.query.filter_by(production_id=production_id).first()
        repair_record = Repair_record.query.filter_by(production_id=production_id).first()
        if iid:
            iid.production_id = None
            db.session.add(iid)

        if repair_record:
            db.session.delete(repair_record)

        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='删除设备:id:' + str(production_id))

        db.session.add(change_record)
        db.session.delete(production)
        db.session.commit()

@main.route('/product_type_drop/<int:ptoduct_type_id>', methods=['POST'])
def product_type_drop(product_type_id):
    product_type = Product_type.query.filter_by(id=product_type_id).first()
    production = Production.query.filter_by(product_type_id=product_type_id).first()
    pt_i = Pt_i.query.filter_by(product_type_id=product_type_id).first()

    if product_type:
        db.session.delete(product_type)

    if production:
        production.product_type_id = None
        db.session.add(production)

    if pt_i:
        db.session.delete(pt_i)
    
    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='删除设备类型:id:' + str(product_type_id))

    db.session.add(change_record)
    db.session.commit()

@main.route('/identifier_drop/<int:identifier_id>', methods=['POST'])
def identifier_drop(identifier_id):
    identifier = Identifier.query.filter_by(id=identifier_id).first()
    pt_i = Pt_i.query.filter_by(identifier_id=identifier_id).first()

    iid = Iid.query.filter_by(identifier_id=identifier_id).first()

    if identifier:
        db.session.delete(identifier)
    
    if pt_i:
        db.session.delete(pt_i)

    if iid:
        iid.identifier_id = None
        db.session.add(iid)

    user = g.current_user
    change_record = Change_record(change_userid=user.id, change_description='删除组件名称:' + str(identifier.item))

    db.session.add(change_record)
    db.session.commit()

@main.route('/identifier_type_drop/<int:identifier_type_id>', methods=['POST'])
def identifier_type_drop(identifier_type_id):
    identifier_type = Identifier_type.query.filter_by(id=identifier_type_id).first()
           
    identifier= Identifier.query.filter_by(identifier_type_id=identifier_type_id).first()

    if identifier_type:
        db.session.delete(identifier_type)

    if identifier:
        identifier.identifier_type_id = None
        db.session.add(identifier)

        user = g.current_user
        change_record = Change_record(change_userid=user.id, change_description='删除组件类型:id:' + str(identifier_type_id))

        db.session.add(change_record)
        db.session.commit()

