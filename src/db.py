import mysql.connector
from mysql.connector import Error
import re
class Database():
    def __init__(self,db_host:string,db_user:string,db_password:string,db:string,table:string="inventory"):
        self.conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            datasabe=db
        )
        self.table = table
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ? (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL,
            who TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            here BOOLEAN DEFAULT TRUE
        );""", (table))
    
    def add_item(name:string):self.cursor.execute("INSERT INTO ? (name) VALUES (?)",(self.table,name))



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
            print(f"Successfully connected to MySQL server at {host}")
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
