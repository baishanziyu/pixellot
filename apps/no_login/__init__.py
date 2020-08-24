from flask import Blueprint

no_login = Blueprint('no_login', __name__)


from . import view
from ..models import db, User


@no_login.app_context_processor
def inject_permissions():
        return dict(db=db, User=User)
