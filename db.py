import pymysql

def get_connection():
    return pymysql.connect(host="localhost" ,user="root", password="Passwordmonenei", database="fc_database", port=3306, cursorclass=pymysql.cursors.DictCursor)