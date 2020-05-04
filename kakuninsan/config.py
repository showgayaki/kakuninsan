import os
from dotenv import load_dotenv
from pathlib import Path


class Config:
    def __init__(self, current_path):
        dotenv_path = os.path.join(Path(current_path).resolve().parents[0], '.env')
        load_dotenv(dotenv_path)

    @staticmethod
    def config():
        conf = {
            'db_info': {
                'host': os.environ.get('DB_HOST')
                , 'database': os.environ.get('DB_NAME')
                , 'user': os.environ.get('DB_USER')
                , 'password': os.environ.get('DB_PASS')
            },
            'table_detail': {
                'table_name': os.environ.get('TABLE_NAME')
                , 'clm_computer_name': os.environ.get('CLM_COMPUTER_NAME')
                , 'clm_global_ip_address': os.environ.get('CLM_GLOBAL_IP_ADDRESS')
                , 'clm_download': os.environ.get('CLM_DOWNLOAD')
                , 'clm_upload': os.environ.get('CLM_UPLOAD')
                , 'clm_image_url': os.environ.get('CLM_IMAGE_URL')
                , 'clm_created_at': os.environ.get('CLM_CREATED_AT')
                , 'clm_updated_at': os.environ.get('CLM_UPDATED_AT')
            },
            'mail_info': {
                'smtp_server': os.environ.get('SMTP_SERVER')
                , 'smtp_port': os.environ.get('SMTP_PORT')
                , 'smtp_user': os.environ.get('SMTP_USER')
                , 'smtp_pass': os.environ.get('SMTP_PASS')
                , 'mail_to': os.environ.get('MAIL_TO')
            }
        }
        return conf
