from flask import Flask, jsonify
import pyodbc

app = Flask(__name__)

# Configure the database connection string for SQL Server
# Replace DRIVER={SQL Server};SERVER=YOUR_HOST;DATABASE=YOUR_DB;UID=YOUR_USER-ID;PWD=YOUR_PASSWORD
connection_string = 'DRIVER={SQL Server};SERVER=MSI\\SQLEXPRESS;DATABASE=edz;UID=snasi;PWD=admin'

# Test the database connection
@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        conn = pyodbc.connect(connection_string)
        conn.close()
        return jsonify({"message": "Database connection successful."}), 200
    except pyodbc.Error as ex:
        return jsonify({"error": str(ex)}), 500

if __name__ == '__main__':
    app.run(debug=True)
