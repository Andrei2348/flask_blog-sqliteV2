import sqlite3


def create_table():
  with sqlite3.connect("database.db") as db:
    cursor = db.cursor()

  query = """
    CREATE TABLE IF NOT EXISTS user(
      user_id INTEGER PRIMARY KEY,
      first_name VARCHAR(20) NOT NULL,
      last_name VARCHAR(20) NOT NULL,
      username VARCHAR(20) UNIQUE NOT NULL,
      email VARCHAR(30) NOT NULL,
      password VARCHAR(200) NOT NULL
    );



    CREATE TABLE IF NOT EXISTS blog(
      blog_id INTEGER PRIMARY KEY,
      title VARCHAR(100) NOT NULL,
      author VARCHAR(20) NOT NULL,
      username VARCHAR(50) NOT NULL,
      body VARCHAR(1000) NOT NULL,
      dateTime text VARCHAR NOT NULL
    )
  """

  cursor.executescript(query)