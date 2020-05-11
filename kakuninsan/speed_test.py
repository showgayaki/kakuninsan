import subprocess
import json


class SpeedTest:
    def __init__(self, options):
        self.options = options

    def speed_test_result(self):
        process = subprocess.run(self.options, encoding='utf-8', stdout=subprocess.PIPE)
        result = [line for line in process.stdout.split('\n')]
        res_json = json.loads(result[0])
        result_dict = {
            'download': res_json['download']
            , 'upload': res_json['upload']
            , 'global_ip_address': res_json['client']['ip']
            , 'sponsor': res_json['server']['sponsor']
            , 'image_url': res_json['share']
        }
        return result_dict
