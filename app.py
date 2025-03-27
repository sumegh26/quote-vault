from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import time

app = Flask(__name__)

# Database connection function with retry
def get_db_connection():
    for _ in range(10):  # Retry up to 10 times
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database=os.getenv("DB_NAME", "quotes"),
                user=os.getenv("DB_USER", "admin"),
                password=os.getenv("DB_PASSWORD", "secret")
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"DB not ready yet: {e}. Retrying in 2 seconds...")
            time.sleep(2)
    raise Exception("Failed to connect to database after retries")

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quotes", methods=["GET"])
def get_quotes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, author FROM quotes")
    quotes = [{"id": row[0], "text": row[1], "author": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(quotes)

@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quotes (text, author) VALUES (%s, %s)", (data["text"], data["author"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote added"}), 201

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def update_quote(quote_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE quotes SET text = %s, author = %s WHERE id = %s", 
                   (data["text"], data["author"], quote_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote updated"})

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = %s", (quote_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote deleted"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)