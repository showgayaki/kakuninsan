import subprocess
import json
import re


class SpeedTest:
    def __init__(self):
        self.SERVER_COUNT = 3
        self.OPTIONS = ['python', '-m', 'speedtest', '--secure']

    def sponsor(self):
        command = []
        command.extend(self.OPTIONS)
        command.append('--list')
        # python -m speedtest --secure --list
        command_result = subprocess.run(command, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if command_result.returncode != 0:
            return {'0': {'error': command_result.stderr}}

        # Serverを抜き出してDictionary化
        server_dict = {}
        # 14623) IPA CyberLab (Bunkyo, Japan)[**.** km]
        # 上記の形で出力されるので、整形してdictにする
        for server in command_result.stdout.split('\n'):
            server_id = '0'
            distance = '0.0 km'
            server_area = ''
            # 日本のサーバーを取得
            if 'Japan' in server:
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

                server_dict[server_id] = {}
                server_dict[server_id]['sponsor'] = server.rstrip()
                server_dict[server_id]['server_area'] = server_area
                server_dict[server_id]['distance'] = distance
            else:
                continue

            if len(server_dict) == self.SERVER_COUNT:
                break

        return server_dict

    def speed_test_result(self, server_id):
        options = []
        if server_id != '0':
            options.extend(self.OPTIONS)
            options.extend(['--json', '--server'])
            options.append(server_id)
        result_dict = {}
        try:
            process = subprocess.run(options, encoding='utf-8', stdout=subprocess.PIPE)
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
