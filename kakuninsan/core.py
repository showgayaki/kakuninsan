import os
import socket
import datetime
import config
from speed_test import SpeedTest
from database import TableIp
from mail import Mail, Html
import graph
from graph import Graph
from line_notify import LineNotify
from logger import Logger


def insert_info(now, computer_name, st_result):
    now = now.strftime('%Y-%m-%d_%H:%M:%S')
    insert_dict = {
        'computer_name': computer_name
        , 'global_ip_address': st_result['global_ip_address']
        , 'download': st_result['download']
        , 'upload': st_result['upload']
        , 'sponsor': st_result['sponsor']
        , 'image_url': st_result['image_url']
        , 'created_at': now
        , 'updated_at': now
    }
    return insert_dict


def check_ip(records):
    # IPが更新されてたら配列最後にupdatedを追加
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
    return is_updated, records


def post_line(api_url, access_token, message, image_file_path):
    bot = LineNotify(api_url, access_token)
    payload = {
        'message': message
        , 'stickerPackageId': None
        , 'stickerId': None
    }
    image = image_file_path
    return bot.send_message(payload, image)


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
    current_ip = st_result['global_ip_address']
    log.logging('Current IP Address: {}'.format(current_ip))
    log.logging('Sponsor: {}'.format(st_result['sponsor']))

    download = graph.bytes_to_megabytes(st_result['download'])
    upload = graph.bytes_to_megabytes(st_result['upload'])
    log.logging('Download Speed: {} Mbps'.format(download))
    log.logging('Upload Speed: {} Mbps'.format(upload))

    # Insert
    db = TableIp(cfg['db_info'], cfg['table_detail']['table_name'])
    insert_dict = insert_info(now, computer_name, st_result)
    insert_result = db.insert_record(cfg['db_info'], cfg['table_detail'], insert_dict)
    log.logging('DB insert {}'.format(insert_result))

    interval_hour = int(cfg['interval_hour']) if cfg['interval_hour'] else 24
    records = db.fetch_last_ip(cfg['table_detail']['clm_created_at'], interval_hour)
    last_ip = records[0][1]
    log.logging('Last IP Address: {}'.format(last_ip))

    # 指定時間になったらメール送信。指定時間以外は、webサーバー動いている環境ならindex.htmlに書き出し
    if now.strftime('%H:%M') == cfg['mail_send_time'] or cfg['web_server']['is_running']:
        # グラフ画像
        grph = Graph(records)
        image_file_path = grph.draw_graph()
        # コンテンツ作成
        html = Html()

    if now.strftime('%H:%M') == cfg['mail_send_time']:
        mail_contents = html.build_html(False, records, image_file_path)
        is_updated, records = check_ip(records)
        subject = 'IP Address is UPDATED' if is_updated else 'IP Address is NOT updated'
        body_dict = {'subject': subject, 'body': mail_contents}
        # メール送信
        mailer = Mail(cfg['mail_info'])
        msg = mailer.create_message(body_dict)
        result = mailer.send_mail(msg)
        log.logging('Send Mail {}'.format(result))
    else:
        log.logging('It is not time to send an email.')

    if cfg['web_server']['is_running']:
        is_updated, records = check_ip(records)
        web_contents = html.build_html(True, records, image_file_path)
        # htmlフォルダなかったら作って、index.htmlに書き出し
        index_dir = os.path.join(cfg['web_server']['document_root'])
        if not os.path.isdir(index_dir):
            os.makedirs(index_dir)
        index_path = os.path.join(index_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(web_contents)

    message = ('\n{:%-m/%-d %H:%M} 現在の回線速度'
               '\n\nダウンロード：{} Mbps'
               '\nアップロード：{} Mbps').format(now, download, upload)
    if last_ip != current_ip:
        message += ('\n\nあと、IP変わったみたいです。'
                    '\n{} --> {}').format(last_ip, current_ip)
        log.logging('IP address is updated: {} --> {}'.format(last_ip, current_ip))
    post_result = post_line(cfg['line']['api_url'], cfg['line']['access_token'], message, image_file_path)
    log.logging('LINE result: {}'.format(post_result))
    log.logging('Stopped.')


if __name__ == '__main__':
    main()
