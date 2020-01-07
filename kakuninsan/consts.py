import os
from dotenv import load_dotenv
import pathlib


dotenv_path = pathlib.Path(__file__).joinpath('../..', '.env')
load_dotenv(dotenv_path.resolve())


FILE_PATH = os.path.dirname(__file__)

URL_INFO = {
            'url': 'http://inet-ip.info/ip',
            'connect_to': 30,
            'read_to': 60
        }

DB_INFO = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASS')
}

TABLE_NAME = os.environ.get('TABLE_NAME')

COLUMNS = {
    'clm_computer_name': os.environ.get('CLM_COMPUTER_NAME'),
    'clm_global_ip': os.environ.get('CLM_GLOBAL_IP'),
    'clm_created_at': os.environ.get('CLM_CREATED_AT'),
    'clm_updated_at': os.environ.get('CLM_UPDATED_AT')
}

MAIL_INFO = {
    'smtp_server': os.environ.get('SMTP_SERVER'),
    'smtp_port': os.environ.get('SMTP_PORT'),
    'smtp_user': os.environ.get('SMTP_USER'),
    'smtp_pass': os.environ.get('SMTP_PASS'),
    'mail_to': os.environ.get('MAIL_TO')
}
