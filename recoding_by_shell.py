import subprocess
import datetime
import argparse
import dropbox
import sys
from configparser import ConfigParser
import time

# Is it need to be here ??
# current_loc = configparser.get('current_loc', 'current_loc')


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


def get_file_names_to_move(from_folder,date_str):
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
    files = [_file.path_lower for _file in continuing_list.entries if date_str[:10] not in _file.name]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor,date_str))
    return files

def get_file_names_to_2weekago(from_folder):
    continuing_list = dbx.files_list_folder(from_folder)
    days_14_ago = datetime.datetime.now() - datetime.timedelta(weeks=2)
    days_14_ago_str = days_14_ago.strftime("%Y-%m-%d")
    files = [_file.path_lower for _file in continuing_list.entries if days_14_ago_str > _file.name]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(continuing_list.cursor,date_str))
    return files


def upload_to_dropbox(dbx,upload_loc,date_str,move_loc,program_name):

    # checking status
    print(dbx.users_get_current_account())

    filelist = get_file_names_to_move(upload_loc,date_str)
    print(filelist)
    # need to no duplicate folder name
    for x in filelist:
        print(x, x.replace(upload_loc, move_loc))
    relocation_paths = [dropbox.files.RelocationPath(x,x.replace(upload_loc,move_loc)) for x in filelist]
    print(relocation_paths)
    move_and_wait_until_complete(relocation_paths)

    m4a_file = date_str + '_' + program_name + '.m4a'

    with open(current_loc+m4a_file, 'rb') as f:
        dbx.files_upload(f.read(), upload_loc+'/' + m4a_file, mode=dropbox.files.WriteMode.overwrite)

    import os
    os.system("mkdir "+current_loc+"past/"+date_str)
    os.system("mv "+current_loc+m4a_file + " " +current_loc+"past/"+date_str+"/"+m4a_file)


    delete_filelist = get_file_names_to_2weekago(move_loc)

    print(delete_filelist)
    for path in delete_filelist:
        dbx.files_delete(path)



# checking : In main, variable is used for global variable
# def recording(var_date_str, var_program_name, var_record_mins):
def recording():

    radio_addr = radio_address

    ori_file = current_loc + date_str + '_' + program_name
    m4a_file = current_loc + date_str + '_' + program_name + '.m4a'

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
    configparser.read(current_loc+'.config')
    api_token = configparser.get('dropbox', 'api_token')
    upload_loc = configparser.get('dropbox', 'upload_loc')
    move_loc = configparser.get('dropbox', 'move_loc')

    radio_address = configparser.get('ebs_address', args.radio_channel)

    dbx = dropbox.Dropbox(api_token)
    recording()
    upload_to_dropbox(dbx,upload_loc,date_str,move_loc,program_name)
