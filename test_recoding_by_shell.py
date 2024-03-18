import unittest
from recoding_by_shell import get_vault_configuration
from recoding_by_shell import recording
from recoding_by_shell import upload_to_dropbox
from recoding_by_shell import move_past_file
from recoding_by_shell import delete_2week_ago_past_file
from recoding_by_shell import file_copy_to_ssh


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
        vault_data = get_vault_configuration("ebs_radio")
        print("ebs_radio",vault_data)

    def test_recording(self):
        print("recording start")
        # date_str_variable = "2024-03-01_07:40"
        # recording(date_str_variable)
        print("recording end")

    def test_get_dropbox_token_upload(self):
        print("get_dropbox_upload start")
        # import requests
        # import json

        # APP_KEY = get_vault_configuration("dropbox")['APP_KEY']
        # APP_SECRET = get_vault_configuration("dropbox")['APP_SECRET']
        # refresh_token = get_vault_configuration("dropbox")['refresh_token']
        # DROPBOX_TOKEN = json.loads(response.text)['access_token']
        # upload_to_dropbox("2024-03-01_07:40_power_english.mp3",DROPBOX_TOKEN)
        print("get_dropbox_upload end")


    def test_get_redis_value(self):
        #dont need
        print("redis access check")

    def test_move_past_file(self):
        # import dropbox
        # programName = "2024-03-01_07:40_power_english.mp3"
        # dateName = programName.split("_")[0]
        # title = "_".join(programName.split("_")[2:]).replace(".mp3","")
        # print("dateName",dateName,"title",title,"move start")
        # move_past_file(programName,token)
        # print("dateName",dateName,"title",title,"move end")
        print("test_move_past_file end")


    def test_deleting_file_on_dropbox(self):
        import dropbox
        programName = "2024-03-01_07:40_power_english.mp3"
        dateName = programName.split("_")[0]
        # title = "_".join(programName.split("_")[2:]).replace(".mp3","")
        # print("dateName",dateName,"title",title,"delete start")
        # delete_2week_ago_past_file(programName,token)
        # print("dateName",dateName,"title",title,"delete end")
        print("deleting file on dropbox")

    def test_moving_file_using_ssh(self):
        # https://stackoverflow.com/questions/68335/how-to-copy-a-file-to-a-remote-server-in-python-using-scp-or-ssh#
        programName = "2024-03-01_07:40_power_english.mp3"
        print("moving file using ssh start")
        file_copy_to_ssh(programName)
        print("moving file using ssh end")

if __name__ == '__main__':
    unittest.main()
