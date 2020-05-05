import os
import socket
import datetime
import requests
from pathlib import Path
import config
from speed_test import SpeedTest
from database import TableIp
from mail import Mail, Html
from graph import Graph
from logger import Logger


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
    image_dir = os.path.join(Path(current_dir).resolve().parents[0], 'img')
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
    log = Logger(current_dir, 10)
    cfg = config.config(current_dir)

    # computer_name取得
    computer_name = socket.gethostname()
    log.logging('Started on {}'.format(computer_name))

    # スピードテスト
    options = ['speedtest', '--json', '--share']
    st = SpeedTest(options)
    st_result = st.speed_test_result()
    log.logging('Current IP Address: {}'.format(st_result['global_ip_address']))

    # Insert
    db = TableIp(cfg['db_info'], cfg['table_detail']['table_name'])
    insert_dict = insert_info(now, computer_name, st_result)
    insert_result = db.insert_record(cfg['db_info'], cfg['table_detail'], insert_dict)
    log.logging('DB insert {}'.format(insert_result))

    # 指定時間になったらメール送信
    if now.strftime('%H:%M') == cfg['mail_send_time']:
        # データベースからレコード取得
        past_records = db.fetch_last_ip(cfg['table_detail']['clm_created_at'])
        graph = Graph(past_records)
        graph.draw_graph(now, current_dir)

        # メール作成
        records, subject = mail_subject(past_records)
        html = Html()
        image_file_path, image = download_image(now, current_dir, st_result['image_url'])
        contents = html.build_html(records, image_file_path)
        body_dict = {'subject': subject, 'body': contents}

        # メール送信
        mailer = Mail(cfg['mail_info'])
        msg = mailer.create_message(body_dict)
        result = mailer.send_mail(msg)
        log.logging('Send Mail {}'.format(result))
    else:
        log.logging('It is not time to send an email')

    log.logging('Stopped.')


if __name__ == '__main__':
    main()
