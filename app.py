from flask import Flask, render_template, flash, session, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import create_table
import datetime


app = Flask(__name__)
create_table.create_table()

def connect_database():
  db = sqlite3.connect('database.db')
  db.row_factory = sqlite3.Row
  cursor = db.cursor()
  return cursor, db

def close_database(cursor, db):
  cursor.close()
  db.close()


# Главная страница сайта
@app.route('/index/')
@app.route('/')
def index():
  connect_database()
  cursor, db = connect_database()
  cursor.execute('SELECT * FROM blog')
  blogs = cursor.fetchall()
  close_database(cursor, db)
  if blogs == []:
    return render_template('index.html', blogs = None, my_title = 'My Blog')
  else:
    return render_template('index.html', blogs = blogs, my_title = 'My Blog')
  

# Страница сайта About
@app.route('/about/')
def about():
  return render_template('about.html', my_title = 'About')


# Вывод выбранного поста (Blogs)
@app.route('/blogs/<int:id>/')
def blogs(id):
  cursor, db = connect_database()
  cursor.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
  blog = cursor.fetchone()
  close_database(cursor, db)
  if blog is None:
    return 'Blog Is Not Found'
  else:
    return render_template('blogs.html', blog = blog, my_title = 'Blogs')


# Регистрация пользователя
@app.route('/register/', methods = ['GET', 'POST'])
def register():
  if request.method == 'POST':
    user_details = request.form
    username = user_details['username']
    # Проверяем существование пользователя с таким же username
    cursor, db = connect_database()
    cursor.execute("SELECT username FROM user WHERE username = ?", [username])
    user = cursor.fetchone()
    if user is not None:
      flash('User Is Already Exist!')
      return redirect(url_for('register'))
    # Сверяем введенный и подтвержденный пароли
    if user_details['password'] != user_details['confirm__password']:
      flash('Passwords do not match! Try again!')
      return render_template('register.html', my_title = 'Registration')
    values = [user_details['firstname'], 
              user_details['lastname'], 
              user_details['username'], 
              user_details['email'],
              # Шифрование пароля
              generate_password_hash(user_details['password'])]
    cursor, db = connect_database()
    cursor.execute("""INSERT INTO user(first_name, last_name, username, email, password) VALUES (?, ?, ?, ?, ?)""", values)
    db.commit()
    close_database(cursor, db)
    flash('Registration Successfull! Please Login')
    return redirect(url_for('login'))
  return render_template('register.html', my_title = 'Registration')


# Вход в личный кабинет
@app.route('/login/', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    user_details = request.form
    username = user_details['username']
    password = user_details['password']
    cursor, db = connect_database()
    cursor.execute("SELECT * FROM user WHERE username = ?", [username])
    user = cursor.fetchone()
    close_database(cursor, db)
    # Проверка существования пользователя
    if user is None:
      flash('User Does Not Exist!')
      return redirect(url_for('login'))
    else:
      # Сверка пароля
      if not check_password_hash(user['password'], password):
        flash("The Password Is Incorrect")
        return redirect(url_for('login'))
      else:
        # Создание сессии
        session['username'] = user['username']
        session['first_name'] = user['first_name']
        session['last_name'] = user['last_name']
        flash('Welcome ' + session['first_name'] + '! You Have Been Succecessfully Logged In!!!')
        return redirect(url_for('index'))
  return render_template('login.html', my_title = 'Login')


# Создание нового поста (write blog)
@app.route('/write-blog/', methods = ['GET', 'POST'])
def write_blog():
  if(session):
    if request.method == 'POST':
      blogpost = request.form
      title = blogpost['title']
      author = session['first_name'] + ' ' + session['last_name']
      username = session['username']
      body = blogpost['body']
      current_date = datetime.datetime.now()
      current_date_string = current_date.strftime('%d.%m.%y %H:%M:%S')
      cursor, db = connect_database()
      cursor.execute("INSERT INTO blog (title, author, username, body, datetime) VALUES (?, ?, ?, ?, ?)", (title, author, username, body, current_date_string))
      db.commit()
      close_database(cursor, db)
      flash("Your Blogpost Is Successfully Posted!")
      return redirect(url_for('index'))
    return render_template('write-blog.html', my_title = 'New Blog')
  else:
    return redirect(url_for('login'))


# Просмотр моих записей постов (my blogs)
@app.route('/my-blogs/')
def my_blogs():
  if(session):
    username = session['username']
    cursor, db = connect_database()
    cursor.execute("SELECT * FROM blog WHERE username = ?", [username])
    blogs = cursor.fetchall()
    close_database(cursor, db)
    if blogs == {}:
      return render_template('my-blogs.html', blogs = None, my_title = 'My Blogs')
    else:
      return render_template('my-blogs.html', blogs = blogs, my_title = 'My Blogs')
  return redirect(url_for('login'))


# Редактирование поста (edit blog)
@app.route('/edit-blog/<int:id>', methods = ['GET', 'POST'])
def edit_blog(id):
  if(session):
    if request.method == 'POST':
      cursor, db = connect_database()
      title = request.form['title']
      body = request.form['body']
      current_date = datetime.datetime.now()
      current_date_string = current_date.strftime('%d.%m.%y %H:%M:%S')
      cursor.execute("UPDATE blog SET title = ?, body = ?, datetime = ? WHERE blog_id = ?", (title, body, current_date_string, id))
      db.commit()
      close_database(cursor, db)
      flash('Blog Is Updated Successfully!')
      return redirect(url_for('my_blogs'))
    cursor, db = connect_database()
    cursor.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    blog = cursor.fetchone()
    close_database(cursor, db)
    return render_template('edit-blog.html', blog = blog, my_title = 'Edit Blog')
  return redirect(url_for('login'))


# Удаление поста (delete blog)
@app.route('/delete-blog/<int:id>')
def delete_blog(id):
  if(session):
    cursor, db = connect_database()
    cursor.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    db.commit()
    close_database(cursor, db)
    flash('Your Blog Has Been Deleted!')
    return redirect(url_for('my_blogs'))
  else:
    return redirect(url_for('login'))


# Выход из личного кабинета (logout)
@app.route('/logout/')
def logout():
  if(session):
    session.clear()
    flash('You Have Been Logged Out!')
    return redirect(url_for('login'))
  return redirect(url_for('login'))


# Ошибка 404
@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html', my_title = 'Error')


if __name__ == '__main__':
  app.secret_key = os.urandom(24)
  app.run(debug = True)


# Added changes 2 01092023