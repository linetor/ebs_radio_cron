import subprocess
import datetime
import argparse
import dropbox
import sys
from configparser import ConfigParser
import os
import time

#to do : need to refactor code style
parser = ConfigParser()
parser.read('.config')
api_token=parser.get('dropbox', 'api_token')
upload_loc=parser.get('dropbox', 'upload_loc')
move_loc = parser.get('dropbox', 'move_loc')

dbx = dropbox.Dropbox(api_token)



def move_and_wait_until_complete(reloc_paths):
    if len(reloc_paths) == 0:
        print("Nothing to move")
        return
    print("{} files to move...".format(len(reloc_paths)))
    job_status = dbx.files_move_batch(reloc_paths, autorename=True)
    if not job_status.is_async_job_id():
        print("Job already complete!")
        return
    jobid = job_status.get_async_job_id()
    print("Executing with jobid({})".format(jobid))
    print("Checking status: ")
    while 1:
        status = dbx.files_move_batch_check(jobid)
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


def get_file_names_to_move(from_folder):
    continuing_list = dbx.files_list_folder( from_folder)
    files = [_file.path_lower for _file in continuing_list.entries]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor))
    return files

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


def upload_to_dropbox():
    import dropbox
    from configparser import ConfigParser
    parser = ConfigParser()
    parser.read('.config')
    api_token=parser.get('dropbox', 'api_token')
    upload_loc=parser.get('dropbox', 'upload_loc')
    move_loc=parser.get('dropbox', 'move_loc')
    dbx = dropbox.Dropbox(api_token)
    print(dbx.users_get_current_account())
    with open("requirements.txt",'rb') as f:
        dbx.files_upload(f.read(), upload_loc+"/requirements.txt", mode=dropbox.files.WriteMode.overwrite)

    fileList=get_file_names_to_move(upload_loc)
    print(fileList)
    #no duplicate folder name
    for x in fileList:
        print(x,x.replace(upload_loc,move_loc))
    relocation_paths=[dropbox.files.RelocationPath(x,x.replace(upload_loc,move_loc)) for x in fileList]
    print(relocation_paths)
    move_and_wait_until_complete(relocation_paths)
    #list(map(lambda x: dropbox.files.RelocationPath(x,os.path.join('/ebs_past', "requirements.txt")), ["/ebs_today/requirements.txt"]))




def recording():

    date = datetime.datetime.now()
    date_str = date.strftime('%Y-%m-%d_%H:%M')

    parser = argparse.ArgumentParser()

    parser.add_argument('program_name', type=str, default=date_str+"_english_radio",
                        help="What is the ebs radio program name?")

    parser.add_argument('duration', type=int, default=20,
                        help="What is the second number?")



    args = parser.parse_args()

    radio_addr = "rtmp://ebsandroid.ebs.co.kr/fmradiofamilypc/familypc1m"

    program_name = args.program_name
    record_mins = args.duration

    ori_file = '/home/python/temp' + date_str + '_' + program_name
    m4a_file = '/home/python/ebs' + date_str + '_' + program_name + '.m4a'

    rtmpdump = ['rtmpdump', '-r', radio_addr, '-B', record_mins, '-o', ori_file]
    ffmpeg = ['ffmpeg', '-i', ori_file, '-vn', '-acodec', 'copy', m4a_file]
    rm = ['rm', '-rf', ori_file]

    p = subprocess.Popen(rtmpdump)
    p.communicate()
    p = subprocess.Popen(ffmpeg)
    p.communicate()
    p = subprocess.Popen(rm)
    p.communicate()


if __name__ == "__main__":
    upload_to_dropbox()
