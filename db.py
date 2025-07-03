import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="sangamner",
        database="agro",
        cursorclass=pymysql.cursors.DictCursor
    )
