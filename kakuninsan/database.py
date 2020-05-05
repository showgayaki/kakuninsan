from mysql import connector


class TableIp:
    def __init__(self, db_dict, table_name):
        self.RECORD_LIMIT_HOUR = 24
        self.db_dict = db_dict.copy()
        self.table_name = table_name

    def fetch_last_ip(self, clm_created_at):
        # 直近24時間分取得
        sql = 'SELECT * FROM {} WHERE DATE_ADD({}, INTERVAL {} HOUR) > NOW()'.format(
            self.table_name, clm_created_at, self.RECORD_LIMIT_HOUR
        )

        conn = connector.connect(**self.db_dict)
        cur = conn.cursor()

        try:
            cur.execute(sql)
            records = cur.fetchall()
            last_records = [list(record) for record in reversed(records)]
        except connector.Error as e:
            return 'Error: {}'.format(e)
        finally:
            cur.close()
            conn.close()

        return last_records

    def insert_record(self, db_info, clm_dict, data_dict):
        sql = ("INSERT INTO {database}.{table_name} "
               "({clm_computer_name}, {clm_global_ip_address}, {clm_download}, {clm_upload}"
               ", {clm_image_url}, {clm_created_at}, {clm_updated_at})"
               " VALUES ('{computer_name}', '{global_ip_address}', {download}"
               ", {upload}, '{image_url}', '{created_at}', '{updated_at}')").format(
            **db_info, **clm_dict, **data_dict)

        conn = connector.connect(**self.db_dict)
        cur = conn.cursor()

        try:
            cur.execute(sql)
            conn.commit()
            return 'Succeeded'
        except connector.Error as e:
            return 'Error: {}'.format(e)
        finally:
            cur.close()
            conn.close()
