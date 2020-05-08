def upload_to_dropbox(var_date_str, var_program_name):
    print(date_str)
    print(program_name)


if __name__ == "__main__":
    import datetime

    date = datetime.datetime.now()

    date_str = date.strftime('%Y-%m-%d_%H:%M')
    program_name = "AAA"
    upload_to_dropbox(date_str, program_name)
