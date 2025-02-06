# IMPORTS
import tkinter as tk
from tkinter import *
from tkinter import font as tkfont
from turtle import *
from random import *
from math import sqrt
from datetime import timedelta
from time import sleep
import string

# tkinter init
class tkn(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Deliverez")

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
    
# MAIN PROGRAM
class App(tkn):
    def __init__(self, basket):
        tkn.__init__(self)

        self.geometry('1200x850+0+50')

        # set up canvas for turtle
        self.canvas = Canvas(self, width=1000, height=850)
        screen = TurtleScreen(self.canvas)
        screen.bgcolor("#cdf0ff")
        self.canvas.pack(side="left")

    # ninja turtles (because i am using the turtle library)
        # introducing 'leonardo' the turtle (for web graph writing)
        self.leo = RawTurtle(screen)
        self.leo.speed(speed=0)
        self.leo.color("#000")
        self.leo.ht()
        # introducing 'donatello' the turtle (for address writing)
        self.don = RawTurtle(screen)
        self.don.speed(speed=0)
        self.don.color("#f00")
        self.don.ht()
        # introducing 'raphael' the turtle (for A* driver writing)
        self.rap = RawTurtle(screen)
        self.rap.speed(speed=0)
        self.rap.color("#0f0")
        self.rap.ht()
        # introducing 'michaelangelo' the turtle (for dijkstra driver writing)
        self.mic = RawTurtle(screen)
        self.mic.speed(speed=0)
        self.mic.color("#ff0")
        self.mic.ht()
    # this can be reduced into a for loop but cannot be bothered

        # variables
        self.address = False
        self.driver_loc = False
        self.letters = list(string.ascii_uppercase)[:6]
        self.basket = basket
        self.tracker = [0]

        # button to reset canvas
        reset = Button(self, text="RESET", command=self.start).pack(padx=10, pady=10, anchor="s", side="right")

        # start
        self.user_input()
        self.start()

    def user_input(self):
        # address buttons
        self.gui_frame = Frame(self)
        self.gui_frame.pack(side="right", anchor="n")
        self.address_label = tk.Label(self.gui_frame, text="What is your address?").pack()
        self.var = tk.IntVar()
        for value, letter in enumerate(self.letters):
            self.r = Radiobutton(self.gui_frame, text=letter, variable=self.var, value=value)
            self.r.pack()
        address_add = Button(self.gui_frame, width="8", text="submit", command=self.create_home).pack()

        # create a driver
        driver_label = tk.Label(self.gui_frame, text="Find a driver").pack()
        driver_add = Button(self.gui_frame, width="8", text="submit", command= lambda: self.create_driver(self.rap)).pack()

        # change number of nodes scale
        n_nodes_label = tk.Label(self.gui_frame, text="Number of addresses").pack()
        self.var2 = tk.StringVar()
        self.n_nodes_scale = Scale(self.gui_frame, variable=self.var2, from_=3, to=26, width=25, sliderlength=10,  orient=HORIZONTAL).pack()
        n_nodes_submit = Button(self.gui_frame, width="8", text="submit", command=self.n_nodes_get).pack()

        # user order
        order_label = Label(self.gui_frame, text="Your order:").pack()
        for i in self.basket:
            l = Label(self.gui_frame, text=i).pack()
        self.time_label = Label(self.gui_frame, text="")
        self.time_label.pack()

    def test(self):
        for widget in self.gui_frame.winfo_children():
            widget.destroy()
        self.gui_frame.destroy()

    # create the border within the canvas
    def create_border(self):
        self.leo.dot(1, "#000")
        self.leo.up()
        self.leo.fillcolor("#fff")
        self.leo.width(4)
        self.leo.begin_fill()
        for corner in [(-405,405),(405,405),(405,-405),(-405,-405),(-405,405)]:
            self.leo.setpos(corner)
            self.leo.down()
        self.leo.end_fill()

    # creates randomly placed nodes in the canvas
    def create_nodes(self):
        self.nodes = {}
        for i in range(len(self.letters)):
            self.leo.up()
            self.leo.setpos(randrange(-390, 390, 10), randrange(-390, 390, 10))
            self.nodes[self.letters[i]] = self.leo.pos()
            self.leo.down()
            self.leo.dot(10, "#000")
            self.leo.write(self.letters[i], font=("Courier", 15, "bold"), align="right")
            #self.leo.write(self.leo.pos(), font=("Courier", 12, "bold"), align="left")
            self.leo.up()

    # create the lines and the relations
    def create_lines(self):
        temp = {}
        for i in self.letters:
            close = self.relation_nodes(self.nodes[i], False)
            far = self.relation_nodes(self.nodes[i], True)
            temp[i] = close+far
        self.relations = {}
        for i in temp.items():
            self.relations[i[0]] = choices(i[1], weights = [3,1,1,1], k=2)
        self.fix_duplicates()

        merge = {i : [] for i in self.letters}
        self.leo.width(2)
        for i in self.relations.items():
            for j in i[1]:
                self.leo.up()
                self.leo.setpos(self.nodes[i[0]])
                merge[list(self.nodes.keys())[list(self.nodes.values()).index(j)]].append(self.nodes[i[0]])
                self.leo.down()
                self.leo.setpos(j)
                distance = self.leo.distance(self.nodes[i[0]], j)
                self.leo.setpos(((self.nodes[i[0]][0]+j[0])/2, (self.nodes[i[0]][1]+j[1])/2))
                self.leo.write(round(distance), font=("Courier", 11, "bold"), align="left")
        for i in self.relations.items():
            self.relations[i[0]] = self.relations[i[0]] + merge[i[0]]
        self.fix_duplicates()
        self.fix_relations()

    # get the farthest or closest nodes to a position
    def relation_nodes(self,pos,dist):
        list_nodes = []
        for i in self.nodes.items():
            list_nodes.append(i[1])
        list_nodes.remove(pos)
            
        distance_metric = lambda x: (x[0] - pos[0])**2 + (x[1] - pos[1])**2
        nodes = []
        for i in range(2):
            if dist == True:
                node = max(list_nodes, key=distance_metric) # farthest
            else:
                node = min(list_nodes, key=distance_metric) # closest
            nodes.append(node)
            list_nodes.remove(node)
        return nodes

    # fixes the relations dict for duplicates
    def fix_duplicates(self):
        for i in self.relations.items():
            temp = i[1]
            temp = list(dict.fromkeys(temp))
            self.relations[i[0]] = temp

    # checks if any node only has 1 connection, if so then reset
    def fix_relations(self):
        for i in self.relations.items():
            if len(i[1]) == 1:
                self.start()

    # create user home address
    def create_home(self):
        # get rid of everything except the web
        self.don.clear()
        self.rap.clear()
        self.mic.clear()
        # get new address
        self.address = self.nodes[self.letters[self.var.get()]]
        self.don.up()
        self.don.setpos(self.address)
        self.don.write("⌂", font=("Courier", 15, "bold"), align="left")
        self.don.write(self.letters[self.var.get()], font=("Courier", 15, "bold"), align="right")
        self.don.dot(10)

    # create driver at random point
    def create_driver(self, turt):
        exclude = self.letters[self.var.get()]
        # get rid of old driver
        turt.clear()
        # go to random node and create driver, excluding the home address
        turt.up()
        letters = self.letters.copy()
        letters.remove(exclude)
        turt.setpos(self.nodes[choice(letters)])
        self.driver_loc = list(self.nodes.keys())[list(self.nodes.values()).index(turt.pos())]
        turt.write("웃", font=("Courier", 15, "bold"), align="left")
        turt.write(self.driver_loc, font=("Courier", 15, "bold"), align="right")
        turt.dot(10)
        self.aStar()
        #self.dijkstra()

    # get value from nodes scale
    def n_nodes_get(self):
        self.letters = list(string.ascii_uppercase)[:int(self.var2.get())]
        self.start()

    # A* algorithm
    def aStar(self):
        def pythagoras(pos1,pos2):
            c = (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2
            return sqrt(c)
        if self.address == False:
            pass
        else:
            visited = []
            self.rap.width(2)
            #self.rap.speed(speed=1)
            dist = 0
            while self.rap.pos() != self.address:
                closest = 9999
                for count,i in enumerate(self.relations[self.driver_loc]):
                    visited.append(self.nodes[self.driver_loc])
                    if i == self.address:
                        pos = i
                        break
                    elif i in visited:
                        pass
                    else:
                        h = pythagoras(i, self.address)
                        g = dist + pythagoras(self.nodes[self.driver_loc], i)
                        f = g + h
                        if f<= closest:
                            closest = f
                            pos = self.relations[self.driver_loc][count]
                
                self.rap.down()
                a = self.rap.pos()
                self.rap.setpos(pos)
                self.rap.dot(10)
                self.driver_loc = list(self.nodes.keys())[list(self.nodes.values()).index(self.rap.pos())]
                dist += round(self.rap.distance(a, self.nodes[self.driver_loc]))
            self.tracker[0] += 1
            self.timer(dist)

    def timer(self,dist):
        current = self.tracker.copy()
        while dist != 0:
            if current[0] != self.tracker[0]:
                break
            else:
                t = str(timedelta(seconds=dist)).split(":")[1:]
                dist-=1
                self.time_label.config(text="Arrives in: {}m {}s".format(int(t[0]),t[1]))
                self.gui_frame.update()
                sleep(1)
        self.time_label.config(text="Your order is here")
            

    # dijkstra algorithm
    def dijkstra(self):
        if self.address == False:
            pass
        else:
            unvisited_nodes = self.nodes.copy()
            #while unvisited_nodes:
            
    # creates the graph
    def start(self):
        self.canvas.delete("all")
        self.test()
        self.address = False
        self.user_input()
        self.create_border()
        self.create_nodes()
        self.create_lines()

# order menu
class FoodOrder(tkn):
    def __init__(self):
        tkn.__init__(self)

        self.geometry('300x200+0+50')

        lab = Label(self, text="ORDER NOW", font=self.title_font).pack()

        # menu stuff
        menu_options = ["burger","wrap","pizza","-","coke","water","fanta"]
        menu = Frame(self)
        menu.pack(side=LEFT, padx=30)
        lab = Label(menu, text="menu").pack()
        self.listbox = Listbox(menu, yscrollcommand=True, selectmode="multiple", bg="#f0f0f0", relief=RIDGE, height=len(menu_options), selectbackground="#c5c5c5")
        self.listbox.pack(expand = YES)
        for i in range(len(menu_options)):
            self.listbox.insert(END, menu_options[i])

        but = Button(self, text="ORDER",command=self.submit)
        but.pack(side=RIGHT, padx=30)

            
    def submit(self):
        basket = []
        for i in self.listbox.curselection():
            if self.listbox.get(i) != "-":
                basket.append(self.listbox.get(i))
        self.destroy()
        app = App(basket)
        app.mainloop()


# login window
class Login(tkn):
    def __init__(self):
        tkn.__init__(self)
        
        self.geometry('300x200+0+50')

        lab = Label(self, text="LOGIN", font=self.title_font)
        lab.pack()

        but = Button(self, text="submit",command=self.loggin)
        but.pack()

    def loggin(self):
        self.destroy()
        app = FoodOrder()
        app.mainloop()

# START
if __name__ == "__main__":
    app = Login()
    app.mainloop()
