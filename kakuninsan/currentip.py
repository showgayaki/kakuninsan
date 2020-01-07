import requests
import ipaddress


class CurrentGlobalIp:
    def __init__(self, url_dict):
        self.url = url_dict['url']
        self.connect_to = url_dict['connect_to']
        self.read_to = url_dict['read_to']

    def fetch_current_ip(self):
        res = requests.get(self.url, timeout=(self.connect_to, self.read_to))
        res.raise_for_status()
        if res.status_code == 200:
            if is_valid_ip(res.text):
                return res.text
            else:
                return 'Error : Value Error'
        else:
            return 'Error : {}'.format(res.status_code)


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
