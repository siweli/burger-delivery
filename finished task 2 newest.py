# IMPORTS
import tkinter as tk
from tkinter import *
from tkinter import font as tkfont
from turtle import *
from random import *
import math
from datetime import timedelta
from time import sleep
import csv
import string


# custom hash function
def chash(x):
    bit = 6
    salt = "P3PP£RP1G"
    x += salt
    y = ""
    for i in x:
        y+=str(ord(i))
    x = y.zfill(bit * math.ceil(len(y) / bit))

    h = 0
    for i in [x[i:i+bit] for i in range(0, len(x), bit)]:
        h = ((h + int(i)) % 10**bit - 1)
    return h

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
        self.screen = TurtleScreen(self.canvas)
        self.screen.bgcolor("#cdf0ff")
        self.canvas.pack(side="left")
        self.canvas.bind('<Button-1>',self.create_home)
        
    # ninja turtles (because i am using the turtle library)
        # introducing 'leonardo' the turtle (for web graph writing)
        self.leo = RawTurtle(self.screen)
        self.leo.speed(speed=0)
        self.leo.color("#000")
        self.leo.ht()
        # introducing 'donatello' the turtle (for address writing)
        self.don = RawTurtle(self.screen)
        self.don.speed(speed=0)
        self.don.color("#f00")
        self.don.ht()
        # introducing 'raphael' the turtle (for A* driver writing)
        self.rap = RawTurtle(self.screen)
        self.rap.speed(speed=0)
        self.rap.color("#9453e6")
        self.rap.ht()
        # introducing 'michaelangelo' the turtle (for dijkstra driver writing)
        self.mic = RawTurtle(self.screen)
        self.mic.speed(speed=0)
        self.mic.color("#c47c2c")
        self.mic.ht()
    # this can be reduced into a for loop but cannot be bothered

        # variables
        self.address = False
        self.driver_loc = False
        self.restaurant = False
        self.icons = {}
        self.basket = basket
        self.tracker = [0]

        # frame
        self.ui_frame = Frame(self)
        self.ui_frame.pack(anchor="n")
        
        # start
        self.start()

    def create_ui(self):
        # create a driver
        driver_label = tk.Label(self.ui_frame, text="Find a driver").pack()
        driver_add = Button(self.ui_frame, width="8", text="submit", command= lambda: self.create_driver(self.rap)).pack()

        # user order
        order_label = Label(self.ui_frame, text="Your order:").pack()
        for i in self.basket:
            l = Label(self.ui_frame, text=i).pack()
        self.time_label = Label(self.ui_frame, text="")
        self.time_label.pack()

        self.time_label = Label(self.ui_frame, text="")
        self.time_label.pack()

        # button to reset canvas
        reset = Button(self.ui_frame, text="RESET", command=self.start).pack(padx=10, pady=10, anchor="s", side="right")

    def delete_ui(self):
        for widget in self.ui_frame.winfo_children():
            widget.destroy()

    # create the border within the canvas
    def create_border(self):
        self.leo.dot(1, "#000")
        self.leo.up()
        self.leo.fillcolor("#1a1a1a")
        self.leo.width(4)
        self.leo.begin_fill()
        for corner in [(-405,405),(405,405),(405,-405),(-405,-405),(-405,405)]:
            self.leo.setpos(corner)
            self.leo.down()
        self.leo.end_fill()

    # creates randomly placed nodes in the canvas
    def create_nodes(self):
        self.nodes = {}
        index = 0
        self.leo.color("#999")
        for y in range(-350, 400, 100):
            for x in range(-350, 400, 100):
                doit = choices([True,False], weights=[15,1],k=1)[0]
                if doit:
                    self.leo.up()
                    self.leo.setpos(x, y)
                    self.nodes[index] = self.leo.pos()
                    self.leo.down()
                    try:
                        self.leo.dot(15)
                    except tk.TclError:
                        exit()
                    # for testing purposes
                    #self.leo.write(str(index)+" ", font=("Courier", 17, "bold"), align="right")
                    #self.leo.write(self.leo.pos(), font=("Courier", 7, "bold"), align="left")
                    self.leo.up()
                    index += 1

    # find the nodes surrounding a position
    def surrounding_nodes(self, pos):
        nodes = self.nodes.copy()
        close = []
        exclude = [pos]
        for i in range(4):
            p = self.closest_node(pos, exclude)
            if p[0] != pos[0] and p[1] != pos[1]:
                pass # do nothing because p is diagonal from pos
            elif p[0] == pos[0] or p[1] == pos[1]:
                if (p[0] > pos[0]+100) or (p[0] < pos[0]-100):
                    pass # do nothing because p is too far in x from pos
                elif (p[1] > pos[1]+100) or (p[1] < pos[1]-100):
                    pass # do nothing because p is too far in y from pos
                else:
                    close.append(p)
            exclude.append(p)
        return close

    # create the lines and the relations
    def create_lines(self):
        self.relations = {}
        for i in self.nodes.items():
            surround_i = self.surrounding_nodes(i[1])
            try:
                self.relations[i[0]] = choices(surround_i, [1]*len(surround_i), k=randint(2,3))
            except IndexError:
                self.start()
        self.fix_duplicates()

        merge = {i : [] for i in range(len(self.nodes))}
        self.leo.width(15)
        for i in self.relations.items():
            for j in i[1]:
                self.leo.up()
                try:
                    self.leo.dot(1) # check if canvas still exists for error handling upon premature closure
                except tk.TclError:
                    exit()
                self.leo.setpos(self.nodes[i[0]])
                merge[list(self.nodes.keys())[list(self.nodes.values()).index(j)]].append(self.nodes[i[0]])
                self.leo.down()
                self.leo.setpos(j)
        for i in self.relations.items():
            self.relations[i[0]] = self.relations[i[0]] + merge[i[0]]
        self.fix_duplicates()

    # fixes the relations dict for duplicates
    def fix_duplicates(self):
        for i in self.relations.items():
            temp = i[1]
            temp = list(dict.fromkeys(temp))
            self.relations[i[0]] = temp

    # find closest node to a position
    def closest_node(self, pos, exclude):
        list_nodes = []
        for i in self.nodes.items():
            list_nodes.append(i[1])
        for i in exclude:
            list_nodes.remove(i)
        distance_metric = lambda x: (x[0] - pos[0])**2 + (x[1] - pos[1])**2
        node = min(list_nodes, key=distance_metric)
        return node

    # create user home address
    def create_home(self, event):
        # get rid of everything except the web
        self.don.clear()
        self.rap.clear()
        self.mic.clear()
        # find closest node to cursor
        xy = (event.x - 500, -event.y + 425)
        pos = self.closest_node(xy, [])
        self.don.up()
        self.don.setpos(pos)
        self.don.write(" ⌂", font=("Courier", 20, "bold"), align="left")
        self.don.dot(12)
        self.address = list(self.nodes.keys())[list(self.nodes.values()).index(self.don.pos())]

    # create driver at random point
    def create_driver(self, turt):
        self.screen.tracer(1)
        if self.address == False:
            pass
        else:
            self.delete_ui()
            self.rap.up()
            self.rap.clear()
            self.mic.up()
            self.mic.clear()

            # create driver excluding home address
            nodes = list(self.nodes.copy())
            nodes.remove(self.address)
            self.rap.setpos(self.nodes[choice(nodes)])
            self.driver_loc = list(self.nodes.keys())[list(self.nodes.values()).index(self.rap.pos())]
            self.rap.write(" 웃", font=("Courier", 17, "bold"), align="left")
            self.rap.dot(12)

            # create restaurant excluding home address and driver location
            nodes.remove(self.driver_loc)
            self.mic.setpos(self.nodes[choice(nodes)])
            self.restaurant = list(self.nodes.keys())[list(self.nodes.values()).index(self.mic.pos())]
            self.mic.write(" 🍔", font=("Courier", 18, "bold"), align="left")
            self.mic.dot(12)

            # execute A* algorithm on restaurant and then home
            self.rap.width(7)
            dist = self.aStar(self.rap, self.driver_loc, self.restaurant)
            #self.rap.color("#ffa500")
            self.mic.width(4)
            dist2 = self.aStar(self.mic, self.restaurant, self.address)
            print("total distance:",dist+dist2)
            self.create_ui()
            self.tracker[0] += 1
            self.timer(dist)
            
    # A* algorithm
    def aStar(self, turt, start, end):
        def pythagoras(pos1,pos2):
            c = (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2
            return math.sqrt(c)
        visited = []
        current = [start].copy()[0]
        dist = 0
        print(start,"-->",end)
        while current != end:
            closest = 9999
            visited.append(self.nodes[current])
            pos = self.nodes[current]
            leng = len(self.relations[current])
            invalid = 0
            for count, i in enumerate(self.relations[current]):
                if i in visited:
                    #print("already been to",list(self.nodes.keys())[list(self.nodes.values()).index(i)])
                    invalid+=1
                    pass
                else:
                    h = pythagoras(i, self.nodes[end])
                    g = dist + 100
                    f = g + h
                    if f < closest:
                        closest = f
                        pos = self.relations[current][count]
            # end for
            turt.down()
            prev = current
            try:
                turt.setpos(pos)
            except tk.TclError:
                exit()
            turt.dot(3)
            current = list(self.nodes.keys())[list(self.nodes.values()).index(turt.pos())]
            dist += 100
            if current == end:
                break
            elif leng == invalid:
                print("stuck at", current)
                # save colour and width
                turt_color = turt.pencolor()
                turt_width = turt.width()
                # set colour to road colour then go back on self
                turt.color("#999")
                turt.width(8)
                turt.setpos(visited[visited.index(self.nodes[current])-1])
                current = list(self.nodes.keys())[list(self.nodes.values()).index(turt.pos())]
                # revert to original
                turt.color(turt_color)
                turt.width(turt_width)
                # adjust dist for backtracking
                dist -= 200
        # end while
        print("done")
        return dist

    # timer for delivery time
    def timer(self,dist):
        current = self.tracker.copy()
        while dist != 0:
            if current[0] != self.tracker[0]:
                break
            else:
                for i in range(100):
                    if i == 0:
                        t = str(timedelta(seconds=dist)).split(":")[1:]
                        dist-=1
                        try:
                            self.time_label.config(text="Arrives in: {}m {}s".format(int(t[0]),t[1]))
                        except tk.TclError:
                            exit()
                        self.ui_frame.update()
                    sleep(0.001)
        if dist == 0:
            self.time_label.config(text="Your order is here")
            
    # creates the graph
    def start(self):
        self.canvas.delete("all")
        self.delete_ui()
        self.tracker[0] += 1
        self.address = False
        self.screen.tracer(0)
        self.create_border()
        self.create_nodes()
        self.create_lines()
        self.screen.update()
        self.create_ui()



# order menu
class FoodOrder(tkn):
    def __init__(self):
        tkn.__init__(self)
        self.geometry('300x200+0+50')

        # label for order menu
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

    # submit button for food order
    def submit(self):
        basket = []
        for i in self.listbox.curselection():
            if self.listbox.get(i) != "-":
                basket.append(self.listbox.get(i))
        self.destroy()
        app = App(basket)
        app.mainloop()



# log in to account page
class Login:
    def __init__(self, root=None):
        self.root = root
        root.geometry('300x200+0+50')
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        
        Label(self.frame, text="LOGIN", font=self.title_font).pack()

        self.user, self.pw = StringVar(), StringVar()
        self.usr_entry = Entry(self.frame, textvariable=self.user)
        self.usr_entry.pack()

        self.pw_entry = Entry(self.frame, textvariable=self.pw, show="*")
        self.pw_entry.pack()

        Button(self.frame, text="submit", command=self.get_entries).pack()
        
        Button(self.frame, text='Create an account', command=self.make_create_page).pack()
        self.Create = Create(master=self.root, app=self)

        # empty label for error
        self.error = Label(self.frame, text="")
        self.error.pack(pady=10)

    def get_entries(self):
        user, pw = self.user.get(), self.pw.get()
        with open("accounts.csv","r") as f:
            csvread = csv.reader(f)
            for i in csvread:
                if i[0] == user and i[1] == str(chash(pw)):
                    self.frame.pack_forget()
                    app = FoodOrder()
                    app.mainloop()
        self.error.config(text="ERROR: incorrect login details", bg="#eb7878")
        self.usr_entry.delete(0, END)
        self.pw_entry.delete(0, END)
                    


    def go(self):
        self.frame.pack()

    def make_create_page(self):
        self.frame.pack_forget()
        self.error.config(text="", bg="#f0f0f0")
        self.Create.go()



# create an account page
class Create:
    def __init__(self, master=None, app=None):
        self.master = master
        self.app = app
        self.frame = tk.Frame(self.master)
        
        Label(self.frame, text="CREATE ACCOUNT", font=app.title_font).pack()

        self.user, self.pw = StringVar(), StringVar()
        self.usr_entry = Entry(self.frame, textvariable=self.user)
        self.usr_entry.pack()

        self.pw_entry = Entry(self.frame, textvariable=self.pw, show="*")
        self.pw_entry.pack()

        Button(self.frame, text="create", command=self.get_entries).pack()
        
        Button(self.frame, text='Go back to login', command=self.go_back).pack()

        # empty label for error
        self.error = Label(self.frame, text="")
        self.error.pack(pady=10)

    def get_entries(self):
        user, pw = self.user.get(), self.pw.get()
        if user == "" or pw == "":
            user = "@"
        for i in user:
            if i not in string.ascii_letters+string.digits+"_.":
                user = "@"
        if user != "@":
            with open("accounts.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([user, chash(pw)])
            self.frame.pack_forget()
            app = FoodOrder()
            app.mainloop()
        else:
            self.error.config(text="ERROR: invalid entry", bg="#eb7878")
            self.usr_entry.delete(0, END)
            self.pw_entry.delete(0, END)

    def go(self):
        self.frame.pack()

    def go_back(self):
        self.frame.pack_forget()
        self.error.config(text="", bg="#f0f0f0")
        self.app.go()

   

# START
if __name__ == "__main__":
    root = tk.Tk()
    app = Login(root)
    root.mainloop()
