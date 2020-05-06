import subprocess
import datetime
import argparse


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
    recording()
