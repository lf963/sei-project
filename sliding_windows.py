#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 11:55:49 2018

@author: garylai
"""
from numpy.lib.stride_tricks import as_strided
from itertools import compress
import operator
import numpy as np
import time       
import csv
import re


def load_data():
    wiki = []
    with open('/Users/garylai/Desktop/wiki2.csv', newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(row)
            wiki.append(row)
    wiki_dict = dict((wi[0], wi[1:]) for wi in wiki)
    return wiki_dict
        
def input_word():
    print('請輸入欲搜尋的字詞')
    check_word = input('Enter your input:')
    return check_word

def input_window():
    print('請輸入欲限制的出現字數')
    window_length = input('Enter your input:')
    window_length = int(window_length)
    return window_length

def in_out_list(check_word):
    all_list = []
    in_list = []
    out_list = []
    if check_word[0] == '+' or check_word[0] == '-':
        add = [m.start() for m in re.finditer('\+',check_word)]
        mi = [m.start() for m in re.finditer('\-',check_word)]
        all_ = mi+add
        all_.sort()
        for i in range(len(all_)-1):
            all_list.append(check_word[all_[i]+1:all_[i+1]].split()[0])
        all_list.append(check_word[all_[-1]+1:].split()[0])
        for i in add:
            in_list.append(all_list[all_.index(i)])
        for i in mi:
            out_list.append(all_list[all_.index(i)])
    else:
        add = [m.start() for m in re.finditer('\+',check_word)]
        mi = [m.start() for m in re.finditer('\-',check_word)]
        all_ = mi+add
        all_.sort()
        in_list.append(check_word[0:all_[0]].split()[0])
        for i in range(len(all_)-1):
            all_list.append(check_word[all_[i]+1:all_[i+1]].split()[0])
        all_list.append(check_word[all_[-1]+1:].split()[0])
        for i in add:
            in_list.append(all_list[all_.index(i)])
        for i in mi:
            out_list.append(all_list[all_.index(i)])
        
    for i in range(len(in_list)):
        if in_list[i][0] == '(':
            in_list[i] = list(filter(None, re.split('\W+', in_list[0])))
            
    for i in range(len(out_list)):
        if out_list[i][0] == '(':
            out_list[i] = list(filter(None, re.split('\W+', out_list[0])))
            
            
            
    return in_list, out_list
        
    
def search_word(in_list):
    is_doc = [x for x in range(len(wiki))]
    for check in range(len(in_list)):
        is_true = []
        for i in is_doc:
            if in_list[check] in wiki[i][3]:
                is_true.append(i)
        is_doc = is_true    
    return is_doc


def sliding_window(data, size, stepsize=1, padded=False, axis=-1, copy=True):

    if axis >= data.ndim:
        raise ValueError(
            "Axis value out of range"
        )

    if stepsize < 1:
        raise ValueError(
            "Stepsize may not be zero or negative"
        )

    if size > data.shape[axis]:
        raise ValueError(
            "Sliding window size may not exceed size of selected axis"
        )

    shape = list(data.shape)
    shape[axis] = np.floor(data.shape[axis] / stepsize - size / stepsize + 1).astype(int)
    shape.append(size)

    strides = list(data.strides)
    strides[axis] *= stepsize
    strides.append(data.strides[axis])

    strided = as_strided(
        data, shape=shape, strides=strides
    )

    if copy:
        return strided.copy()
    else:
        return strided

            
def processing(length, is_doc, in_list, out_list):
    get_docs = []
    run = 0
    for doc in is_doc:
        print(run)
        slide_in_list = []
        slide_out_list = []
        doc = str(doc)
        for check in in_list:
            if type(check) == str:
                slide_in_list.append([m.start() for m in re.finditer(check,wiki[doc][2])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki[doc][2])]
                s_word = [m.start() for m in re.finditer(check[1],wiki[doc][2])]
                c_word = []
                
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_in_list.append(c_word)
                
        for check in out_list:
            if type(check) == str:
                slide_out_list.append([m.start() for m in re.finditer(check,wiki[doc][2])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki[doc][2])]
                s_word = [m.start() for m in re.finditer(check[1],wiki[doc][2])]
                c_word = []
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_out_list.append(c_word)
        
        if len([x for x in slide_out_list if x != []]) > 0:
            end = max([max([sublist[-1] for sublist in slide_in_list]),max([sublist[-1] for sublist in slide_out_list if sublist != []])])
            start = min([min([sublist[0] for sublist in slide_in_list]),min([sublist[0] for sublist in slide_out_list if sublist != []])])
        else:
            end = max([sublist[-1] for sublist in slide_in_list])
            start = min([sublist[0] for sublist in slide_in_list])
        
        if (end-start <length) & (len([x for x in slide_out_list if x != []]) > 0):
            pass
        elif (end-start <length) & (len([x for x in slide_out_list if x != []]) == 0):
            get_docs.append(doc)
        else:
            slide_doc = np.zeros((len(in_list)+len(out_list),end-start+1), dtype = bool)
            
            iter = 0
            for sublist in slide_in_list:
                if len(sublist) != 0:                    
                    slide_doc[iter,np.asarray(sublist)-start] = True
                else:
                    pass
                iter += 1  
            for sublist in slide_out_list:
                if len(sublist) != 0:                    
                    slide_doc[iter,np.asarray(sublist)-start] = True
                else:
                    pass
                iter += 1
            
            k = len(in_list)
            l = len(out_list)
            m = len(slide_doc[0])-length+1
            
            slide_doc_in = np.max(sliding_window(slide_doc[:len(in_list),:], size = length, stepsize=1),axis=2).reshape(k,m)
            slide_doc_out = np.min(np.invert(sliding_window(slide_doc[len(in_list):,:], size = length, stepsize=1)),axis=2).reshape(l,m)
            slide_doc_all = np.concatenate((slide_doc_in, slide_doc_out), axis=0)
            
            entre = np.where(slide_doc_all.sum(axis=1) == min(slide_doc_all.sum(axis=1)))[0][0]
            for i in np.where(slide_doc_all[entre,:] == True)[0]:
                if not(False in slide_doc_all[:,i]):
                    get_docs.append(doc)
                    break
        run+=1
    return get_docs 


'''----'''
def processing(length, is_doc, in_list, out_list):
    get_docs = []
    run = 0
    for doc in is_doc:
        print(run)
        slide_in_list = []
        slide_out_list = []
        
        for check in in_list:
            if type(check) == str:
                slide_in_list.append([m.start() for m in re.finditer(check,wiki['690'][2])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki['690'][2])]
                s_word = [m.start() for m in re.finditer(check[1],wiki['690'][2])]
                c_word = []
                
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_in_list.append(c_word)
                
        for check in out_list:
            if type(check) == str:
                slide_out_list.append([m.start() for m in re.finditer(check,wiki['690'][2])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki['690'][2])]
                s_word = [m.start() for m in re.finditer(check[1],wiki['690'][2])]
                c_word = []
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_out_list.append(c_word)
        
        if len([x for x in slide_out_list if x != []]) > 0:
            end = max([max([sublist[-1] for sublist in slide_in_list]),max([sublist[-1] for sublist in slide_out_list if sublist != []])])
            start = min([min([sublist[0] for sublist in slide_in_list]),min([sublist[0] for sublist in slide_out_list if sublist != []])])
        else:
            end = max([sublist[-1] for sublist in slide_in_list])
            start = min([sublist[0] for sublist in slide_in_list])
        
        if (end-start <length) & (len([x for x in slide_out_list if x != []]) > 0):
            pass
        elif (end-start <length) & (len([x for x in slide_out_list if x != []]) == 0):
            get_docs.append(doc)
        else:
            slide_doc = np.zeros((len(in_list)+len(out_list),end-start+1), dtype = bool)
            
            iter = 0
            for sublist in slide_in_list:
                if len(sublist) != 0:                    
                    slide_doc[iter,np.asarray(sublist)-start] = True
                else:
                    pass
                iter += 1  
            for sublist in slide_out_list:
                if len(sublist) != 0:                    
                    slide_doc[iter,np.asarray(sublist)-start] = True
                else:
                    pass
                iter += 1
            
            k = len(in_list)
            l = len(out_list)
            m = len(slide_doc[0])-length+1
            
            slide_doc_in = np.max(sliding_window(slide_doc[:len(in_list),:], size = length, stepsize=1),axis=2).reshape(k,m)
            slide_doc_out = np.min(np.invert(sliding_window(slide_doc[len(in_list):,:], size = length, stepsize=1)),axis=2).reshape(l,m)
            slide_doc_all = np.concatenate((slide_doc_in, slide_doc_out), axis=0)
            
            entre = np.where(slide_doc_all.sum(axis=1) == min(slide_doc_all.sum(axis=1)))[0][0]
            for i in np.where(slide_doc_all[entre,:] == True)[0]:
                if not(False in slide_doc_all[:,i]):
                    get_docs.append(doc)
                    break
        run+=1
    return get_docs           


def get_doc(is_doc):
    title = []
    for i in is_doc:
        title.append(wiki[i][2])
    return title, is_doc


def main():
    t0 = time.time()
    search_answer = []
    for searching in input_processing:
        length = searching[0]
        is_doc = searching[1]
        in_list = searching[2]
        out_list = searching[3]
        title, doc_index = get_doc(processing(length, is_doc, in_list, out_list))
        search_answer.append(doc_index)
    print(time.time()-t0)
    return search_answer
    

if __name__ == '__main__':
    main()
