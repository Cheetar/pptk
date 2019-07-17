import json
import unittest

from verifier import app

app.app_context().push()  # Push the context


class TestVerifier(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_verify(self):
        url = "https://jrbenjamin.files.wordpress.com/2014/05/teddy-roosevelt.jpg"

        response = self.app.get('/api/v1/verify?image={}'.format(url))
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.get_data(as_text=True))
        self.assertIn("image_funniness", response_data)
        self.assertIn("suitable_for_presentation", response_data)


if __name__ == '__main__':
    unittest.main()
