import os
import psycopg2
from flask import Flask, jsonify

os.environ["DD_DBM_PROPAGATION_MODE"] = "full"

app = Flask(__name__)

# Set up the database connection
conn = psycopg2.connect(
    host= "127.0.0.1",
    port= "5466",
    dbname= "enum_db",
    user= "enum",
    password= "enum"
)

@app.route('/apm-dbm')
def index():
    # Query the database for all rows in a table
    cur = conn.cursor()
    cur.execute("SELECT * FROM hosts")
    rows = cur.fetchall()
    
    # Convert the rows to a list of dictionaries
    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'name': row[1],
            'ip_address': row[2],
            # Add additional fields as needed
        })
    
    # Return the result as JSON
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
