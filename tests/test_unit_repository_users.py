import unittest
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel
from src.repositories.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)


class TestUserRepositoryUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user_data = UserModel(username="testuser", email="test@example.com", password="securepassword")
        self.default_avatar = "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0"

    async def test_get_user_by_email_found(self):
        user = User(email=self.user_data.email)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=self.user_data.email, db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="notfound@example.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        mock_user = User(
            id=1,
            username=self.user_data.username,
            email=self.user_data.email,
            created_at=datetime.now(),
            avatar=self.default_avatar
        )

        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', mock_user.id))

        created_user = await create_user(body=self.user_data, db=self.session)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(created_user.username, self.user_data.username)
        self.assertEqual(created_user.email, self.user_data.email)
        self.assertEqual(created_user.avatar, self.default_avatar)

        self.session.refresh.assert_called_once()

    async def test_update_token(self):
        user = User(email=self.user_data.email, refresh_token="oldtoken")
        await update_token(user=user, token="newtoken", db=self.session)
        self.assertEqual(user.refresh_token, "newtoken")
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(email=self.user_data.email, confirmed=False)
        self.session.query().filter().first.return_value = user
        await confirmed_email(self.user_data.email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(email=self.user_data.email, avatar="oldurl")
        self.session.query().filter().first.return_value = user
        updated_user = await update_avatar(email=self.user_data.email, url="newurl", db=self.session)
        self.assertEqual(updated_user.avatar, "newurl")
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
