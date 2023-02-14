from pathlib import Path
import socket
import datetime
import time
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
        'computer_name': computer_name,
        'global_ip_address': st_result['global_ip_address'],
        'download': st_result['download'],
        'upload': st_result['upload'],
        'sponsor': st_result['sponsor'],
        'image_url': st_result['image_url'],
        'created_at': now,
        'updated_at': now
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


def post_line(api_url, access_token, image_file_path):
    bot = LineNotify(api_url, access_token)
    payload = {
        'message': '本日の回線速度',
        'stickerPackageId': None,
        'stickerId': None
    }
    image = image_file_path
    return bot.send_message(payload, image)


def main():
    now = datetime.datetime.now()
    root_dir = Path(__file__).resolve().parents[1]
    log = Logger(root_dir)
    cfg = config.config(root_dir)
    # computer_name取得
    computer_name = socket.gethostname()
    log.logging('info', '===== Kakuninsan Started on {} ====='.format(computer_name))

    # DBインスタンス
    db = TableIp(cfg['db_info'], cfg['table_detail']['table_name'])

    # スピードテスト
    st = SpeedTest()
    log.logging('info', 'Fetch Server list.')
    server_dict = st.sponsor()
    log.logging('info', '---Server list---')
    server_ids = []
    for i, item in enumerate(server_dict.items()):
        server_ids.append(item[0])
        log.logging('info', 'Server{}: {}'.format(i + 1, item))
    log.logging('info', '-----------------')

    # test_server = {'20976': {'sponsor': 'GLBB Japan', 'server_area': 'Tokyo, Japan', 'distance': '2.12 km'}}
    # server_ids.insert(0, '20976')
    # server_dict.update(test_server)

    for server_id in server_ids:
        # サーバーリストが取得できなかったら、ループを抜けてスピードテストは行わない
        if server_id == '0':
            log.logging('error', 'FAILED to fetch Server list.')
            break

        for i in range(1, int(cfg['speedtest']['retry_count']) + 1):
            log.logging('info', 'Start SpeedTest on Server[id: {}, sponsor: {}], count: {}'
                        .format(server_id, server_dict[server_id]['sponsor'], i))
            st_result = st.speed_test_result(server_id)

            if 'Error' in st_result.keys():
                log.logging('error', 'SpeedTest Failed: {}'.format(st_result['Error']))
                log.logging('error', 'Pause for {} Seconds.'.format(cfg['speedtest']['interval_seconds']))
                time.sleep(int(cfg['speedtest']['interval_seconds']))
                continue
            else:
                current_ip = st_result['global_ip_address']
                log.logging('info', 'Current IP Address: {}'.format(current_ip))

                download = graph.bytes_to_megabytes(st_result['download'])
                upload = graph.bytes_to_megabytes(st_result['upload'])
                log.logging('info', 'Download Speed: {} Mbps'.format(download))
                log.logging('info', 'Upload Speed: {} Mbps'.format(upload))

                # Insert
                log.logging('info', 'Start DB insert')
                insert_dict = insert_info(now, computer_name, st_result)
                insert_result = db.insert_record(cfg['db_info'], cfg['table_detail'], insert_dict)
                level = 'error' if 'Error' in insert_result else 'info'
                log.logging(level, 'DB insert {}'.format(insert_result))
                break
        # スピードテストが成功したらループ抜ける
        if level == 'info':
            break

    # 指定時間分のレコード取得
    interval_hour = int(cfg['interval_hour']) if cfg['interval_hour'] else 24
    records = db.fetch_last_ip(cfg['table_detail']['clm_created_at'], interval_hour)
    level = 'error' if 'Error' in records else 'info'
    # 前回のIPは、今回インサートしたものの一つ前(listの2番目)のレコード
    last_ip = records[1][1]
    log.logging(level, 'Last IP Address: {}'.format(last_ip))

    is_send_time = now.strftime('%H') == cfg['mail_send_time']
    is_post_time = now.strftime('%H') == cfg['line']['post_time']
    # 指定時間になったらメール送信 or LINEで通知。指定時間以外は、webサーバー動いている環境ならindex.htmlに書き出し
    if is_send_time or is_post_time or cfg['web_server']['is_running']:
        # グラフ画像
        grph = Graph(records)
        image_file_path = grph.draw_graph()
        # コンテンツ作成
        html = Html(root_dir)

        if is_send_time:
            log.logging('info', 'It is time to send an email')
            is_updated, records = check_ip(records)
            mail_contents = html.build_html(False, records, image_file_path)
            subject = 'IP Address is UPDATED' if is_updated else 'IP Address is NOT updated'
            body_dict = {'subject': subject, 'body': mail_contents}
            # メール送信
            log.logging('info', 'Start to send email')
            mailer = Mail(cfg['mail_info'])
            msg = mailer.create_message(body_dict)
            result = mailer.send_mail(msg)
            level = 'error' if 'Error' in result else 'info'
            log.logging(level, 'Send Mail Result {}'.format(result))
        else:
            log.logging('info', 'It is not time to send an email')

        if cfg['web_server']['is_running']:
            is_updated, records = check_ip(records)
            web_contents = html.build_html(True, records, image_file_path)
            # htmlフォルダなかったら作って、index.htmlに書き出し
            index_dir = Path(cfg['web_server']['document_root'])
            if not index_dir.is_dir():
                index_dir.mkdir()
            index_path = index_dir.joinpath('index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(web_contents)

        if is_post_time:
            log.logging('info', 'Start post to LINE.')
            post_result = post_line(cfg['line']['api_url'], cfg['line']['access_token'], image_file_path)
            level = 'error' if 'Error' in post_result else 'info'
            log.logging(level, 'LINE result: {}'.format(post_result))
        else:
            log.logging('info', 'It is not time to post to LINE.')

    log.logging('info', '===== Kakuninsan Stopped. =====')


if __name__ == '__main__':
    main()
