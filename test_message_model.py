"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

#sanity check to make sure we're using the test db and not the production db. If this fails, all of our tests will be writing to the production db, which is very bad.
print("TEST DB:", app.config["SQLALCHEMY_DATABASE_URI"])


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        # Keep context for the whole test! app context is breaking down in the middle of tests and causing db.session to fail. This is a workaround to keep the app context alive for the whole test case!!!
        self.ctx = app.app_context()
        self.ctx.push()

        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()
        self.ctx.pop() # pop the app context at the end of the test case to clean up after ourselves and prevent any potential side effects on other tests!
        return super().tearDown()


    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="a warble",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "a warble")

    def test_message_likes(self):
        m1 = Message(text="a warble", user_id=self.uid)
        m2 = Message(text="a very interesting warble", user_id=self.uid)

        u = User.signup("yetanothertest", "t@email.com", "password", None)
        u.id = 888

        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)
        db.session.commit()

        l = Likes.query.filter_by(user_id=u.id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)

        u_fresh = User.query.get(u.id)
        self.assertEqual(len(u_fresh.likes), 1)
        self.assertEqual(u_fresh.likes[0].id, m1.id)

