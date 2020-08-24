import os
from apps import create_app
from apps.models import db, User, Production, Product_type, Customer, Identifier, Identifier_type, Adress, Change_record, Iid, Pt_i, Repair_record
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Production=Production, Product_type=Product_type, Customer=Customer,
                Identifier=Identifier, Identifier_type=Identifier_type, Adress=Adress, Change_record=Change_record, Iid=Iid, Pt_i=Pt_i, Repair_record=Repair_record)

if __name__ == 'main':
    app.run()