"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db, app
from models import User, Message, Follows


# moved all of Springboard's code below into a with application context. None of this db code will work without flask app context. 
with app.app_context():
    db.drop_all()
    db.create_all()
    with open('generator/users.csv') as users:
        db.session.bulk_insert_mappings(User, DictReader(users))

    with open('generator/messages.csv') as messages:
        db.session.bulk_insert_mappings(Message, DictReader(messages))
    
    with open('generator/follows.csv') as follows:
        db.session.bulk_insert_mappings(Follows, DictReader(follows))

    db.session.commit()
