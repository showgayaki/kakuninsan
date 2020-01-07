from mysql import connector


class TableIp:
    def __init__(self, db_dict, table_name):
        self.db_dict = db_dict.copy()
        self.table_name = table_name

    def fetch_last_ip(self, clm_created_at):
        # 最新の一件取得
        sql = 'SELECT * FROM {} ORDER BY {} DESC LIMIT 1'.format(self.table_name, clm_created_at)

        conn = connector.connect(**self.db_dict)
        cur = conn.cursor()

        try:
            cur.execute(sql)
            last_ip = cur.fetchone()[1]
        except connector.Error as e:
            return 'Error:{}'.format(str(e))
        finally:
            cur.close()
            conn.close()

        return last_ip

    def insert_record(self, sql_dict):
        sql = "INSERT INTO {database}.{table_name} " \
              "({clm_computer_name}, {clm_global_ip}, {clm_created_at}, {clm_updated_at}) "\
              "VALUES ('{computer_name}', '{global_ip}', '{created_at}', '{updated_at}')".format(**sql_dict)

        conn = connector.connect(**self.db_dict)
        cur = conn.cursor()

        try:
            cur.execute(sql)
            conn.commit()
            return 'Succeeded'
        except connector.Error:
            return 'Failed'
        finally:
            cur.close()
            conn.close()

