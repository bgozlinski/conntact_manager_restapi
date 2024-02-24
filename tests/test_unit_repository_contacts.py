import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import User, Contact
from datetime import datetime, timedelta
from src.repositories.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    search_contact,
    get_contacts_with_upcoming_birthdays

)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), ]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = Contact(first_name="John", last_name="Doe", email="john.doe@example.com",
                       phone_number="1234567890", birth_date=datetime.now(), additional_info="Test")
        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock()
        new_contact = await create_contact(body=body, user=self.user, db=self.session)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(new_contact.first_name, body.first_name)
        self.assertEqual(new_contact.last_name, body.last_name)
        self.assertEqual(new_contact.email, body.email)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact = Contact(id=1, user_id=1, first_name="Original")
        updated_data = Contact(first_name="Updated")
        self.session.query().filter().first.return_value = contact
        updated_contact = await update_contact(contact_id=1, body=updated_data, user=self.user, db=self.session)
        self.assertEqual(updated_contact.first_name, updated_data.first_name)
        self.session.commit.assert_called_once()

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=999, body=Contact(first_name="Ghost"), user=self.user, db=self.session)
        self.assertIsNone(result)
        self.session.commit.assert_not_called()

    async def test_search_contact(self):
        matching_contacts = [Contact(first_name="John"), Contact(first_name="Johnny")]
        self.session.query().filter().all.return_value = matching_contacts

        result = await search_contact(query="John", db=self.session)
        self.assertEqual(len(result), 2)
        for contact in result:
            self.assertIn("John", contact.first_name)

    async def test_get_contacts_with_upcoming_birthdays(self):
        birthday_contact = Contact(birth_date=datetime.now() + timedelta(days=5))
        self.session.query().filter().all.return_value = [birthday_contact]

        result = await get_contacts_with_upcoming_birthdays(db=self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], birthday_contact)


if __name__ == '__main__':
    unittest.main()