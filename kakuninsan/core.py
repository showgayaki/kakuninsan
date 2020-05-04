import socket
import datetime
import os
from config import Config
from speed_test import SpeedTest
import database
from mail import Mail, Html
import logger
import requests
from pathlib import Path


def insert_info(now, computer_name, st_result):
    now = now.strftime('%Y-%m-%d_%H:%M:%S')
    insert_dict = {
        'computer_name': computer_name
        , 'global_ip_address': st_result['global_ip_address']
        , 'download': st_result['download']
        , 'upload': st_result['upload']
        , 'image_url': st_result['image_url']
        , 'created_at': now
        , 'updated_at': now
    }

    return insert_dict


def download_image(now, current_dir, url):
    now = now.strftime('%Y-%m-%d_%H-%M-%S')
    res = requests.get(url)
    image_dir = os.path.join(current_dir, 'templates/img')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    image_file_path = os.path.join(image_dir, '{}.png'.format(now))
    image = res.content
    with open(image_file_path, 'wb') as f:
        f.write(image)
    return image_file_path, image


def mail_subject(records):
    is_updated = False
    for i, record in enumerate(records):
        if i != len(records) - 1:
            if records[i][1] != records[i + 1][1]:
                is_updated = True
                record.append('updated')
            else:
                record.append('')
        else:
            record.append('')
    subject = 'IP Address is UPDATED' if is_updated else 'IP Address is NOT updated'

    return records, subject


def main():
    now = datetime.datetime.now()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    log = logger.Logger(current_dir, 10)
    config = Config(current_dir)
    cfg = config.config()

    # computer_name取得
    computer_name = socket.gethostname()
    log.logging('Started on {}'.format(computer_name))

    # スピードテスト
    options = ['speedtest', '--json', '--share']
    st = SpeedTest(options)
    st_result = st.speed_test_result()
    log.logging('Current IP Address: {}'.format(st_result['global_ip_address']))

    # Insert
    db = database.TableIp(cfg['db_info'], cfg['table_detail']['table_name'])
    insert_dict = insert_info(now, computer_name, st_result)
    insert_result = db.insert_record(cfg['db_info'], cfg['table_detail'], insert_dict)
    log.logging('DB insert {}'.format(insert_result))

    # データベースからレコード取得
    last_records = db.fetch_last_ip(cfg['table_detail']['clm_created_at'])

    # メール作成
    records, subject = mail_subject(last_records)
    html = Html()
    # ToDo matplotlibで回線速度をグラフ化
    image_file_path, image = download_image(now, current_dir, st_result['image_url'])
    contents = html.build_html(records, image_file_path)
    body_dict = {'subject': subject, 'body': contents}

    # メール送信
    mailer = Mail(cfg['mail_info'])
    msg = mailer.create_message(body_dict)
    result = mailer.send_mail(msg)
    log.logging('Send Mail {}'.format(result))


if __name__ == '__main__':
    main()
