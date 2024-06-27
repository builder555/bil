import sqlite3
def sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBAdaptor:
    
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name, isolation_level=None)
        self.con.row_factory = sqlite_dict_factory
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.close()

    def __read(self, sql):
        query = self.cur.execute(sql)
        return query.fetchall()
    
    def __insert(self, sql):
        self.cur.execute(sql)
        return self.cur.lastrowid
    
    def __modify(self, sql):
        rows_affected = self.cur.execute(sql).rowcount
        return rows_affected
        
    def get_projects(self):
        sql = 'SELECT `id`, `name` FROM `projects`'
        return self.__read(sql)

    def add_project(self, name):
        sql = f'INSERT INTO `projects`(`name`) VALUES("{name}")'
        return self.__insert(sql)

    def update_project(self, project_id, details):
        sql = f"""
                UPDATE `projects`
                SET `name`='{details['name']}'
                WHERE `id`={project_id}"""
        return self.__modify(sql)

    def delete_project(self, project):
        sql = f'DELETE FROM `projects` WHERE `id`={project}'
        return self.__modify(sql)

    def get_paygroups(self, project: int):
        sql = f"""
                SELECT
                    paygroups.id,
                    paygroups.project,
                    paygroups.name,
                    CASE
                        WHEN (paysums.totalamount IS NULL) THEN 0
                        ELSE paysums.totalamount
                    END AS `total`,
                    CASE
                        WHEN (paysums.totalowed IS NULL) THEN 0
                        ELSE paysums.totalowed
                    END AS `owed`
                FROM
                    `paygroups` 
                    LEFT JOIN (
                        SELECT
                            SUM(`amount`) AS `totalamount`,
                            SUM(`owed`) AS `totalowed`,
                            `paygroup`
                        FROM
                            `payments`
                        GROUP BY
                            `paygroup`
                    ) AS `paysums` ON paygroups.id = paysums.paygroup
                WHERE
                    paygroups.project = {project}
                """
        return self.__read(sql)

    def add_payment_group(self, data):
        sql = f'INSERT INTO `paygroups`(`name`,`project`) VALUES(\'{data["name"]}\',{data["project"]})'
        return self.__insert(sql)

    def delete_group(self, group_id):
        sql = f'DELETE FROM `paygroups` WHERE `id`={group_id}'
        return self.__modify(sql)

    def update_group(self, group_id, details):
        sql = f"""
                UPDATE `paygroups`
                SET `name`='{details['name']}', `project`={details['project']} 
                WHERE `id`={group_id}"""
        print('updating', sql)
        return self.__modify(sql)

    def get_payments(self, paygroup: int):
        sql = f"""
                SELECT 
                    `id`,
                    `name`,
                    `when`,
                    `amount`,
                    `owed`,
                    `paygroup`
                FROM `payments` 
                WHERE `paygroup`= {paygroup}"""
        return self.__read(sql)

    def add_payment(self, data):
        sql = f"""
                INSERT INTO `payments`(
                    `name`,
                    `when`,
                    `paygroup`,
                    `amount`,
                    `owed`
                ) 
                VALUES(
                        '{data['name']}',
                        '{data['when']}',
                        {data['paygroup']},
                        {data['amount']},
                        {data['owed']}
                    )
                """
        return self.__insert(sql)

    def update_payment(self, pay_id, data):
        sql = f"""
                UPDATE `payments`
                SET
                    `name` = '{data['name']}',
                    `when` = '{data['when']}',
                    `paygroup` = {data['paygroup']},
                    `amount` = {data['amount']},
                    `owed` = {data['owed']}
                WHERE `id`={pay_id}"""
        return self.__modify(sql)

    def delete_payment(self, payment):
        sql = f'DELETE FROM `payments` WHERE `id`={payment}'
        return self.__modify(sql)

    def export_json(self):
        sql = 'SELECT * FROM `payments`'
        payments = {str(p['id']): p for p in self.__read(sql)}
        sql = 'SELECT * FROM `paygroups`'
        paygroups = {str(p['id']): {**p, 'payments': []} for p in self.__read(sql)}
        sql = 'SELECT * FROM `projects`'
        projects = {str(p['id']): {**p, 'groups': []} for p in self.__read(sql)}
        print(paygroups)
        for _, pay in payments.items():
            group_id = str(pay['paygroup'])
            if group_id in paygroups:
                paygroups[group_id]['payments'].append(pay)

        for _, group in paygroups.items():
            project_id = str(group['project'])
            if project_id in projects:
                projects[project_id]['groups'].append(group)

        return projects
