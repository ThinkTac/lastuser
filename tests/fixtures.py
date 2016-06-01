# -*- coding: utf-8 -*-

from lastuserapp import db
from lastuser_core.models import *


def make_fixtures():
    user1 = User(username=u"user1", fullname=u"User 1")
    user2 = User(username=u"user2", fullname=u"User 2")
    db.session.add_all([user1, user2])

    email1 = UserEmail(email=u"user1@example.com", user=user1)
    phone1 = UserPhone(phone=u"1234567890", user=user1)
    email2 = UserEmail(email=u"user2@example.com", user=user2)
    phone2 = UserPhone(phone=u"1234567891", user=user2)
    db.session.add_all([email1, phone1, email2, phone2])

    org = Organization(name=u"org", title=u"Organization")
    org.owners.users.append(user1)
    db.session.add(org)

    client = Client(title=u"Test Application", org=org, confidential=True, website=u"http://example.com", namespace=u"123.example.com")
    db.session.add(client)

    resource = Resource(name=u"test_resource", title=u"Test Resource", client=client)
    db.session.add(resource)

    action = ResourceAction(name=u"read", title=u"Read", resource=resource)
    db.session.add(action)

    message = SMSMessage(phone_number=phone1.phone, transaction_id=u"1" * 40, message=u"Test message")
    db.session.add(message)

    db.session.commit()
