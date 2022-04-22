import time
import unittest
import requests


class ApiTest(unittest.TestCase):
    API_URL = 'http://127.0.0.1'
    CREATE_USER_URL = '/create_user'
    LOGIN_USER_URL = '/login'
    GET_ALL_MOVIES_URL = '/get_all_movie_titles'
    GET_MOVIES_CATEGORY_URL = '/get_movies_by_category'
    NAVIGATE_URL = '/navigate'
    RENT_URL = '/rent'
    RETURN_MOVIE_URL = '/return_movie'
    GET_RENTALS_URL = '/get_rentals'
    GET_CHARGE_URL = '/get_charge'

    USER_OBJ = {
        "email": "bob@email.com",
        "password": "1234",
        "first_name": "john",
        "last_name": "marston"
    }

    USER_OBJ_INCORRECT_PASSWORD = {
        "email": "bob@email.com",
        "password": "12345"
    }

    USER_OBJ_LOGIN_NOT_EXISTS = {
        "email": "sus@email.com",
        "password": "1234"
    }

    MOVIE_OBJ = {
        "title": "Pulp Fiction"
    }

    MOVIE_OBJ_NOT_EXISTS = {
        "title": "asdfasd 3"
    }

    jwt_token = None
    HEADER = {"content-type": "application/json"}
    header_auth = {"x-access-token": '%s' % jwt_token}

    @classmethod
    def setUpClass(cls):
        r = requests.post(cls.API_URL + cls.CREATE_USER_URL, json=cls.USER_OBJ)
        pass

    @classmethod
    def tearDownClass(cls):
        # code that is executed after all tests in one test run
        pass

    def tearDown(self):
        # code that is executed after each test
        time.sleep(0.5)

    # This test will either return 200 if run for the first time and afterwards 400 because
    # the user will have already been inserted in the database.
    def test_create_user_exists(self):
        r = requests.post(self.API_URL + self.CREATE_USER_URL, json=self.USER_OBJ)
        self.assertEqual(r.status_code, 400)

    def test_create_user_missing_json(self):
        r = requests.post(self.API_URL + self.CREATE_USER_URL)
        self.assertEqual(r.status_code, 400)

    def test_login_user(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        self.assertEqual(r.status_code, 201)

    def test_login_user_missing_json(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL)
        self.assertEqual(r.status_code, 400)

    def test_login_user_incorrect_password(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ_INCORRECT_PASSWORD)
        self.assertEqual(r.status_code, 403)

    def test_login_user_not_exists(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ_LOGIN_NOT_EXISTS)
        self.assertEqual(r.status_code, 404)

    def test_auth_test(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        self.assertTrue(r.json()['ok'])

    def test_auth_missing(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ_LOGIN_NOT_EXISTS)
        self.assertFalse(r.json()['ok'])

    def test_auth_invalid(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ_INCORRECT_PASSWORD)
        self.assertEqual(r.status_code, 403)

    def test_get_all_movies(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.get(self.API_URL + self.GET_ALL_MOVIES_URL, headers=header_auth)
        self.assertEqual(r.status_code, 200)

    def test_get_movies_by_category(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}
        params = {"category": "History"}

        r = requests.get(self.API_URL + self.GET_MOVIES_CATEGORY_URL, headers=header_auth, params=params)
        self.assertEqual(r.status_code, 200)

    def test_get_movies_by_category_no_params(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.get(self.API_URL + self.GET_MOVIES_CATEGORY_URL, headers=header_auth)
        self.assertEqual(r.status_code, 400)

    def test_get_movies_by_category_and_category_no_exist(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}
        params = {"category": "lalalala"}

        r = requests.get(self.API_URL + self.GET_MOVIES_CATEGORY_URL, headers=header_auth, params=params)
        self.assertEqual(r.status_code, 404)

    def test_navigate(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}
        params = {"title": "Pulp Fiction"}

        r = requests.get(self.API_URL + self.NAVIGATE_URL, headers=header_auth, params=params)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 12)

    def test_navigate_no_params(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.get(self.API_URL + self.NAVIGATE_URL, headers=header_auth)
        self.assertEqual(r.status_code, 400)

    def test_navigate_movie_no_exist(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}
        params = {"title": "lalalala 2"}

        r = requests.get(self.API_URL + self.NAVIGATE_URL, headers=header_auth, params=params)
        self.assertEqual(r.status_code, 404)

    def test_rent(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.post(self.API_URL + self.RENT_URL, headers=header_auth, json=self.MOVIE_OBJ)
        self.assertEqual(len(r.json()), 2)

    def test_rent_body_missing(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.post(self.API_URL + self.RENT_URL, headers=header_auth)
        self.assertEqual(r.status_code, 400)

    def test_rent_already_renting(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.post(self.API_URL + self.RENT_URL, headers=header_auth, json=self.MOVIE_OBJ)
        self.assertEqual(len(r.json()), 2)

    def test_rent_not_found(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.post(self.API_URL + self.RENT_URL, headers=header_auth, json=self.MOVIE_OBJ_NOT_EXISTS)
        self.assertEqual(r.status_code, 404)

    def test_return_movie(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.post(self.API_URL + self.RETURN_MOVIE_URL, headers=header_auth, json=self.MOVIE_OBJ)
        self.assertEqual(len(r.json()), 2)

    def test_get_rentals(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.get(self.API_URL + self.GET_RENTALS_URL, headers=header_auth)
        self.assertEqual(r.status_code, 200)

    def test_get_charge(self):
        r = requests.post(self.API_URL + self.LOGIN_USER_URL, json=self.USER_OBJ)
        jwt_token = r.json()['token']
        header_auth = {"x-access-token": '%s' % jwt_token}

        r = requests.get(self.API_URL + self.GET_CHARGE_URL, headers=header_auth)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
