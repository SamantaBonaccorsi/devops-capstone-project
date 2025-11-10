"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
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
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

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

    # ADD YOUR TEST CASES HERE ...

    def test_read_account(self):
        """It should read the account"""
        # create an account
        accounts = self._create_accounts(1)
        account = accounts[0]

        response = self.client.post(
                BASE_URL,
                json = account.serialize(),
                content_type = "application/json"
        )
        # check if account created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account.id = response.get_json()["id"]

        # try to read
        response = self.client.get(f"{BASE_URL}/{account.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_account = account.deserialize(response.get_json())

        logging.info(f"Test read_an_account - Account creato {account.name}")
        logging.info(f"Test read_an_account - Account letto {new_account.name}")
                
        self.assertTrue(
            account.id == new_account.id
            and account.name == new_account.name
            and account.email == new_account.email
            and account.address == new_account.address
            and account.phone_number == new_account.phone_number
            and account.date_joined == new_account.date_joined
        )
    
    def test_read_account_not_found(self):
        """If no account found It should return HTTP_404_NOT_FOUND"""
        # try to read
        response = self.client.get(f"{BASE_URL}/{999999}")
        logging.info(f"Test test_read_account_not_found {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
      
    def test_list_all_account(self):
        """It should list all the accounts created"""
        # create 10 account
        accounts = self._create_accounts(10)
        
        for account in accounts:
            logging.info(f"Test test_list_all_account - Account creato {account.name}")
            response = self.client.post(
                BASE_URL,
                json = account.serialize(),
                content_type = "application/json"
            )
            # check if account created
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
        # try to read
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        account_list = response.get_json()
        logging.info(f"Lunghezza lista {len(account_list)}")
        self.assertTrue(len(account_list) >= 10)
        
    def test_update_account(self):
        """It should Update an Account"""
        accounts = self._create_accounts(1)
        response = self.client.post(
            BASE_URL,
            json=accounts[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Overwrite the account with new data
        # And give it the id of the first account created
        account = AccountFactory()
        account.id = response.get_json()["id"]

        response = self.client.put(
            f"{BASE_URL}/{account.id}",
            json = account.serialize(),
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the data is correct
        new_account = response.get_json()
        logging.info(new_account)
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

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

    def test_delete_account(self):
        """It should Delete an Account"""
        accounts = self._create_accounts(1)
        response = self.client.post(
            BASE_URL,
            json=accounts[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get the id
        id = response.get_json()["id"]
        logging.info(f"Id da eliminare: {id}")
        response = self.client.delete(
            f"{BASE_URL}/{id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_account_not_exists(self):  
        """It should return HTTP_404_NOT_FOUND """
        logging.info(f"Id da eliminare: {9999999}")
        response = self.client.delete(
            f"{BASE_URL}/{999999}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        