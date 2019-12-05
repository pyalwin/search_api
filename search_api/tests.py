from django.test import TestCase

# Create your tests here.
client = Client()

class SearchQueryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_query(self):
        response = self.client.get('/search/?term=The%20Book&no_of_results=2')
        self.assertEqual(response.status_code, 200)