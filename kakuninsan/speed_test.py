import subprocess
import json
import re


class SpeedTest:
    def __init__(self):
        self.SERVER_COUNT = 3
        self.options = ['speedtest', '--json', '--share']

    def sponsor(self):
        # 日本のサーバーを取得
        p1 = subprocess.Popen(['speedtest', '--list'], encoding='utf-8', stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', 'Japan'], encoding='utf-8', stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        # Serverを抜き出してリスト化
        server_list = {}
        # 14623) IPA CyberLab (Bunkyo, Japan)[**.** km]
        # 上記の形で出力されるので、整形してdictにする
        for server in p2.communicate()[0].split('\n'):
            server_id = '0'
            distance = '0.0 km'
            server_area = ''
            # 先頭空白削除して、server_idをとりあえずかっこ付きで抜き出し
            server = server.lstrip()
            id_match = re.compile(r'\d+\)')
            if id_match.match(server):
                server_id = id_match.match(server).group()
                # 出力文字列からserver_idを削除、先頭空白も削除
                server = id_match.sub('', server).lstrip()
                # カッコ取る
                server_id = server_id.replace(')', '')

            # 距離抜き出し
            distance_match = re.compile(r'\[\d+\.\d+ km\]')
            if distance_match.search(server):
                distance = distance_match.search(server).group()
                # 出力文字列からdistance削除
                server = distance_match.sub('', server)
                # カッコ取る
                distance = distance.replace('[', '').replace(']', '')

            # サーバーエリア抜き出し
            server_area_match = re.compile(r' \(.+, Japan\)')
            if server_area_match.search(server):
                server_area = server_area_match.search(server).group().lstrip()
                server = server_area_match.sub('', server)
                server_area = server_area.replace('(', '').replace(')', '')

            server_list[server_id] = {}
            server_list[server_id]['sponsor'] = server.rstrip()
            server_list[server_id]['server_area'] = server_area
            server_list[server_id]['distance'] = distance

            if len(server_list) == self.SERVER_COUNT:
                break

        return server_list

    def speed_test_result(self, server_id):
        if server_id != '0':
            self.options.append('--server')
            self.options.append(server_id)
        result_dict = {}
        try:
            process = subprocess.run(self.options, encoding='utf-8', stdout=subprocess.PIPE)
            result = [line for line in process.stdout.split('\n')]
            res_json = json.loads(result[0])
            result_dict = {
                'download': res_json['download'],
                'upload': res_json['upload'],
                'global_ip_address': res_json['client']['ip'],
                'sponsor': res_json['server']['sponsor'],
                'image_url': res_json['share']
            }
            return result_dict
        except Exception as e:
            result_dict['Error'] = e
        return result_dict
