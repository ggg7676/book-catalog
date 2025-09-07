#Book catalog api

import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("books.db")
    connection.row_factory = sqlite3.Row
    return connection

@app.route("/init")
def init_db():
    connection = get_db_connection()
    connection.execute("""
                        CREATE TABLE IF NOT EXISTS Books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL
                       )
                       """)
    connection.commit()
    connection.close()
    return jsonify({"message": "Database initialization complete."})



#get all the books in the catalog
@app.route("/books", methods=["GET"])
def get_all_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    all_books = cursor.execute("SELECT * FROM Books").fetchall()
    connection.close()
    return jsonify([{"id": book["id"], 
                     "title" : book["title"], 
                     "author" : book["author"]} 
                     for book in all_books])


#get a epcific book by id
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    book = cursor.execute("SELECT * FROM Books WHERE id = ?", (book_id,)).fetchone()
    connection.close()

    if book is None:
        return jsonify({"error" : "Book not found"}), 404
    
    return jsonify({"id" : book["id"], "title" : book["title"], "author" : book["author"]})

    
#add a new book
@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return jsonify({"message" : "The book must have a title and an author."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO Books (title, author) VALUES (?, ?)", (title, author))
        connection.commit()
        connection.close()
    except Exception as e:
        return jsonify({"message" : str(e)}), 400
    
    return jsonify({"message" : "Book added successfully"}), 201


#update the info for an existing book
@app.route("/books/<int:book_id>", methods=["PATCH"])
def update_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    book = cursor.execute("SELECT * FROM Books WHERE id = ?", (book_id,)).fetchone()
    
    if book is None:
        return jsonify({"error" : "Book not found"}), 404
    
    data = request.get_json()
    #whichever one is changed will get the updated value
    title = data.get("title", book["title"])
    author = data.get("author", book["author"])

    try:
        cursor.execute("UPDATE Books SET title = ?, author = ? WHERE id = ?", (title, author, book_id))
    except Exception as e:
        return jsonify({"message" : str(e)}), 400

    connection.commit()
    connection.close()

    return jsonify({"message" : "Book info updated successfully"}), 200


#delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    book = cursor.execute("SELECT * FROM Books WHERE id = ?", (book_id,)).fetchone()
    
    if book is None:
        return jsonify({"error" : "Book not found"}), 404
    
    try:
        cursor.execute("DELETE FROM Books WHERE id = ?", (book_id,))
    except Exception as e:
        return jsonify({"message" : str(e)}), 400
    
    connection.commit()
    connection.close()

    return jsonify({"message" : "Book deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)

