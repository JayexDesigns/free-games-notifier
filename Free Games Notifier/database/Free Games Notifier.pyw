#imports
from bs4 import BeautifulSoup
import win10toast_persist
from time import sleep
import requests
import sqlite3
import os

#create notification
notification = win10toast_persist.ToastNotifier()

#connect with the SQL database
dbconn = sqlite3.connect("database\\Free Games.db")
db = dbconn.cursor()



#assign notification
def notify(game):
    notification.show_toast(game, "All free games are available in indiegamebundles.com/category/free/", icon_path="resources/icon.ico", duration=None, threaded=True)

#creates the games table with the default values
def createGamesTable():
    try:
        db.execute("DROP TABLE games;")
    except:
        pass
    names = ["First", "Second", "Third", "Fourth", "Fifth"]
    db.execute("""CREATE TABLE games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        link TEXT,
        seen INTEGER
        );""")
    for i in range(5):
        db.execute(f"""INSERT INTO games VALUES (
            {i+1}, '{names[i]} Link', 'https://indiegamebundles.com/category/free/', 1
            );""")
        dbconn.commit()

#creates the settings table with the default values
def createSettingsTable():
    try:
        db.execute("DROP TABLE settings;")
    except:
        pass
    db.execute("""CREATE TABLE settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        activated INTEGER
        );""")
    db.execute("""INSERT INTO settings Values (
        1, "Running", 1
        );""")
    db.execute("""INSERT INTO settings Values (
        2, "Startup", 0
        );""")
    db.execute("""INSERT INTO settings Values (
        3, "Path", 0
        );""")
    dbconn.commit()

#checks if the database has a correct info
def checkDatabase():
    db.execute("SELECT * FROM games;")
    dbconn.commit()
    if len(db.fetchall()) == 5:
        pass
    else:
        createGamesTable()

    db.execute("SELECT * FROM settings;")
    dbconn.commit()
    if len(db.fetchall()) == 3:
        pass
    else:
        createSettingsTable()

#get the values of the webpage and saves them in the database if there are new games
def notificator():
    db.execute("SELECT link FROM games WHERE id=1;")
    lastEntry = str(db.fetchone()[0])
    source = requests.get("https://www.indiegamebundles.com/category/free/").text
    soup = BeautifulSoup(source, "lxml")
    links = []
    texts = []
    iterator = 0
    for content in soup.find_all("h3", class_="entry-title td-module-title"):
        if content.a.get("href") != lastEntry and iterator != 5:
            iterator += 1
            links.append(content.a.get("href"))
            texts.append(content.a.text)
        elif content.a.get("href") == lastEntry or iterator == 5:
            break
    if iterator != 0:
        for i in range(iterator):
            db.execute(f"DELETE FROM games WHERE id={5-i};")
            dbconn.commit()
        for i in range(5-iterator):
            i = (5-iterator) - i
            db.execute(f"UPDATE games SET id={i+iterator} WHERE id={i};")
            dbconn.commit()
        for i in range(len(links)):
            db.execute(f"""INSERT INTO games VALUES (
            {i+1}, '{texts[i]}', '{links[i]}', 0
            );""")
            dbconn.commit()
            notify(texts[i])

#execute the app
notification.show_toast("The app is running", "All free games will be notified", icon_path="resources/icon.ico", duration=2, threaded=True)
while True:
    db.execute("SELECT activated FROM settings WHERE id=1;")
    value = db.fetchone()[0]
    if value == 0:
        notification.show_toast("The app is closing", "All free games will no longer be notified", icon_path="resources/icon.ico", duration=2, threaded=True)
        break
    elif value == 1:
        sleep(3)
        checkDatabase()
        try:
            notificator()
        except:
            continue