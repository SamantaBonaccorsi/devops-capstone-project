"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  python -m pip install pytest
  python -m pip install fastapi starlette
"""
import os
import logging
import unittest
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.INFO)

        logging.basicConfig(level=logging.INFO)
        init_db(app)
        
    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  T E S T S
    ######################################################################

    def test_bad_request(self):
        """It should return error 400 Bad Request"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
  
    def test_read_account_not_found(self):
        """If no account found It should return HTTP_404_NOT_FOUND"""
        # try to read
        response = self.client.get(f"{BASE_URL}/{999999}")
        logging.info(f"Test test_read_account_not_found {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)     
 
    def test_update_account_not_found(self):
        """It should fail with HTTP_404_NOT_FOUND status"""
        # l’oggetto con un certo ID non è presente nel database.
        accounts = self._create_accounts(1)
        response = self.client.put(
            f"{BASE_URL}/{9999999}",
            json=accounts[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_not_exists(self):  
        """It should return HTTP_404_NOT_FOUND """
        logging.info(f"Id da eliminare: {9999999}")
        response = self.client.delete(
            f"{BASE_URL}/{999999}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_method_not_allowed(self):
        """ It should return HTTP_405_METHOD_NOT_ALLOWED """
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
