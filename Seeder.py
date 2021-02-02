import sqlite3
import csv
import json as js
import sys
import tkinter as tk
import tkinter.simpledialog



class cfile:
    #subclass file to have a more convienient use of writeline
    def __init__(self, fileName, mode = 'r'):
        self.f = open(fileName, mode)

    def wl(self, string):
        self.f.write(string + '\n')

    def close(self):
        self.f.close()
    
        



#GUI
    

root = tk.Tk()
root.title("Seeder by @NoMeHeVistoFE Alpha1.1")

fr_space = tk.Frame(master=root,width=100,height=50)
fr_space.pack(side=tk.TOP)

fr1 = tk.Frame(master=root,width=100,height=50)
fr1.pack(side=tk.TOP)

fr_fileName = tk.Frame(master=fr1,width=50,height=50)
fr_fileName.pack(side=tk.LEFT)

ent_fileName = tk.Entry(master=fr_fileName)
ent_fileName.insert(0, "Introducir ruta al archivo de jugadores")
ent_fileName.pack()

fr_space = tk.Frame(master=fr1,width=20,height=50)
fr_space.pack(side=tk.LEFT)

fr_DB = tk.Frame(master=fr1,width=50,height=50)
fr_DB.pack(side=tk.LEFT)

ent_DB = tk.Entry(master=fr_DB)
ent_DB.insert(0, "ultimate_player_database.db")
ent_DB.pack(side=tk.LEFT)

on_var = tk.IntVar()
off_var = tk.IntVar()
cb_online = tk.Checkbutton(master=root, text="Use Online results", variable=on_var, onvalue=1, offvalue=0)
cb_online.pack(side=tk.TOP)
cb_offline = tk.Checkbutton(master=root, text="Use Offline results", variable=off_var, onvalue=1, offvalue=0)
cb_offline.pack(side=tk.TOP)

fr_seed = tk.Frame(master=root,width=25,height=25)
fr_seed.pack(side=tk.TOP)
btn_seed = tk.Button(master=fr_seed,text="Start!")
btn_seed.pack()

fr_log = tk.Frame(master=root,width=100,height=100)
fr_log.pack(side=tk.RIGHT)

tx_log = tk.Text(master=fr_log)
tx_log.pack()
tx_log.config(state='disabled')

fr_seed = tk.Frame(master=root,width=100,height=100)
fr_seed.pack(side=tk.RIGHT)

tx_seed = tk.Text(master=fr_seed)
tx_seed.pack()
tx_seed.config(state='disabled')

fails = []
points = {}
logs = cfile('log.txt', 'w')

DB = ent_DB.get()
logs.wl(f"DB: {DB}")

conn = sqlite3.connect(DB)
c = conn.cursor()
logs.wl("Conected to DB succesfully! \n")

#Values for the placings
logs.wl("Values:")
values = {
    1   : 10,
    2   : 8,
    3   : 6,
    4   : 5,
    8   : 4,
    16  : 3,
    32  : 2,
    64  : 1,
    128 : 0.5,
    256 : 0.25,
    512 : 0.125
}
logs.wl(str(values))
logs.wl("")

#Multipliers depending on the number of players

multipliers = {
    16  : 0.5,
    32  : 0.75,
    64  : 1,
    128 : 2,
    256 : 4,
    512 : 8
}
logs.wl("Multipliers:")
logs.wl(str(multipliers))
logs.wl("")


def get_points(placings,player_tag):
    logs.wl("-----------------------------------------------------------")
    logs.wl(str(placings))
    logs.wl("-----------------------------------------------------------")
    #Transform the js to a List of dictionaries
    pl = js.loads(placings[0])
    
    #We will start looking for the results
    #Tournament format:
    #{'key': 'gouken-legacy__gouken-legacy-singles', 'placing': 65, 'seed': 67, 'dq': False}
    provisional_points = []
    for tournament in pl:
        
        #If the player DQ'd we will skip this tournament
        #Later functionality will count them and penalize it
        key = (tournament["key"],)
        logs.wl(f"Torneo: {key[0]}")
        if tournament["dq"] is True:
            logs.wl("DQ, ignoring tournament")
            logs.wl("-----------------------------------------------------------")
            continue
        
        #We get the key of the tournament
        #to see if it's an online/offline one
        
        #For now only online is implemented
        
        
        c.execute('SELECT online FROM tournament_info WHERE key=?',key)
        online = c.fetchone()
        
        #If it's an offline tournament we skip it
        on = on_var.get()
        off = off_var.get()
        logs.wl(f"{online[0]} {str(off)} {str(on)}")
        if online[0] == 0 and off == 0:
            logs.wl("Offline tournament, ignoring it")
            logs.wl("-----------------------------------------------------------")
            continue
        elif online[0] == 1 and on == 0:
            logs.wl("Online tournament, ignoring it")
            logs.wl("-----------------------------------------------------------")
            continue
        
        
        #If it's an online one:
        ## 1. Get the number of entrants
        
        c.execute('SELECT entrants FROM tournament_info WHERE key=?',key)
        n_entrants = c.fetchone()[0]
        logs.wl(f"Nº de entrants: {n_entrants}")
        
        ## 2. Get the seeding
        
        seeding = tournament["seed"]
        logs.wl(f"Seed: {seeding}")
        
        ## 3. Get the placing
        
        placing = tournament["placing"]
        logs.wl(f"Placing: {placing}")
        
        # 4. Get the value and the multiplier
        #Placings
        if not placing > 4:
            value = values[placing]
        elif placing < 8:
            value = values[8]
        elif placing < 16:
            value = values[16]
        elif placing < 32:
            value = values[32]
        elif placing < 64:
            value = values[64]
        elif placing < 128:
            value = values[128]
        elif placing < 256:
            value = values[256]
        elif placing < 512:
            value = values[512]
        else:
            value = 0.05
            #Entrants
        if n_entrants < 16:
            #Ignore tournament
            continue
        elif n_entrants < 32:
            mult = multipliers[16]
        elif n_entrants < 64:
            mult = multipliers[32]
        elif n_entrants < 128:
            mult = multipliers[64]
        elif n_entrants < 256:
            mult = multipliers[128]
        elif n_entrants < 512:
            mult = multipliers[256]
        else:
            mult = multipliers[512]
            
        # 5. Get number of points for this tournament
            
        provisional_points.append(value*mult)
        logs.wl(f"Value: {value}")
        logs.wl(f"Multiplier: {mult}")
        logs.wl(f"Points: {value*mult}")
        logs.wl("-----------------------------------------------------------")
        
    if len(provisional_points) > 0:
        points[player_tag] = sum(provisional_points)/len(provisional_points)
    else:
        points[player_tag] = 0
            





def seed():
    

    #A dictionary, will contain each player
    #With a calculated value depending on its placings
    

    filename = ent_fileName.get()

    logs.wl(f"Filename: {filename}")

    with open(filename, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        logs.wl("File opened succesfully! \n")
        for row in reader:
        
            #Get the tag (The id doesn't work right now)
            #And the placings as a List of dictionaries
            tag = (row['Short GamerTag'],)
            logs.wl("-----------------------------------------------------------")
            logs.wl(f"Player: {tag[0]}")
            c.execute('SELECT placings FROM players WHERE tag=?',tag)
            placings = c.fetchone()
            if c.fetchone() is not None:
                logs.wl("More than one player found! \n Asking for ID")
                fails.append(tag[0])
                continue
                
            #ID is unused for now
            #c.execute('SELECT player_id FROM players WHERE tag=?',tag) #Optimizar
            #id = c.fetchone()

            #Error with the player, not found
            if type(placings) is not tuple:
                print(tag[0])
                print("Player not found!")
                logs.wl(tag[0])
                logs.wl("Player not found! \n Setting seed random")
                #We set it's value as 0
                points[tag[0]]=0
                continue
            
            get_points(placings,tag[0])
    
        for player_tag in fails:
            id = (tkinter.simpledialog.askstring(title="Seeder by @NoMeHeVistoFE Alpha1.1",prompt=f"Insert the id of the player {player_tag}"),)
            print(id)
            logs.wl("-----------------------------------------------------------")
            logs.wl(f"Player: {player_tag}")
            c.execute('SELECT placings FROM players WHERE player_id=?',id)
            placings = c.fetchone()
            if placings is None:
                logs.wl('Incorrect ID!\nSetting random seed')
                points[player_tag] = 0
                continue
            get_points(placings,player_tag)
            
        #Short dictionary
        values = dict(sorted(points.items(), key=lambda item: item[1], reverse=True))
        print(values)
        logs.wl("Seeding:")
        logs.wl(f"{str(values)}")
        tx_seed.config(state='normal')
        tx_seed.insert(0.0,f"{str(values)}")
        tx_seed.config(state='disabled')

        logs.close()
        f = open('log.txt','r')
        tx_log.config(state='normal')
        tx_log.insert(0.0,f.read())
        tx_log.config(state='disabled')

 #Button handler

def handle_click_start_seed(event):
    seed()
btn_seed.bind("<Button-1>",handle_click_start_seed)


root.resizable(False,False)
root.mainloop()

    
        
        


