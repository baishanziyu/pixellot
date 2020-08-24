from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from . import authentication
from ..models import db, User, Production, Product_type, Customer, Identifier, Identifier_type, Adress, Change_record, Iid, Pt_i, Repair_record


@main.app_context_processor
def inject_permissions():
        return dict(db=db, User=User, Production=Production, Product_type=Product_type, Customer=Customer,
                    Identifier=Identifier, Identifier_type=Identifier_type, Adress=Adress, Change_record=Change_record,
                    Iid=Iid, Pt_i=Pt_i, Repair_record=Repair_record)
