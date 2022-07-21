from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


# initialized database
def db_init(app):
    db.init_app(app)

    # creates the logs table if db dosent exist
    with app.app_context():
        db.create_all()


# initializes schema
def ma_init(app):
    ma.init_app(app)
