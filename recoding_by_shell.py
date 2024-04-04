import subprocess
import datetime
import argparse
import dropbox
import sys
from configparser import ConfigParser
import time
import logging

logger = logging.getLogger(name='ebs recording')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('|%(asctime)s||%(name)s||%(levelname)s|%(message)s',datefmt='%Y-%m-%d %H:%M:%S') 
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def file_copy_to_ssh(programName):
    ssh_info = get_vault_configuration("ssh")

    ssh_ip = ssh_info['ssh_ip']['odroid']
    ssh_id = ssh_info['ssh_id']
    ssh_pass = ssh_info['ssh_pass']


    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_ip, username=ssh_id, password=ssh_pass)
    logger.info("file_copy_to_ssh start")
    sftp = ssh.open_sftp()
    sftp.put(programName, "/mnt/backup/ebs_radio_mp3/"+programName)
    sftp.close()
    ssh.close()
    os.remove(programName)
    logger.info("end start")



import requests
import os
def get_vault_configuration(endpoint):
    vault_addr = os.environ.get("VAULT_ADDR")
    vault_token = os.environ.get("VAULT_TOKEN")
    endpoint = f"{vault_addr}/v1/kv/data/{endpoint}"

    # HTTP GET 요청을 통해 데이터를 가져옵니다.
    headers = {"X-Vault-Token": vault_token}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['data']['data']

    else:
        # 에러 응답의 경우 예외를 발생시킵니다.
        response.raise_for_status()


def recording(date_str_variable):
    import subprocess
    vault_data = get_vault_configuration('ebs_radio')
    date_str = date_str_variable[:10]
    time_str = date_str_variable[11:]

    url = vault_data['ebs_url']

    program_name = vault_data[time_str.replace(":","")]['name']
    logger.info(f"{date_str_variable}_{program_name}.mp3 recording")
    output_file = f"{date_str_variable}_{program_name}.mp3"
    duration = int(vault_data['duration']) * 60    # 녹음 시간
    ffmpeg_cmd = f"ffmpeg  -i {url} -t {duration} -y  {output_file}"
    subprocess.call(ffmpeg_cmd, shell=True)

    return f"{date_str_variable}_{program_name}.mp3"

import pathlib
def upload_to_dropbox(programName,TOKEN):
    upload_location = "/ebs_today"

    dropBox = dropbox.Dropbox(TOKEN)
    fileName = pathlib.Path(".") / programName

    with fileName.open("rb") as f:
        meta = dropBox.files_upload(f.read(), upload_location+"/"+programName, mode=dropbox.files.WriteMode("overwrite"))

def move_past_file(programName,TOKEN):
    from_path = "/ebs_today"
    to_path = "/ebs_past"
    dateName = programName.split("_")[0]
    title = "_".join(programName.split("_")[2:]).replace(".mp3","")
    logger.info("today standard ","dateName",dateName,"title",title)
    dropBox = dropbox.Dropbox(TOKEN)

    fileNameList = [x.name for x in dropBox.files_list_folder(from_path).entries]
    fileNameList = [x for x in fileNameList if x<dateName and title in x]
    for fileName in fileNameList:
        dropBox.files_move_v2(from_path+"/"+fileName,to_path+"/"+fileName)
        logger.info("fileName ",fileName," moved")

def delete_2week_ago_past_file(programName,TOKEN):
    from datetime import datetime, timedelta
    delete_path = "/ebs_past"
    dateName = programName.split("_")[0] #2024-03-01
    week2ago_dateName = (datetime.strptime(dateName, "%Y-%m-%d") - timedelta(weeks=2)).strftime("%Y-%m-%d")

    title = "_".join(programName.split("_")[2:]).replace(".mp3","")
    logger.info("delete standard ","dateName",dateName,"week2ago_dateName", week2ago_dateName,"title",title)
    dropBox = dropbox.Dropbox(TOKEN)

    fileNameList = [x.name for x in dropBox.files_list_folder(delete_path).entries]
    logger.info("fileNameList before",fileNameList)
    fileNameList = [x for x in fileNameList if x < dateName and title in x and  x > week2ago_dateName]
    logger.info("fileNameList after",fileNameList)
    for fileName in fileNameList:
        dropBox.files_delete_v2(delete_path+"/"+fileName)
        logger.info("fileName ",fileName," deleted")


if __name__ == "__main__":
    #airflow에서 지정된 시간에 trigger 됨
    #지정된 시간에 time ex) 07:40 에 시작 --> 입력 parameter : 2024-03-01_07:40
    #vault 에서 현재 시간(0740)으로 시간을 받아서 라디오 명(power_english)을 받아서 라디오 녹음 시작 --> recording function
    #라디오 녹음 완료 시, dropbox로 update
    #dropbox 저장장소 확인 후 2주전 데이터 삭제
    #update 완료시 현재 경로의 파일 삭제 후, 저장 장소(odroid)에 이동

    date = datetime.datetime.now()
    date_str = date.strftime('%Y-%m-%d_%H:%M')

    logger.info("ebs recording start")

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--start_time_str', type=str, default=date_str,
                            help="trigger time ")
    args = arg_parser.parse_args()
    logger.info(f"arg : {{args.start_time_str}}" )

    programName = recording(args.start_time_str)
    logger.info("programName : "+programName)

    dropbox_kv = get_vault_configuration('dropbox')
    APP_KEY = dropbox_kv['APP_KEY']
    APP_SECRET = dropbox_kv['APP_SECRET']
    refresh_token = dropbox_kv['refresh_token']

    url = "https://api.dropbox.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }

    response = requests.post(url, headers=headers, data=data)
    import json
    DROPBOX_TOKEN = json.loads(response.text)['access_token']
    logger.info("get dropbbox token done")

    upload_to_dropbox(programName,DROPBOX_TOKEN)
    logger.info("upload to dropbbox done")
    
    file_copy_to_ssh(programName)
    logger.info("file copy to backup done")

    move_past_file(programName,DROPBOX_TOKEN)
    logger.info("move from today to past on dropbbox done")

    delete_2week_ago_past_file(programName,DROPBOX_TOKEN)
    logger.info("delete 2 week ago file on dropbbox done")

