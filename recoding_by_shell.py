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
formatter = logging.Formatter('|%(asctime)s||%(name)s||%(levelname)s|\n%(message)s',datefmt='%Y-%m-%d %H:%M:%S') 
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler) 

def move_and_wait_until_complete(reloc_paths, dbx_variable):
    if len(reloc_paths) == 0:
        print("Nothing to move")
        return

    print("{} files to move...".format(len(reloc_paths)))
    # files_move_batch is deprecated and need to change to move_batch.
    # but there is no move_batch api?
    job_status = dbx_variable.files_move_batch(reloc_paths, autorename=True)
    if not job_status.is_async_job_id():
        print("Job already complete!")
        return
    jobid = job_status.get_async_job_id()
    print("Executing with jobid({})".format(jobid))
    print("Checking status: ")
    while 1:
        status = dbx_variable.files_move_batch_check(jobid)
        if not (status.is_complete() or status.is_failed()):
            sys.stdout.write("...")
            sys.stdout.flush()
            time.sleep(1)
            continue

        if status.is_complete():
            print("\nJob id ({}) complete".format(jobid))
            print("{} files moved".format(len(reloc_paths)))
        else:
            print("\nJob id ({}) failed".format(jobid))
            print(status.get_failed())
        break


def get_file_names_to_move(from_folder, date_str_variable, dbx_variable):
    # original code
    """
    if cursor is not None:
        continuing_list = dbx.files_list_folder_continue(cursor)
    else:
        continuing_list = dbx.files_list_folder( upload_loc)

    files = [_file.path_lower for _file in continuing_list.entries]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor))
    return files
    """
    continuing_list = dbx_variable.files_list_folder(from_folder)
    files = [_file.path_lower for _file in continuing_list.entries if date_str_variable[:10] not in _file.name]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor, date_str_variable, dbx_variable))
    return files


def get_file_names_to_2weekago(from_folder, dbx_variable, date_str_variable):
    continuing_list = dbx_variable.files_list_folder(from_folder)
    days_14_ago = datetime.datetime.now() - datetime.timedelta(weeks=2)
    days_14_ago_str = days_14_ago.strftime("%Y-%m-%d")
    files = [_file.path_lower for _file in continuing_list.entries if days_14_ago_str > _file.name]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor, date_str_variable, dbx_variable))
    return files


def upload_to_dropbox(dbx_variable, upload_loc_var, date_str_variable, move_loc_var, program_name_var,current_loc_var):
    # checking status
    print(dbx_variable.users_get_current_account())

    filelist = get_file_names_to_move(upload_loc_var, date_str_variable, dbx_variable)
    print(filelist)
    # need to no duplicate folder name
    for x in filelist:
        print(x, x.replace(upload_loc_var, move_loc_var))
    relocation_paths = [dropbox.files.RelocationPath(x, x.replace(upload_loc_var, move_loc_var)) for x in filelist]
    print(relocation_paths)
    move_and_wait_until_complete(relocation_paths, dbx_variable)

    mp3_file = date_str_variable + '_' + program_name_var + '.mp3'

    with open(current_loc_var + mp3_file, 'rb') as f:
        dbx_variable.files_upload(f.read(), upload_loc_var + '/' + mp3_file, mode=dropbox.files.WriteMode.overwrite)

    import os
    os.system("mkdir " + current_loc_var + "past/" + date_str_variable)
    os.system("mv " + current_loc_var + mp3_file + " " + current_loc_var + "past/" + date_str_variable + "/" + mp3_file)

    delete_filelist = get_file_names_to_2weekago(move_loc_var, dbx_variable, date_str_variable)

    print(delete_filelist)
    for path in delete_filelist:
        dbx_variable.files_delete(path)

import requests
import os
def get_vault_configuration():
    vault_addr = os.environ.get("VAULT_ADDR")
    vault_token = os.environ.get("VAULT_TOKEN")
    endpoint = f"{vault_addr}/v1/kv/data/ebs_radio"

    # HTTP GET 요청을 통해 데이터를 가져옵니다.
    headers = {"X-Vault-Token": vault_token}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        # 에러 응답의 경우 예외를 발생시킵니다.
        response.raise_for_status()

def recording(date_str_variable):
    
    """
    ori_file = current_loc_var + date_str_variable + '_' + program_name
    mp3_file = current_loc_var + date_str_variable + '_' + program_name + '.mp3'

    rtmpdump = ['rtmpdump', '-r', radio_addr, '-B', record_mins, '-o', ori_file]
    ffmpeg = ['ffmpeg', '-i', ori_file, '-vn', '-acodec', 'copy', mp3_file]
    rm = ['rm', '-rf', ori_file]

    p = subprocess.Popen(rtmpdump)
    p.communicate()
    p = subprocess.Popen(ffmpeg)
    p.communicate()
    p = subprocess.Popen(rm)
    p.communicate()
    """


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
    arg_parser.add_argument('start_time_str', type=str, default=date_str,
                            help="trigger time ")
    args = arg_parser.parse_args()
    recording(date_str)


    """
    date = datetime.datetime.now()

    date_str = date.strftime('%Y-%m-%d_%H:%M')

    argparser = argparse.ArgumentParser()
    argparser.add_argument('radio_channel', type=str, default="ebs_fm",
                           help="Which channel do you want to record?")

    argparser.add_argument('duration', type=int, default=20,
                           help="What is the second number?")

    argparser.add_argument('current_loc', type=str, default="~/",
                           help="What is the current folder")

    args = argparser.parse_args()

    current_loc = args.current_loc
    program_name = args.program_name
    record_mins = str(args.duration)

    configparser = ConfigParser()
    configparser.read(current_loc + '.config')
    api_token = configparser.get('dropbox', 'api_token')
    upload_loc = configparser.get('dropbox', 'upload_loc')
    move_loc = configparser.get('dropbox', 'move_loc')

    radio_address = configparser.get('ebs_address', args.radio_channel)

    dbx = dropbox.Dropbox(api_token)
    recording(date_str,current_loc)
    upload_to_dropbox(dbx, upload_loc, date_str, move_loc, program_name,current_loc)
    """
