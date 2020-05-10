import os
import socket
import datetime
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


def build_contents(db, cfg, log):
    # データベースからレコード取得
    interval_hour = int(cfg['interval_hour']) if cfg['interval_hour'] else 24
    records = db.fetch_last_ip(cfg['table_detail']['clm_created_at'], interval_hour)
    log.logging('Last IP Address: {}'.format(records[0][1]))

    # グラフ画像
    graph = Graph(records)
    image_file_path = graph.draw_graph()

    # IPの更新有無によってメールsubject変更
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

    # コンテンツ作成
    html = Html()
    contents = html.build_html(records, image_file_path)
    # htmlフォルダなかったら作って、index.htmlに書き出し
    index_dir = os.path.join(cfg['web_server']['document_root'])
    if not os.path.isdir(index_dir):
        os.makedirs(index_dir)
    index_path = os.path.join(index_dir, 'index.html')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(contents)
    return {'subject': subject, 'body': contents}


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
    log.logging('Download Speed: {} bps'.format(int(st_result['download'])))
    log.logging('Upload Speed: {} bps'.format(int(st_result['upload'])))

    # Insert
    db = TableIp(cfg['db_info'], cfg['table_detail']['table_name'])
    insert_dict = insert_info(now, computer_name, st_result)
    insert_result = db.insert_record(cfg['db_info'], cfg['table_detail'], insert_dict)
    log.logging('DB insert {}'.format(insert_result))

    # 指定時間になったらメール送信。指定時間以外は、webサーバー動いている環境ならindex.htmlに書き出し
    if now.strftime('%H:%M') == cfg['mail_send_time']:
        body_dict = build_contents(db, cfg, log)
        # メール送信
        mailer = Mail(cfg['mail_info'])
        msg = mailer.create_message(body_dict)
        result = mailer.send_mail(msg)
        log.logging('Send Mail {}'.format(result))
    elif cfg['web_server']['is_running'] == 'True':
        build_contents(db, cfg, log)
        log.logging('It is not time to send an email.')

    log.logging('Stopped.')


if __name__ == '__main__':
    main()
