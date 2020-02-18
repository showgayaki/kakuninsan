import consts
import currentip
import database
import mail
import logger
import socket
import datetime


def current_ip(url_dict):
    ip = currentip.CurrentGlobalIp(url_dict)
    return ip.fetch_current_ip()


def last_ip(connect_db, clm_created_at):
    return connect_db.fetch_last_ip(clm_created_at)


def insert_info(clm_dict, computer_name, global_ip, created_at, updated_at):
    insert_dict = {
        'computer_name': computer_name,
        'global_ip': global_ip,
        'created_at': created_at,
        'updated_at': updated_at
    }
    insert_dict.update(clm_dict)
    return insert_dict


def create_body(computer_name, last, current, insert_result):
    if last == current:
        subject = 'IP Address is NOT updated'
    elif 'Error' in last or 'Error' in current:
        subject = 'IP Address FAILED to get'
    else:
        subject = 'IP Address is UPDATED'

    body = f'Computer Name      : {computer_name}\n'\
        f'Last IP Address    : {last}\n'\
        f'Current IP Address : {current}\n\n'\
        f'DB Insert {insert_result}'

    body_dict = {
        'subject': subject,
        'body': body
    }
    return body_dict


def create_sql_dict(insert_dict, sql_dict,  table_name):
    del sql_dict['host'], sql_dict['user'], sql_dict['password']
    sql_dict['table_name'] = table_name
    sql_dict.update(insert_dict)

    return sql_dict


def mail_result(smtp_dict, body_dict):
    mailer = mail.Mail(smtp_dict)
    msg = mailer.create_message(body_dict)
    return mailer.send_mail(msg)


def main():
    log = logger.Logger(consts.FILE_PATH, 10)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # computer_name取得
    computer_name = socket.gethostname()

    # サイトから現在のIP取得
    current = current_ip(consts.URL_INFO)
    log.logging('Current IP Address:{}'.format(current))

    # データベースから前回のIP取得
    connect_db = database.TableIp(consts.DB_INFO, consts.TABLE_NAME)
    last = last_ip(connect_db, consts.COLUMNS['clm_created_at'])
    log.logging('Last IP Address:{}'.format(last))

    # insert用dict作成
    insert_dict = insert_info(consts.COLUMNS, computer_name, current, now, now)
    sql_dict = create_sql_dict(insert_dict, consts.DB_INFO, consts.TABLE_NAME)

    # insertログ
    insert_result = connect_db.insert_record(sql_dict)
    log.logging('DB insert {}'.format(insert_result))

    # メール送信
    body_dict = create_body(computer_name, last, current, insert_result)
    result = mail_result(consts.MAIL_INFO, body_dict)
    log.logging('Send Mail {}'.format(result))


if __name__ == '__main__':
    main()
