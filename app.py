from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("quotes.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)
    conn.close()

# Home route - serves the frontend
@app.route("/")
def index():
    return render_template("index.html")

# API: Get all quotes
@app.route("/quotes", methods=["GET"])
def get_quotes():
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, author FROM quotes")
    quotes = [{"id": row[0], "text": row[1], "author": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(quotes)

# API: Create a quote
@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.json
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quotes (text, author) VALUES (?, ?)", (data["text"], data["author"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote added"}), 201

# API: Update a quote
@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def update_quote(quote_id):
    data = request.json
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE quotes SET text = ?, author = ? WHERE id = ?", 
                   (data["text"], data["author"], quote_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote updated"})

# API: Delete a quote
@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote deleted"})

if __name__ == "__main__":
    init_db()  # Create DB on first run
    app.run(host="0.0.0.0", port=5000, debug=True)