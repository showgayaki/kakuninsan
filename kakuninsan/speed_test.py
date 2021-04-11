import subprocess
import json


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
        for server in p2.communicate()[0].split('\n')[:self.SERVER_COUNT]:
            # 14623) IPA CyberLab (Bunkyo, Japan)[**.** km]
            # 上記の形で出力されるので、整形してdictにする
            server_id = server.split(') ')[0]
            server_list[server_id] = {}
            server_list[server_id]['sponsor'] = server.split(') ')[1].split(' (')[0]
            server_list[server_id]['server_area'] = server.split(') ')[1].split(' (')[1]
            server_list[server_id]['distance'] = server.split(') ')[2].replace('[', '').replace(']', '')

        return server_list

    def speed_test_result(self, server_id):
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
