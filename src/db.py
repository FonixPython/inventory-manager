import mysql.connector
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





import mysql.connector
from mysql.connector import Error

def check_mysql_connection(host, user, password, database, table):
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database 
        )
        
        if connection.is_connected():
            print(f"Successfully connected to MySQL server at {host}")
            
            cursor = connection.cursor()
            
            # Check if database exists (optional)
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            if database not in databases:
                print(f"Database '{database}' does not exist.")
                return False
            
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                print(f"Table '{table}' exists and is accessible.")
                return True
            else:
                print(f"Table '{table}' does not exist or access denied.")
                return False

    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Example usage
check_mysql_connection(
    host="localhost",
    user="your_username",
    password="your_password",
    database="your_database",
    table="your_table"
)