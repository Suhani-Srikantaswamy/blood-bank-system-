from flask import Flask
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'blood_bank_db'
}

@app.route('/')
def test():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return f"<h1>Success! Found {count} hospitals in database</h1>"
    except Exception as e:
        return f"<h1>Database Error: {str(e)}</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5002)