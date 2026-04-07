import mysql.connector
from mysql.connector import Error
import re
class Database():
    def __init__(self,db_host:string,db_port:int,db_user:string,db_password:string,db:string,table:string="inventory"):
        self.conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db,
        )
        self.table = table
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table}(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL,
            who TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            here BOOLEAN DEFAULT TRUE);
            """)
    
    def add_item(self,name:string):
        self.cursor.execute(f"INSERT INTO {self.table} (name) VALUES (%s)",[name,])
        self.conn.commit()
    def edit_item(self,id,name):
        self.cursor.execute(f"UPDATE {self.table} SET name=%s WHERE id = %s",[name,id])
        self.conn.commit()
    def got_back(self,id):
        self.cursor.execute(f"UPDATE {self.table} SET here=TRUE, who=NULL, date = CURRENT_TIMESTAMP WHERE id = %s",[id,])
        self.conn.commit()
    def lend(self,id,who):
        self.cursor.execute(f"UPDATE {self.table} SET here=FALSE, who=%s, date = CURRENT_TIMESTAMP WHERE id = %s",[who,id])
        self.conn.commit()
    def delete_item(self,id):
        self.cursor.execute(f"DELETE FROM {self.table} WHERE id = %s",[id,])
        self.conn.commit()
    def get_items(self, search_query: str | None = None, filter: str | None = None):
        sql_statement = f"SELECT * FROM `{self.table}`"
        conditions = []
        params = []
        if filter == "IN":conditions.append("here = TRUE")
        elif filter == "OUT":conditions.append("here = FALSE")
        if search_query:
            conditions.append("name LIKE %s OR who LIKE %s")
            params.append(f"%{search_query}%")
            params.append(f"%{search_query}%")
        if conditions:
            sql_statement += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(sql_statement, tuple(params))
        return self.cursor.fetchall()


def parse_grants(grants):
    permissions = {}
    grant_regex = re.compile(r"GRANT (.+?) ON (.+?) TO",re.IGNORECASE)
    for grant in grants:
        match = grant_regex.search(grant)
        if not match:continue
        perms_part, scope = match.groups()
        scope = scope.replace("`", "").strip()
        perms = {p.strip().upper() for p in perms_part.split(",")}
        if "ALL PRIVILEGES" in perms:perms = {"ALL"}
        if scope not in permissions:permissions[scope] = set()
        permissions[scope].update(perms)
    return permissions

def check_mysql_connection(host, user, password, database, port):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            if database not in databases:
                return Error("Database doesn't exist!")
            cursor.execute("SHOW GRANTS FOR CURRENT_USER")
            parsed = parse_grants([row[0] for row in cursor.fetchall()])
            if not "ALL" in parsed[f"{database}.*"]:
                return PermissionError("User needs to have all permissions to the database!")
            return "Success"

    except mysql.connector.Error as err:return err
    finally:
        if 'connection' in locals() and connection.is_connected():connection.close()

