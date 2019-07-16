import os
import unittest

from application import create_app, db
from application.models import Slide

import json

app = create_app()  # Dynamically create the app
app.app_context().push()  # Push the context

class TestAPI(unittest.TestCase):
    def create_slide(self, url, funniness=None):
        s = Slide(url=url, funniness=funniness)
        db.session.add(s)
        db.session.commit()
        return s.id

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_healthcheck(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_create_slide(self):
        url1 = "https://images.pexels.com/photos/617278/pexels-photo-617278.jpeg"
        url2 = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        funniness1 = None
        funniness2 = 0.45

        # Create the slides
        response1 = self.app.post('/api/v1/slides', json={"url": url1})
        response2 = self.app.post('/api/v1/slides', json={"url": url2, "funniness": funniness2})
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

        r1 = json.loads(response1.get_data(as_text=True))
        r2 = json.loads(response2.get_data(as_text=True))
        
        id1 = r1["id"]
        id2 = r2["id"]

        s1 = Slide.query.filter_by(id=id1).first()
        s2 = Slide.query.filter_by(id=id2).first()
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)
        self.assertFalse(s1.deleted)
        self.assertFalse(s2.deleted)

        self.assertEqual(s1.url, url1)
        self.assertEqual(s2.url, url2)
        self.assertEqual(s1.funniness, funniness1)
        self.assertEqual(s2.funniness, funniness2)

    def test_get_slide(self):
        url = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        funniness = 0.3
        id = self.create_slide(url, funniness)

        response = self.app.get(f'/api/v1/slides/{id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'"url": "{url}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id}"', response.get_data(as_text=True))

    def test_get_slides(self):
        url1 = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        url2 = "https://images.pexels.com/photos/617278/pexels-photo-617278.jpeg"
        funniness1 = 0.5
        funniness2 = "null"

        id1 = self.create_slide(url1, funniness1)
        id2 = self.create_slide(url2)

        response = self.app.get('/api/v1/slides')
        self.assertEqual(response.status_code, 200)

        # Check if response contains the first slide
        self.assertIn(f'"url": "{url1}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness1}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id1}"', response.get_data(as_text=True))

        # Check if response contains the second slide
        self.assertIn(f'"url": "{url2}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness2}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id2}"', response.get_data(as_text=True))

    def test_delete_slide(self):
        url = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        funniness = 0.3
        id = self.create_slide(url, funniness)

        s = Slide.query.filter_by(id=id).first()
        self.assertIsNotNone(s)

        response = self.app.delete("/api/v1/slides/{}".format(id))
        self.assertEqual(response.status_code, 200)

        s = Slide.query.filter_by(id=id).first()
        self.assertTrue(s.deleted)

    def test_get_random_slides(self):
        url1 = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        url2 = "https://images.pexels.com/photos/617278/pexels-photo-617278.jpeg"
        url3 = "https://images.pexels.com/photos/320014/pexels-photo-320014.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        funniness1 = 0.3
        funniness2 = 0.5 
        funniness3 = "null"

        id1 = self.create_slide(url1, funniness1)
        id2 = self.create_slide(url2, funniness2)
        id3 = self.create_slide(url3)

        response = self.app.get('/api/v1/slides/random/3')
        self.assertEqual(response.status_code, 200)

        # Check if response contains the first slide
        self.assertIn(f'"url": "{url1}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness1}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id1}"', response.get_data(as_text=True))

        # Check if response contains the second slide
        self.assertIn(f'"url": "{url2}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness2}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id2}"', response.get_data(as_text=True))

        # Check if response contains the third slide
        self.assertIn(f'"url": "{url3}"', response.get_data(as_text=True))
        self.assertIn(f'"funniness": {funniness3}', response.get_data(as_text=True))
        self.assertIn(f'"id": "{id3}"', response.get_data(as_text=True))

        # Check for info
        self.assertIn(f'"min_funniness": {funniness1}', response.get_data(as_text=True))
        self.assertIn(f'"max_funniness": {funniness2}', response.get_data(as_text=True))
        self.assertIn(f'"avg_funniness": {float(funniness1+funniness2)/2}', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
