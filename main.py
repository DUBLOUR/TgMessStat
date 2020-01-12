import random
import math
import datetime
import time
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
    
    #local files:
import messparser
import painter


now_chat_id = 0
smooth_id = -1
main_plot_mode = 1
my_name = str()


def print_time_label(text, start=None):
    t = time.process_time()
    if start != None:
        pass
    print(text, f"{t:0}")
    return 0



def build_plot_grid():
    global main_plot,pie_plot,list_chats_plot,fig
    
    #layout, ax = plt.subplots(figsize=(16, 12))
    layout, ax = plt.subplots()
    ax.axis('off')
    layout.canvas.mpl_connect('key_press_event', press)

    layout.canvas.set_window_title('TgStat')
    #layout = plt.figure(constrained_layout=True)
    gs = layout.add_gridspec(4, 4)

    main_plot = layout.add_subplot(gs[:, :-1])
    main_plot.set_title('main')

    pie_plot = layout.add_subplot(gs[0:2, -1:])
    pie_plot.set_title('right-top')

    list_chats_plot = layout.add_subplot(gs[2:, -1:])
    list_chats_plot.set_title('right')

    list_chats_plot.set_frame_on(False)
    #layout.canvas.show(False)
    #list_chats_plot.axis('on')
    #list_chats_plot.axis('off')



def press(event):
    global now_chat_id,smooth_id,main_plot_mode

    #print('press', event.key)
    #sys.stdout.flush()
    key = str(event.key)
    ev = 0
    if key == "left" or key == "up":    now_chat_id -= 1; ev = 1
    if key == "right" or key == "down": now_chat_id += 1; ev = 1
    
    if key == "[": smooth_id -= 1; ev = 2
    if key == "]": smooth_id += 1; ev = 2
    
    if key == " ":
        ev = 3
        main_plot_mode ^= 1
        print("changed")

    if ev != 0:
        last_press_event_time = time.process_time()
        draw_chat(now_chat_id, smooth_id, main_plot_mode)
        print(time.process_time() - last_press_event_time)



def draw_chat(id, smooth_id, main_mode):
    painter.draw_chat(
        id, smooth_id, main_mode, 
        my_name, chat_day_data, 
        main_plot,pie_plot,list_chats_plot
    )
    

def main(debug = False):
    global my_name,chat_day_data
    
    os.system('clear')
    print_time_label("Time, start reading")

    input_file = "result.json"
    if debug:
        input_file = "result_short.json"
    my_name,chat_day_data = messparser.prepare_data(input_file)

    print_time_label("Time, end prepare:")
    build_plot_grid()
    print_time_label("Time, build grid:")

    draw_chat(now_chat_id, smooth_id, main_plot_mode)
    plt.show()


main(debug = 0)