#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')

import sys
import numpy as np
import numpy.polynomial.polynomial as poly
import os
import math
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from obspy.core import Trace, Stream, UTCDateTime
from tkinter import *
from matplotlib import pyplot as plt

global pick_mode
global line_mode
global pick_1
global pick_2
pick_mode = None
line_mode = None
pick_1 = None
pick_2 = None
global user_lines
user_lines = []

fig=plt.figure(figsize=(7,5))
ax=plt.subplot(111)

def open_picks():

    input_path =  sorted(filedialog.askopenfilenames(title='Open',
                                                           filetypes=[('Text','*.txt')]))
    if not input_path:
        print('No file found')
    else:
        global site_name
        print('Opening file ', input_path)

        f = open(input_path[0],'r')                      # Open and Parse file
        for line in f:
            file_contents = f.read()
        line_data = file_contents.split("\n")
        header = line_data[0]
        td_time = []
        td_distance = [] 
        for i in range(1,len(line_data)-1):
            td_data = line_data[i].split()
            td_time.append(float(td_data[1]))
            td_distance.append(float(td_data[0]))
        f.close()

        temp_label = input_path[0].split("/")
        site_name=temp_label[-2]
        ax.set_title(site_name)
        ax.grid(color=(0.8, 0.8, 0.8), linestyle='--', linewidth=1)
        
        
        temp_line_id = 'picks' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('picks')))
        print(temp_line_id)

        line = plt.plot(td_distance,td_time,'o',markersize=5, label=temp_label[-1], gid = temp_line_id)
        print(ax.lines[0].get_xdata())

        plt.xlabel('Distance (m)')
        plt.ylabel('Time (ms)')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)

        fig.canvas.draw()

def clear_picks(): 
    if not ax.lines:
        print('nothing to clear')
    else:
        print('ax.lines before = ', ax.lines)

        for i in reversed(ax.lines):
            if 'picks' in i.get_gid():
                print('picks in', i.get_gid())
                i.remove()

        print('ax.lines after= ', ax.lines)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        fig.canvas.draw()

class LineDrawer(object): # Defines line object type and drawing function
    def draw_line(self):
        global final_picks
        xy = final_picks
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        vel = 1000./abs((y[1]-y[0])/(x[1]-x[0]))


        mid_x = x[0]+(x[1]-x[0])/2
        mid_y = y[0]+(y[1]-y[0])/2
        temp_line_id = 'line_manual_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('line')))
        print('id will be', temp_line_id)
        temp_text_id = 'text_manual_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('text')))
        print('id will be', temp_line_id)
        label = ax.text(mid_x, mid_y, str("%.0f" % vel) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_text_id)
        line = ax.plot(x,y,'-k', gid = temp_line_id)             # Plots user's line
        fig.canvas.draw()


def destroy():
    sys.exit()
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sys.exit()
def save_fig():
    
    fig_path=('/Users/freddiejackson/Documents/EasternCanadaFieldWork2017/GeodeDB/' + site_name + '.png')
    fig.savefig(fig_path)
    print('Figure saved as ' + fig_path)

def set_axis():
    def update_axis():
        ax.set_xlim(float(e1.get()), float(e2.get()))
        ax.set_ylim(float(e3.get()), float(e4.get()))
        root3.destroy()
        ax.figure.canvas.draw()
        print('Axis Updated')
    
    root3 = Toplevel()                                 # Creates a second window. Because we can't have multiple TKs, we create a Toplevel
    root3.wm_title("Set Axes") 
    Label(root3, text="X Min").grid(row=0)       # Positions labels
    Label(root3, text="X Max").grid(row=1)
    Label(root3, text="Y Min").grid(row=2)
    Label(root3, text="Y Max").grid(row=3)
    current_xlim=ax.get_xlim()
    current_ylim=ax.get_ylim()

    e1 = Entry(root3)                            # TK entry function
    e1.insert(0, current_xlim[0])                   # Enters current axis limits
    e2 = Entry(root3)
    e2.insert(0, current_xlim[1])

    e3 = Entry(root3)
    e3.insert(0, current_ylim[0])
    e4 = Entry(root3)
    e4.insert(0, current_ylim[1])

    e1.grid(row=0, column=1)                        # Positions entry functions
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    e4.grid(row=3, column=1)

    Button(root3, text='Update Axis', command=update_axis).grid(row=5, column=1, sticky=W, pady=4)

def pick_point():
    global pick_mode
    if pick_mode is None:
        pick_mode = True
    elif pick_mode is False:
        pick_mode = True

    def on_click(event):
        global pick_mode
        if event.inaxes is not None:
            if pick_mode is True:
                print(event.xdata, event.ydata)
                pick_mode = False
                fig.canvas.mpl_disconnect(cid)
        else:
            print('Clicked ouside axes bounds but inside plot window')
    cid = fig.canvas.mpl_connect('button_press_event', on_click)

    try:
        fig.canvas.mpl_disconnect(cid2)
    except:
        None

def pick_line():   #Defines what the TK button does
    global picks
    global line_mode
    picks = None
    global user_lines
    

    if line_mode is None:
        line_mode = True
    elif line_mode is False:
        line_mode = True

    def on_click2(event):
        global line_mode
        global pick_mode
        global final_picks
        global pick_1
        global pick_2

        if event.inaxes is not None:
            if line_mode is True:
                if pick_mode is not True:
                    if pick_1 == None:
                        pick_1 = event.xdata, event.ydata
                        print('pick 1 saved as ', pick_1) 
                    else:
                        pick_2 = event.xdata, event.ydata
                        print('pick 2 saved as ', pick_2)
                        final_picks = pick_1, pick_2
                        print('final picks = ', final_picks)
                        print('line picking complete')
                        pick_1 = None
                        pick_2 = None
                        line_mode = False
                        fig.canvas.mpl_disconnect(cid2)

                        ld = LineDrawer()
                        ld.draw_line()
                        user_lines.append(ld)

        else:
            print('Clicked ouside axes bounds but inside plot window')
    cid2 = fig.canvas.mpl_connect('button_press_event', on_click2)
    try:
        fig.canvas.mpl_disconnect(cid)
    except:
        None

def remove_line():   #Defines what the TK button does
    #if len(user_lines) > 0:
    #    user_lines.pop(-1)
    #    ax.lines.pop(-1)
    #    ax.figure.canvas.draw()
    #    print('Line cleared')

    for j in reversed(ax.lines):
        print(j.get_gid())
        if 'line_manual' in j.get_gid():
            print(j.get_gid(), ' is getting removed')
            j.remove()
    for j in reversed(ax.texts):
        if ('text' in j.get_gid() and 'row' not in j.get_gid()):
            print(j.get_gid(), ' is getting removed')
            j.remove()
    fig.canvas.draw()

def auto_line():   #Defines what the TK button does
    nlayer_entries = []
    xhinge1_entries = []
    xhinge2_entries = []

    def plot_autoline(data_i, temp_nlayers, temp_xhinge1, temp_xhinge2):
        clear_autoline(data_i)
        print('i = ', data_i)
        x_temp = ax.lines[data_i].get_xdata()
        y_temp = ax.lines[data_i].get_ydata()
        min_x = min(x_temp[0], x_temp[-1])
        max_x = max(x_temp[0], x_temp[-1])

        temp_line_id = 'line_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('line')))
        print('id will be', temp_line_id)
        temp_label_id = 'text_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('text')))
        print('id will be', temp_label_id)

        if temp_nlayers == 1:
            mid_x = min_x+(max_x-min_x)/2
            x_new = np.linspace(min_x, max_x, 100)
            coefs = poly.polyfit(x_temp, y_temp, 1)
            vel = 1000./abs(coefs[1])
            ffit = poly.polyval(x_new, coefs)
            poly_line = ax.plot(x_new, ffit, '-k', gid = temp_line_id)
            vel_label = ax.text(mid_x, poly.polyval(mid_x, coefs), str("%.0f" % vel) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id)
       
        elif temp_nlayers == 2:
            mid_x1 = min_x+(temp_xhinge1-min_x)/2
            mid_x2 = temp_xhinge1+(max_x-temp_xhinge1)/2
            x1_new = np.linspace(min_x, temp_xhinge1, 100)
            x2_new = np.linspace(temp_xhinge1, max_x, 100)

            temp_line_id2 = 'line_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('line'))+1)
            print('id2 will be', temp_line_id)
            temp_label_id2 = 'text_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('text'))+1)
            print('id2 will be', temp_label_id)

            #Split data by hinge
            line1_x, line1_y, line2_x, line2_y = [], [], [], []
            for l in range(len(x_temp)):
                print('if ', x_temp[l], ' is smaller than ', temp_xhinge1)
                if x_temp[l] < temp_xhinge1:
                    line1_x.append(x_temp[l])
                    line1_y.append(y_temp[l])
                else:
                    line2_x.append(x_temp[l])
                    line2_y.append(y_temp[l])

            print(line1_x)

            coefs1 = poly.polyfit(line1_x, line1_y, 1)
            coefs2 = poly.polyfit(line2_x, line2_y, 1)
            vel1 = 1000./abs(coefs1[1])
            vel2 = 1000./abs(coefs2[1])
            ffit1 = poly.polyval(x1_new, coefs1)
            ffit2 = poly.polyval(x2_new, coefs2)
            poly_line1 = ax.plot(x1_new, ffit1, '-k', gid = temp_line_id)
            poly_line2 = ax.plot(x2_new, ffit2, '-k', gid = temp_line_id2)
            vel_label1 = ax.text(mid_x1, poly.polyval(mid_x1, coefs1), str("%.0f" % vel1) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id)
            vel_label2 = ax.text(mid_x2, poly.polyval(mid_x2, coefs2), str("%.0f" % vel2) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id2)

        elif temp_nlayers == 3:
            temp_line_id2 = 'line_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('line'))+1)
            temp_label_id2 = 'text_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('text'))+1)
            temp_line_id3 = 'line_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('line'))+2)
            temp_label_id3 = 'text_row' + str(data_i) + '_' + str(sum(1 for i in ax.lines if i.get_gid().__contains__('text'))+2)

            temp_temp_xhinge1 = temp_xhinge1
            temp_temp_xhinge2 = temp_xhinge2

            temp_xhinge1 = min(temp_temp_xhinge1, temp_temp_xhinge2)
            temp_xhinge2 = max(temp_temp_xhinge1, temp_temp_xhinge2)

            mid_x1 = min_x+(temp_xhinge1-min_x)/2
            mid_x2 = temp_xhinge1+(temp_xhinge2-temp_xhinge1)/2
            mid_x3 = temp_xhinge2+(max_x-temp_xhinge2)/2

            x1_new = np.linspace(min_x, temp_xhinge1, 100)
            x2_new = np.linspace(temp_xhinge1, temp_xhinge2, 100)
            x3_new = np.linspace(temp_xhinge2, max_x, 100)


            #Split data by hinge
            line1_x, line1_y, line2_x, line2_y, line3_x, line3_y = [], [], [], [], [], []
            for l in range(len(x_temp)):                                         #Groups data by the hinges
                
                if x_temp[l] < temp_xhinge1:
                    line1_x.append(x_temp[l])
                    line1_y.append(y_temp[l])
                    print(x_temp[l], 'is smaller than', temp_xhinge1)
                elif (x_temp[l] > temp_xhinge1 and x_temp[l] < temp_xhinge2):
                    line2_x.append(x_temp[l])
                    line2_y.append(y_temp[l])
                    print(x_temp[l], 'is smaller than', temp_xhinge2)
                elif x_temp[l] > temp_xhinge2:
                    line3_x.append(x_temp[l])
                    line3_y.append(y_temp[l])
                    print(x_temp[l], 'is larger than', temp_xhinge2)

            coefs1 = poly.polyfit(line1_x, line1_y, 1) #Determines polynomial coefficients for each line
            coefs2 = poly.polyfit(line2_x, line2_y, 1)
            coefs3 = poly.polyfit(line3_x, line3_y, 1)
            vel1 = 1000./abs(coefs1[1])
            vel2 = 1000./abs(coefs2[1])
            vel3 = 1000./abs(coefs3[1])
            ffit1 = poly.polyval(x1_new, coefs1)
            ffit2 = poly.polyval(x2_new, coefs2)
            ffit3 = poly.polyval(x3_new, coefs3)
            poly_line1 = ax.plot(x1_new, ffit1, '-k', gid = temp_line_id)
            poly_line2 = ax.plot(x2_new, ffit2, '-k', gid = temp_line_id2)
            poly_line3 = ax.plot(x3_new, ffit3, '-k', gid = temp_line_id3)
            vel_label1 = ax.text(mid_x1, poly.polyval(mid_x1, coefs1), str("%.0f" % vel1) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id)
            vel_label2 = ax.text(mid_x2, poly.polyval(mid_x2, coefs2), str("%.0f" % vel2) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id2)
            vel_label3 = ax.text(mid_x3, poly.polyval(mid_x3, coefs3), str("%.0f" % vel3) + ' m/s', ha='center', va='center',color='k',rotation=0,bbox={'facecolor':'white', 'alpha':0.9, 'pad':3}, gid = temp_label_id3)
            print(line3_x)


            #Layer 1
        #elif temp_nlayers == 3:
            #do stuff
        else:
            print('unknown number of layers')


        #data_i = 0

        fig.canvas.draw()
        print('Line auto tool')
    def clear_autoline(i):
        for j in reversed(ax.lines):
            print(j.get_gid())
            if ('line' in j.get_gid() and 'row' + str(i) in j.get_gid()):
                print(j.get_gid(), ' is getting removed')
                j.remove()

        for j in reversed(ax.texts):
            if ('text' in j.get_gid() and 'row' + str(i) in j.get_gid()):
                print(j.get_gid(), ' is getting removed')
                j.remove()
        fig.canvas.draw()
    def autoline_done():
        print(nlayer_entries[0].get())
        #plot_autoline(1)
        root4.destroy()
        ax.figure.canvas.draw()
    def show_boxes(row, n_layers):
        if n_layers == 1:
            #xhinge1_entries.append(0)
            #xhinge2_entries.append(0)
            Button(root4, text='Plot', command= lambda row=row: plot_autoline(row, 1, '', '')).grid(row=row, column=9, sticky=W, pady=4)
            Button(root4, text='Clear', command= lambda row=row: clear_autoline(row)).grid(row=row, column=10, sticky=W, pady=4)  
        if n_layers == 2:
            print('dog')
            Label(root4, text='x val for hinge point 1').grid(row=row, column = 4)
            
            e2 = Entry(root4) 
            e2.grid(row=row, column=5)

            print(xhinge1_entries)
            Button(root4, text='Plot', command= lambda row=row: plot_autoline(row, 2, float(e2.get()), '')).grid(row=row, column=9, sticky=W, pady=4)
            Button(root4, text='Clear', command= lambda row=row: clear_autoline(row)).grid(row=row, column=10, sticky=W, pady=4)  
        if n_layers == 3:

            Label(root4, text='x val for hinge point 1').grid(row=row, column = 4)
            
            e2 = Entry(root4) 
            e2.grid(row=row, column=5)
            xhinge1_entries.append(e2)

            Label(root4, text='x val for hinge point 2').grid(row=row, column = 6)
            
            e3 = Entry(root4) 
            e3.grid(row=row, column=7)
            #xhinge2_entries.append(e3)

            Button(root4, text='Plot', command= lambda row=row: plot_autoline(row, 3, float(e2.get()), float(e3.get()))).grid(row=row, column=7, sticky=W, pady=4)
            Button(root4, text='Clear', command= lambda row=row: clear_autoline(row)).grid(row=row, column=5, sticky=W, pady=4)
    
    root4 = Toplevel()                                 # Creates a second window. Because we can't have multiple TKs, we create a Toplevel
    root4.wm_title("Auto line plot") 
    
    #print('length = ', len(ax.lines))
    #print('range = ', range(len(ax.lines))

        #ax.lines line has label (501.sgy), gid (picks0)



    for i in range(len(ax.lines)):
        if 'picks' in ax.lines[i].get_gid():
            Label(root4, text=ax.lines[i].get_label()).grid(row=i) #Reads label from 
            Label(root4, text='N Layers').grid(row=i, column = 1)
            #print(ax.lines.get_label())
            #labels = [o.get_label() for o in ax.lines if 'picks' in o.get_gid()] # This is called a Generator expression
            #print([o.get_label() for o in ax.lines if o.get_label() == '501.txt']) # This generator will find the line with a specified label
            #print(labels)



            e1 = Entry(root4)                            # TK entry function
            #e1.insert(0, current_xlim[0])               # Enters current axis limit
            e1.grid(row=i, column=2)
            nlayer_entries.append(e1)

            Button(root4, text='Go', command= lambda i=i: show_boxes(i, int(nlayer_entries[i].get()))).grid(row=i, column=3, sticky=W, pady=4)


    Button(root4, text='Done', command=autoline_done).grid(row=5, column=1, sticky=W, pady=4)


#A Root creates an ordinary window. You should only create one root widget for each program, and it must be created before any other widgets.
root2 = Tk()                          #Initialises the TK interpreter and creates a root window
root2.wm_title("Time-Distance curves")        #Window title

root2.minsize(width=1000, height=600)

# Create a tk.DrawingArea
canvas = FigureCanvasTkAgg(fig, master=root2)
canvas.show()

canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)  

# Buttons

open_button = Button(master=root2, text='Open', command=open_picks) #Define the button
open_button.pack(side=LEFT) #Where the widget goes

clear_button = Button(master=root2, text='Clear', command=clear_picks) #Define the button
clear_button.pack(side=LEFT) #Where the widget goes

save_button = Button(master=root2, text='Save fig', command=save_fig) #Define the button
save_button.pack(side=LEFT) #Where the widget goes

quit_button = Button(master=root2, text='Quit', command=destroy) #Define the button
quit_button.pack(side=LEFT) #Where the widget goes

point_button = Button(master=root2, text='Get xy', command=pick_point) #Define the button
point_button.pack(side=RIGHT) #Where the widget goes

axis_button = Button(master=root2, text='Set Axis', command=set_axis) #Define the button
axis_button.pack(side=RIGHT) #Where the widget goes

remove_line_button = Button(master=root2, text='Remove last line', command=remove_line) #Define the button
remove_line_button.pack(side=RIGHT) #Where the widget goes

pickline_button = Button(master=root2, text='Pick Line', command=pick_line) #Define the button
pickline_button.pack(side=RIGHT) #Where the widget goes

autoline_button = Button(master=root2, text='Auto Pick Line', command=auto_line) #Define the button
autoline_button.pack(side=RIGHT) #Where the widget goes

root2.protocol("WM_DELETE_WINDOW", on_closing)
#plt.gcf().subplots_adjust(bottom=0.2)
root2.mainloop()


