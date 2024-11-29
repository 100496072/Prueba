import sqlite3 as sql


def insert_letter(letter, sender, correo, city, country, firma, letter_time):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO letters (nombre, correo, ciudad, pais, carta, sign, date) VALUES (?,?,?,?,?,?,?)""", (sender, correo, city, country,letter, firma, letter_time))
    conn.commit()
    conn.close()


def get_letter(sender, letter_time):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM letters WHERE (nombre = ? AND date = ?)""", (sender, letter_time))
    return cursor.fetchone()
