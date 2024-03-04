import unittest
from recoding_by_shell import get_vault_configuration

class TestMyFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setUpClass')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_string_function(self):
        date_str_var = "2024-03-01_07:40"
        date_str = date_str_var[:10]
        time_str = date_str_var[11:]
        self.assertEqual(date_str,"2024-03-01")
        self.assertEqual(time_str.replace(":",""),"0740")

    def test_get_vault_configuration(self):
        vault_data = get_vault_configuration()['data']['data']
        print(vault_data)

if __name__ == '__main__':
    unittest.main()
