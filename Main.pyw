#imports
from tkinter import *
from tkinter.font import Font
from tkinter import ttk
from time import sleep
import webbrowser
import subprocess
import threading
import sqlite3
import os

#version
version = "Beta 0.3"

#file path
path=os.path.realpath(__file__)
path = path.split("\\")
folder = ""
file = ""
for i in range(len(path)):
    if i == len(path) - 1:
        file = path[i]
    else:
        folder += path[i] + "\\"
os.chdir(folder)

#connect with the SQL database
dbconn = sqlite3.connect("database\\Free Games.db")
db = dbconn.cursor()



#<===FUNCTIONING===>

#executes the app
def execute():
    os.startfile(f'"{folder}database\\Free Games Notifier.exe"')

appThread = threading.Thread(target=execute)

#executes the notifier
def notifier():
    db.execute("SELECT activated FROM settings WHERE id=1;")
    activated = db.fetchone()
    if int(activated[0]) == 0:
        saveButton.config(state=DISABLED)
        db.execute("UPDATE settings SET activated=1 WHERE id=1;")
        dbconn.commit()
        appThread.start()
        sleep(4)
        powerButtonVar.set("STOP")
    elif int(activated[0]) == 1:
        saveButton.config(state=NORMAL)
        db.execute("UPDATE settings SET activated=0 WHERE id=1;")
        dbconn.commit()
        sleep(3)
        powerButtonVar.set("START")

#saves the startup value
def saveStartup():
    start = startupVar.get()
    if start == 0:
        db.execute("UPDATE settings SET activated=0 WHERE id=2;")
        dbconn.commit()
    if start == 1:
        db.execute("UPDATE settings SET activated=1 WHERE id=2;")
        dbconn.commit()
    #--------------------------------------------------------------------------------------------CODE FOR STARTUP----------------------------

#change the names of the games buttons
def changeNameValues():
    db.execute("SELECT name, seen FROM games WHERE id=1;")
    data = db.fetchone()
    name = data[0]
    seen = data[1]
    dbconn.commit()
    firstNameVar.set(f"{str(name)}")
    if seen == 1:
        firstLink.config(fg=lightgray, activeforeground=lightgray)
    else:
        firstLink.config(fg=main, activeforeground=main)

    db.execute("SELECT name, seen FROM games WHERE id=2;")
    data = db.fetchone()
    name = data[0]
    seen = data[1]
    dbconn.commit()
    secondNameVar.set(f"{str(name)}")
    if seen == 1:
        secondLink.config(fg=lightgray, activeforeground=lightgray)
    else:
        secondLink.config(fg=main, activeforeground=main)

    db.execute("SELECT name, seen FROM games WHERE id=3;")
    data = db.fetchone()
    name = data[0]
    seen = data[1]
    dbconn.commit()
    thirdNameVar.set(f"{str(name)}")
    if seen == 1:
        thirdLink.config(fg=lightgray, activeforeground=lightgray)
    else:
        thirdLink.config(fg=main, activeforeground=main)

    db.execute("SELECT name, seen FROM games WHERE id=4;")
    data = db.fetchone()
    name = data[0]
    seen = data[1]
    dbconn.commit()
    fourthNameVar.set(f"{str(name)}")
    if seen == 1:
        fourthLink.config(fg=lightgray, activeforeground=lightgray)
    else:
        fourthLink.config(fg=main, activeforeground=main)

    db.execute("SELECT name, seen FROM games WHERE id=5;")
    data = db.fetchone()
    name = data[0]
    seen = data[1]
    dbconn.commit()
    fifthNameVar.set(f"{str(name)}")
    if seen == 1:
        fifthLink.config(fg=lightgray, activeforeground=lightgray)
    else:
        fifthLink.config(fg=main, activeforeground=main)

#opens the link of the button pressed
def openLink(num):
    if num == 0:
        webbrowser.open("https://indiegamebundles.com/category/free/", new=2, autoraise=True)

    elif num != 0:
        db.execute(f"SELECT link FROM games WHERE id={num};")
        link = db.fetchone()
        dbconn.commit()
        webbrowser.open(str(link[0]), new=2, autoraise=True)
        db.execute(f"UPDATE games SET seen=1 WHERE id={num};")
        dbconn.commit()

    changeNameValues()



#<===GUI===>

#color variables
black = "#101010"
gray = "#1a1a1a"
lightgray = "#999999"
white = "#ffffff"
pink = "#ff0066"
green = "#00ffaa"
purple = "#7b00ff"
back = gray
secondary = black
main = white
accent = pink

#create tkinter
root = Tk()

#change title, icon and background of the gui
root.title(f"Free Games Notifier (v: {version})")
root.iconbitmap("resources\\icon.ico")
root.resizable(False, False)
root.configure(bg=back)

#center the window on the screen
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
root.geometry(f"784x347+{(screenWidth//2)-(784//2)}+{(screenHeight//2)-(347//2)}")

#convert units to pixels
pixelVirtual = PhotoImage(width=1, height=1)

#add the nexa font
nexaBold = Font(family="Nexa-Bold", size=15)
nexaRegular = Font(family="Nexa-Regular", size=12)

#settings
powerButtonVar = StringVar()
powerButtonVar.set("START")
powerButton = Button(root, textvariable=powerButtonVar, command=notifier, image=pixelVirtual, compound="c", width=300, height=70, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaBold).grid(row=0, column=0, padx=30, pady=(30, 15))

settingsFrame = LabelFrame(root, background=back, relief=FLAT, padx=0, pady=0)
settingsFrame.grid(row=1, column=0, padx=30, pady=(15, 30))

startupVar = IntVar()
startup = Checkbutton(settingsFrame, text="Start On Startup", variable=startupVar, bg=back, fg=accent, activebackground=back, activeforeground=accent, selectcolor=secondary, font=nexaRegular).grid(row=0, column=0, padx=0, pady=11)

saveButton = Button(settingsFrame, text="Save", command=saveStartup, image=pixelVirtual, compound="c", width=150, height=40, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaBold)
saveButton.grid(row=1, column=0, padx=0, pady=(10, 30))

wattermarkVar = StringVar()
wattermarkVar.set("Made By Jayex Designs")
wattermark = Label(settingsFrame, textvariable=wattermarkVar, bg=back, fg=main, font=nexaRegular).grid(row=2, column=0, padx=0, pady=(10, 0))

#separator
separator = ttk.Separator(root, orient=VERTICAL).grid(row=0, column=1, rowspan=5, sticky="ns", pady=50)

#links
allFreeButton = Button(root, text="ALL\nFREE GAMES", command=lambda:openLink(0), image=pixelVirtual, compound="c", width=170, height=70, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaBold).grid(row=0, column=2, columnspan=1, padx=(30, 5), pady=(30, 15))

updateButton = Button(root, text="UPDATE", command=changeNameValues, image=pixelVirtual, compound="c", width=170, height=70, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaBold).grid(row=0, column=3, columnspan=1, padx=(5, 30), pady=(30, 15))

linksFrame = LabelFrame(root, background=back, relief=FLAT, padx=0, pady=0)
linksFrame.grid(row=1, column=2, columnspan=2, padx=30, pady=(15, 30))

firstNameVar = StringVar()
firstNameVar.set("First Link")
firstLink = Button(linksFrame, textvariable=firstNameVar, command=lambda:openLink(1), image=pixelVirtual, compound="c", anchor="w", padx=8, width=335, height=25, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaRegular)
firstLink.grid(row=0, column=0, padx=0, pady=(0, 5))

secondNameVar = StringVar()
secondNameVar.set("Second Link")
secondLink = Button(linksFrame, textvariable=secondNameVar, command=lambda:openLink(2), image=pixelVirtual, compound="c", anchor="w", padx=8, width=335, height=25, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaRegular)
secondLink.grid(row=1, column=0, padx=0, pady=(0, 5))

thirdNameVar = StringVar()
thirdNameVar.set("Third Link")
thirdLink = Button(linksFrame, textvariable=thirdNameVar, command=lambda:openLink(3), image=pixelVirtual, compound="c", anchor="w", padx=8, width=335, height=25, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaRegular)
thirdLink.grid(row=2, column=0, padx=0, pady=(0, 5))

fourthNameVar = StringVar()
fourthNameVar.set("Fourth Link")
fourthLink = Button(linksFrame, textvariable=fourthNameVar, command=lambda:openLink(4), image=pixelVirtual, compound="c", anchor="w", padx=8, width=335, height=25, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaRegular)
fourthLink.grid(row=3, column=0, padx=0, pady=(0, 5))

fifthNameVar = StringVar()
fifthNameVar.set("Fifth Link")
fifthLink = Button(linksFrame, textvariable=fifthNameVar, command=lambda:openLink(5), image=pixelVirtual, compound="c", anchor="w", padx=8, width=335, height=25, bg=secondary, fg=main, activebackground=back, activeforeground=main, borderwidth=0, font=nexaRegular)
fifthLink.grid(row=4, column=0, padx=0, pady=(0, 5))

#update text values
changeNameValues()

db.execute("SELECT activated FROM settings WHERE id=1;")
activated = db.fetchone()
if int(activated[0]) == 0:
    powerButtonVar.set("START")
    saveButton.config(state=NORMAL)
elif int(activated[0]) == 1:
    powerButtonVar.set("STOP")
    saveButton.config(state=DISABLED)

db.execute("SELECT activated FROM settings WHERE id=2;")
activated = db.fetchone()
if int(activated[0]) == 0:
    startupVar.set(0)
elif int(activated[0]) == 1:
    startupVar.set(1)

#execute tkinter window
root.mainloop()