import os
from dotenv import load_dotenv
from pathlib import Path


def config(root_dir):
    dotenv_path = Path(root_dir).resolve().joinpath('.env')
    load_dotenv(dotenv_path)
    conf = {
        'db_info': {
            'host': os.environ.get('DB_HOST')
            , 'database': os.environ.get('DB_NAME')
            , 'user': os.environ.get('DB_USER')
            , 'password': os.environ.get('DB_PASS')
        }
        , 'table_detail': {
            'table_name': os.environ.get('TABLE_NAME')
            , 'clm_computer_name': os.environ.get('CLM_COMPUTER_NAME')
            , 'clm_global_ip_address': os.environ.get('CLM_GLOBAL_IP_ADDRESS')
            , 'clm_download': os.environ.get('CLM_DOWNLOAD')
            , 'clm_upload': os.environ.get('CLM_UPLOAD')
            , 'clm_sponsor': os.environ.get('CLM_SPONSOR')
            , 'clm_image_url': os.environ.get('CLM_IMAGE_URL')
            , 'clm_created_at': os.environ.get('CLM_CREATED_AT')
            , 'clm_updated_at': os.environ.get('CLM_UPDATED_AT')
        }
        , 'interval_hour': os.environ.get('INTERVAL_HOUR')
        , 'mail_info': {
            'smtp_server': os.environ.get('SMTP_SERVER')
            , 'smtp_port': os.environ.get('SMTP_PORT')
            , 'smtp_user': os.environ.get('SMTP_USER')
            , 'smtp_pass': os.environ.get('SMTP_PASS')
            , 'mail_to': os.environ.get('MAIL_TO')
        }
        , 'mail_send_time': os.environ.get('MAIL_SEND_TIME')
        , 'web_server': {
            'is_running': True if os.environ.get('IS_RUNNING_WEB_SERVER') == 'True' else False
            , 'document_root': os.environ.get('DOCUMENT_ROOT')
        }
        , 'line': {
            'api_url': os.environ.get('API_URL')
            , 'access_token': os.environ.get('ACCESS_TOKEN')
            , 'post_time': os.environ.get('LINE_POST_TIME')
        }
    }
    return conf
