import pymysql
import re

class Database():
    def __init__(self, db_host: str, db_port: int, db_user: str, db_password: str, db: str, table: str = "inventory"):
        self.conn = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            database=db,
            cursorclass=pymysql.cursors.Cursor,
            autocommit=True
        )
        self.table = table
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{table}`(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL,
            who TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            here BOOLEAN DEFAULT TRUE
        );""")

    def add_item(self, name: str):
        self.cursor.execute(f"INSERT INTO `{self.table}` (name) VALUES (%s)", (name,))
    def edit_item(self, id, name):
        self.cursor.execute(f"UPDATE `{self.table}` SET name=%s WHERE id=%s", (name, id))
    def got_back(self, id):
        self.cursor.execute(f"UPDATE `{self.table}` SET here=TRUE, who=NULL, date=CURRENT_TIMESTAMP WHERE id=%s",(id,))
    def lend(self, id, who):
        self.cursor.execute(f"UPDATE `{self.table}` SET here=FALSE, who=%s, date=CURRENT_TIMESTAMP WHERE id=%s",(who, id))
    def delete_item(self, id):
        self.cursor.execute(f"DELETE FROM `{self.table}` WHERE id=%s", (id,))
    def get_items(self, search_query: str | None = None, filter: str | None = None):
        sql_statement = f"SELECT * FROM `{self.table}`"
        conditions = []
        params = []
        if filter == "IN":conditions.append("here = TRUE")
        elif filter == "OUT":conditions.append("here = FALSE")
        if search_query:
            conditions.append("(name LIKE %s OR who LIKE %s)")
            params.append(f"%{search_query}%")
            params.append(f"%{search_query}%")
        if conditions:sql_statement += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(sql_statement, tuple(params))
        return self.cursor.fetchall()

def parse_grants(grants):
    permissions = {}
    grant_regex = re.compile(r"GRANT (.+?) ON (.+?) TO", re.IGNORECASE)
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
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.Cursor
        )

        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        if database not in databases:return Exception("Database doesn't exist!")
        cursor.execute("SHOW GRANTS FOR CURRENT_USER")
        parsed = parse_grants([row[0] for row in cursor.fetchall()])
        if f"{database}.*" not in parsed or "ALL" not in parsed[f"{database}.*"]:
            return PermissionError("User needs to have all permissions to the database!")
        return "Success"
    except pymysql.MySQLError as err:return err
    finally:
        try:connection.close()
        except:pass