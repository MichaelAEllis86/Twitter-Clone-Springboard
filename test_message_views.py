"""Message View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

# set an environmental variable
# to use a different database for tests

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

#sanity check to make sure we're using the test db and not the production db. If this fails, all of our tests will be writing to the production db, which is very bad.
print("TEST DB:", app.config["SQLALCHEMY_DATABASE_URI"])

#naked createDB's without app context are breaking our tests. Moving this into an app context to fix that issue!!!
with app.app_context():
    db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        self.ctx = app.app_context()
        self.ctx.push()

        # Clean up any existing data and create fresh new clean test data
        User.query.delete()
        Message.query.delete()
        db.session.commit()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
    
    def tearDown(self):
        db.session.rollback()
        self.ctx.pop() # pop the app context at the end of the test case to clean up after ourselves and prevent any potential side effects on other tests!
        return super().tearDown()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello moto"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello moto")
