# ebs_radio_cron
## recoding by shell
## will upload to dropbox
# reference
https://younworld.tistory.com/entry/EBS-%EB%9D%BC%EB%94%94%EC%98%A4-%EC%9E%90%EB%8F%99-%EB%85%B9%EC%9D%8C
# need to install
rtmpdump, ffmpeg : linux  
I want to change these to python pachage not shell
#current status
need to test by raspberry  
#raspberry problem
When I install using pip install requirement.txt, there is problem like this.
Installing collected packages: certifi                                                                                                                                           
  Found existing installation: certifi 2018.8.24                                                                                                                                 
Cannot uninstall 'certifi'.   
It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.  
I don't know why this happens.
But When I skip this certifi(remove certifi==2020.4.5.1), All are happy
todo --> whey this problem happens
#radio address
I find there are two channel for engligh lecture.  
I find it by googling it in the blog.
But actually, I need to find how to get address 
#cron setting
## need to change python, ~/recoding_by_shell.py to proper position
50 05 * * 1-6 python ~/recoding_by_shell.py british_eng ebs_fm 590
00 06 * * 1-6 python ~/recoding_by_shell.py easy_writing ebs_fm 1190
20 06 * * 1-6 python ~/recoding_by_shell.py ear_engligh ebs_fm 1190
40 06 * * 1-6 python ~/recoding_by_shell.py mouse_engligh ebs_fm 1190
00 07 * * 1-6 python ~/recoding_by_shell.py start_engligh ebs_fm 1190
20 07 * * 1-6 python ~/recoding_by_shell.py easy_engligh ebs_fm 1190
40 07 * * 1-6 python ~/recoding_by_shell.py power_english ebs_fm 1190

00 06 * * 1-6 python ~/recoding_by_shell.py gogo_listening ebse 590
10 06 * * 1-6 python ~/recoding_by_shell.py travel_diary ebse 590
20 06 * * 1-6 python ~/recoding_by_shell.py anyone_toktok ebse 590
30 06 * * 1-6 python ~/recoding_by_shell.py breakthrough_speaking ebse 590
40 06 * * 1-6 python ~/recoding_by_shell.py word_order ebse 590
50 06 * * 1-6 python ~/recoding_by_shell.py english_allinone ebse 590
00 07 * * 1-6 python ~/recoding_by_shell.py english_news ebse 1190
20 07 * * 1-6 python ~/recoding_by_shell.py common_english ebse 1790

