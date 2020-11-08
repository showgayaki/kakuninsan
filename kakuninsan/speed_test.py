import subprocess
import json
import time


class SpeedTest:
    def __init__(self, options):
        self.RETRY_COUNT = 3
        self.SLEEP_SECONDS = 3
        self.options = options

    def speed_test_result(self):
        try_count = 1
        while True:
            try:
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
                break
            except Exception as e:
                time.sleep(self.SLEEP_SECONDS)
                if try_count == self.RETRY_COUNT:
                    result_dict = {'Error': e}
                    break
                try_count += 1
        return result_dict
