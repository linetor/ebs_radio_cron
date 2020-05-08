import subprocess
import datetime
import argparse
import dropbox
import sys
from configparser import ConfigParser
import time

# Is it need to be here ??
configparser = ConfigParser()
configparser.read('.config')
api_token = configparser.get('dropbox', 'api_token')
upload_loc = configparser.get('dropbox', 'upload_loc')
move_loc = configparser.get('dropbox', 'move_loc')
dbx = dropbox.Dropbox(api_token)


def move_and_wait_until_complete(reloc_paths):

    if len(reloc_paths) == 0:
        print("Nothing to move")
        return

    print("{} files to move...".format(len(reloc_paths)))
    # files_move_batch is deprecated and need to change to move_batch.
    # but there is no move_batch api?
    job_status = dbx.files_move_batch(reloc_paths, autorename=True)
    if not job_status.is_async_job_id():
        print("Job already complete!")
        return
    jobid = job_status.get_async_job_id()
    print("Executing with jobid({})".format(jobid))
    print("Checking status: ")
    while 1:
        status = dbx.files_move_batch(jobid)
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
    continuing_list = dbx.files_list_folder(from_folder)
    files = [_file.path_lower for _file in continuing_list.entries]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor))
    return files


def upload_to_dropbox():

    # checking status
    print(dbx.users_get_current_account())

    filelist = get_file_names_to_move(upload_loc)
    print(filelist)
    # need to no duplicate folder name
    for x in filelist:
        print(x, x.replace(upload_loc, move_loc))
    relocation_paths = [dropbox.files.RelocationPath(x,x.replace(upload_loc,move_loc)) for x in filelist]
    print(relocation_paths)
    move_and_wait_until_complete(relocation_paths)

    m4a_file = date_str + '_' + program_name + '.m4a'

    with open("~/"+m4a_file, 'rb') as f:
        dbx.files_upload(f.read(), upload_loc+'/' + m4a_file, mode=dropbox.files.WriteMode.overwrite)

    import os
    os.system("rm ~/"+m4a_file)


# checking : In main, variable is used for global variable
# def recording(var_date_str, var_program_name, var_record_mins):
def recording():

    radio_addr = "rtmp://ebsandroid.ebs.co.kr/fmradiofamilypc/familypc1m"

    ori_file = '~/' + date_str + '_' + program_name
    m4a_file = '~/' + date_str + '_' + program_name + '.m4a'

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

    date = datetime.datetime.now()

    date_str = date.strftime('%Y-%m-%d_%H:%M')

    argparser = argparse.ArgumentParser()

    argparser.add_argument('program_name', type=str, default=date_str+"_english_radio",
                           help="What is the ebs radio program name?")

    argparser.add_argument('duration', type=int, default=20,
                           help="What is the second number?")

    args = argparser.parse_args()

    program_name = args.program_name
    record_mins = args.duration

    recording()
    upload_to_dropbox()
