#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 09:08:06 2018

@author: garylai
"""

import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import multiprocessing as mp
import and_or_operation
import custom_exception as ex
import search_wildcard
import sliding_windows
import produce_graph_upper
import parse_input
        
print("sliding_windows.load_data()..................")
wiki = sliding_windows.load_data()
window = tk.Tk()
window.title('關鍵字搜尋器')
window.geometry('930x600')

prompt_text = tk.StringVar()
prompt_text = '請輸入欲搜尋的關鍵字'
prompt = tk.Label(window, 
                  text = prompt_text,    # 标签的文字
                  font=('Arial', 10))
prompt.place(x=5, y=6, anchor='nw')

input_num = tk.Entry(window, font=('Verdana',25))
input_num.place(x=5, y=25, width = 60,anchor='nw')

input_text = tk.Entry(window,font=('Verdana',25))
input_text.place(x=70, y=25, width = 700,anchor='nw')


and_or_var = tk.StringVar()

Radio1 = tk.Radiobutton(window, text='And',
                    variable=and_or_var, value='&', bg = '#E5E8E8',
                    width = 8, height = 1, borderwidth=1, relief="groove"
                    )
Radio1.place(x=768, y=26,anchor='nw')

Radio2 = tk.Radiobutton(window, text='Or',
                    variable=and_or_var, value='|', bg = '#E5E8E8',
                    width = 8, height = 1, borderwidth=1, relief="groove"
                    )
Radio2.place(x=768, y=46 ,anchor='nw')


h=0
search_list = []


def Submit_command():
    global h
    global search_list
    global condition_list
    global searched
    global conditional
    
    
    search_text = input_text.get()
    condition_text = and_or_var.get()
    searched = tk.Label(window, 
                    text = search_text,    # 标签的文字
                    font=('Arial', 16),     # 字体和字体大小
                    width=50, height=2,  # 标签长宽
                    borderwidth=2, relief="groove")
    searched.place(x=230, y=90+h, anchor='nw')   # 固定窗口位置
    Radio1.deselect()
    Radio2.deselect()   
    search_list.append('('+search_text+')')
    
    h+=50
    if condition_text == '&':
        conditional_text = 'And'
        conditional = tk.Label(window, 
                       text = conditional_text,    # 标签的文字
                       font=('Arial', 16),     # 字体和字体大小
                       bg = '#FF8F8D',
                       width=50, height=2,  # 标签长宽
                       borderwidth=2, relief="groove")
        conditional.place(x=230, y=90+h, anchor='nw')   # 固定窗口位置
        search_list.append(condition_text)
        h+=50
        
    elif condition_text == '|':
        conditional_text = 'Or'
        conditional = tk.Label(window, 
                       text = conditional_text,    # 标签的文字
                       font=('Arial', 16),     # 字体和字体大小
                       bg = '#921aff',
                       width=50, height=2,  # 标签长宽
                       borderwidth=2, relief="groove")
        conditional.place(x=230, y=90+h, anchor='nw')   # 固定窗口位置
        search_list.append(condition_text)
        h+=50
        
    input_text.delete(0, 'end')


#class App: 
#    def __init__(self, parent):
#        self.parent = parent
#        self.canvas = tk.Canvas(parent, width=320, height=320)
#        self.canvas.place(x=535 , y=150, anchor='nw')
#        self.sequence = [ImageTk.PhotoImage(img) for img in 
#                         ImageSequence.Iterator(Image.open('giphy-downsized.gif'))]
#        self.image = self.canvas.create_image(160, 160, image=self.sequence[0])
#        self.animating = True
#        self.animate(0)
#        
#    def animate(self, counter):
#        self.canvas.itemconfig(self.image, image=self.sequence[counter])
#        if not self.animating:
#            return
#        self.parent.after(90, lambda: self.animate((counter+1) % len(self.sequence)))
#        
#def run_animated():
#    app= App(window)
    
button_num = 3

def Continue_command():
    global continue_button
    global search_list
    global button_num
    
    search_list = []
    
    for widget in window.winfo_children():
        if widget.winfo_class() == 'Label':
            widget.place_forget()
    
    for widget in window.winfo_children():
        if widget.winfo_name() == '!button'+str(button_num):
            widget.place_forget()
        elif widget.winfo_name() == '!button'+str(button_num+1):
            widget.place_forget()
            
    for widget in window.winfo_children():
        if widget.winfo_class() == 'Listbox':
            widget.place_forget()
    
    prompt_text = '請輸入欲搜尋的關鍵字'
    prompt = tk.Label(window, 
                      text = prompt_text,    # 标签的文字
                      font=('Arial', 10))
    prompt.place(x=5, y=6, anchor='nw')
    
    button_num+=2
    
def print_selection():
    global lb
    global sentence
    
    for widget in window.winfo_children():
        if widget.winfo_class() == 'Label':
            widget.place_forget()
    
    var1 = tk.StringVar()
    l =tk.Label(window,bg='white',borderwidth=2 ,relief="ridge" ,
                textvariable=var1 ,anchor=W, justify=LEFT, wraplength = 500 )
    l.place(x = 25, y = 100)
    value = lb.get(lb.curselection())
    run = 0
    for i in sentence[value]:
        if run == 0:
            search_sentence = i
        else:
            search_sentence += '\n'
            search_sentence += i
        run+=1
    var1.set(search_sentence)

    
    
def Search_command():
    global h 
    global searched
    global conditional
    global search_list
    global wiki
    global continue_button
    global prompt
    global consequence
    global lb
    global sentence
#    app = App(window)
    
    h = 0
    for widget in window.winfo_children():
        if widget.winfo_class() == 'Label':
            widget.place_forget()


    if len(search_list) == 0:
        prompt_text = '!!!務必搜尋輸入字詞!!!'
        prompt = tk.Label(window, 
                          text = prompt_text,    # 标签的文字
                          font=('Arial', 10))
        prompt.place(x=5, y=6, anchor='nw')
        pass
    else:
        prompt_text = '搜尋中....'
        prompt = tk.Label(window, 
                          text = prompt_text,    # 标签的文字
                          font=('Arial', 10))
        prompt.place(x=5, y=6, anchor='nw')
        
        
        num = input_num.get()
        if len(num)!=0:
            search = str(input_num.get()) + ',' + ' '.join(w for w in search_list)
        else:
            search = ' '.join(w for w in search_list)
        input_num.delete(0, 'end')
        window_size, rule_list, operator_list, rule = parse_input.parse_main(search)
        print("Call parse_input.py")
        print("Window size = %s" % window_size)
        print(rule_list)
        print(operator_list)
        print("----------------------------------------------------")
        print("call search_wildcard.py")
        if window_size == -1:
            final_result, graph_result, sentence = search_wildcard.step_1(window_size, rule_list)
        else:
            final_result, graph_result = search_wildcard.step_1(window_size, rule_list)
        if int(window_size) != -1:  # window size is not -1, go to sliding_windows.py
            print("sliding_windows.main()..............")
            final_result ,sentence = sliding_windows.main(final_result, wiki)
        else:  # window size is -1, do and/or operation and print
            for result in final_result:
                result.sort()
                for result in final_result:
                    print(result)
                print("----------------------------------------------------")
                print("call and_or_output.py")
        dot, last_node, result = and_or_output.and_or(final_result, operator_list)
        produce_graph_upper.draw(window_size, rule, rule_list, graph_result, final_result, dot, last_node, result)
        
    
        for widget in window.winfo_children():
            if widget.winfo_class() == 'Label':
                widget.place_forget()
    
        prompt_text = '搜尋完成，若要繼續搜尋請點擊按鈕～'
        prompt = tk.Label(window, 
                          text = prompt_text,    # 标签的文字
                          font=('Arial', 10))
        prompt.place(x=5, y=6, anchor='nw')
        
        
    #    im = Image.open("G.gv.png")
    #    photo = ImageTk.PhotoImage(im)
    #
    #    consequence = tk.Label(window, image = photo, bg = 'black')
    ##    consequence.image = photo  # keep a reference!
    #    consequence.place(x=7, y=90, anchor='nw')
        
    #    canvas = Canvas(root, width = 300, height = 300)  
    #    canvas.pack()  
    #    img = ImageTk.PhotoImage(Image.open("G.gv.png"))  
    #    canvas.create_image(20, 20, anchor=NW, image=img)  
    #
        Continue_button = tk.Button(window, text = '繼續搜尋' , command = Continue_command)
        Continue_button.place(x=840, y=500,anchor='nw')
    
             
            
        print_select = tk.Button(window, text='print selection', width=15,
                       height=2, command=print_selection)
        print_select.place(x = 670, y = 200, anchor = 'nw')
        
        var2 = tk.StringVar()
        var2.set(()) 
    
        #创建Listbox
        
        lb = tk.Listbox(window, listvariable=var2)  
        
        #创建一个list并将值循环添加到Listbox控件中
        list_items = list(wiki['title'][result])
        for item in list_items:
            lb.insert('end', item)  #从最后一个位置开始加入值
        lb.place(x = 650, y = 250, anchor = 'nw')
    
        
    
submit_img = tk.PhotoImage(file="add32.png")
search_img = tk.PhotoImage(file="search.png")
search_img = search_img.subsample(1,1)
submit_img = submit_img.subsample(1,1)

Submit_button = tk.Button(window, image = submit_img,width = 38, height = 38, command = Submit_command)
Submit_button.place(x=840, y=25,anchor='nw')

Search_button = tk.Button(window, image = search_img,width = 38, height = 38,
                          command = Search_command)
Search_button.place(x=880, y=25,anchor='nw')

window.mainloop()


