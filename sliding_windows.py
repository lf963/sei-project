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
import pandas as pd
import os
import sqlite3



def load_data():
    return pd.read_sql('SELECT * FROM wiki', con=sqlite3.connect('/Users/garylai/Desktop/News.sqlite'), index_col='id')
       


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

    

            
def processing(length, is_doc, in_list, out_list, wiki):
    get_docs = []
    get_all_sentence = []
    run = 0
    for doc in is_doc:
        get_sentence = []
#        print(run)
        slide_in_list = []
        slide_out_list = []
        for check in in_list:
            if type(check) == str:
                slide_in_list.append([m.start() for m in re.finditer(check.lower(),wiki['text'][doc].lower())])
            else:
                f_word = [m.start() for m in re.finditer(check[0].lower(),wiki['text'][doc].lower())]
                s_word = [m.start() for m in re.finditer(check[1].lower(),wiki['text'][doc].lower())]
                c_word = []
                
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_in_list.append(c_word)
                
        for check in out_list:
            if type(check) == str:
                slide_out_list.append([m.start() for m in re.finditer(check.lower(),wiki['text'][doc].lower())])
            else:
                f_word = [m.start() for m in re.finditer(check[0].lower(),wiki['text'][doc].lower())]
                s_word = [m.start() for m in re.finditer(check[1].lower(),wiki['text'][doc].lower())]
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
            get_sentence += [start]
            get_all_sentence.append(get_sentence)
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
            m = len(slide_doc[0])
            
            
            pad_doc_in = np.pad(slide_doc[:len(in_list),:], ((0,0),(length-1,length-1)), 'constant', constant_values=(False, False))
            pad_doc_out = np.pad(slide_doc[len(in_list):,:], ((0,0),(length+l-1,length+l-1)), 'constant', constant_values=(False, False))
            
            slide_doc_in = np.max(sliding_window(pad_doc_in, size = (2*length-1), stepsize=1),axis=2).reshape(k,m)
            slide_doc_out = np.min(np.invert(sliding_window(pad_doc_out, size = (2*(length+l)-1), stepsize=1)),axis=2).reshape(l,m)
            slide_doc_all = np.concatenate((slide_doc_in, slide_doc_out), axis=0)
            
            entre = np.where(slide_doc_all.sum(axis=1) == min(slide_doc_all.sum(axis=1)))[0][0]
            for i in np.where(slide_doc_all[entre,:] == True)[0]:
                if not(False in slide_doc_all[:,i]):
                    if doc not in get_docs:
                        get_docs.append(doc)
                    get_sentence += [i+start]
            if len(get_sentence ) != 0:
                get_all_sentence.append(get_sentence)
        run+=1
    return get_docs, get_all_sentence

    
def get_word_sentence(length, get_docs, get_all_sentence, wiki):
    get_position = []
    for i in range(len(get_docs)):
        word = get_all_sentence[i]
        position = []
        for j in range(len(word)-1):
            if abs(word[j+1] - word[j]) >1:
                position += [word[j]]
        position += [word[len(word)-1]]
        get_position.append(position)
        
    sentence = {}
    for i in range(len(get_docs)):
        doc = get_docs[i]
        doc_sentence=[]
        for j in get_position[i]:
            k = max(0,j-(2*length-1))
            doc_sentence += [wiki['text'][doc][k:j+length]]
        sentence[wiki['title'][doc]] = doc_sentence
    
    return sentence
                        


def get_doc(is_doc, wiki):
    title = []
    for i in is_doc:
        title.append(wiki['text'][i])
    return title, is_doc


def main(input_processing, wiki):
    t0 = time.time()
    search_answer = []
    all_sentence = {}
    for searching in input_processing:
        length = int(searching[0])
        is_doc = searching[1]
        in_list = searching[2]
        out_list = searching[3]
        get_docs, get_all_sentence = processing(length, is_doc, in_list, out_list, wiki)
        title, doc_index = get_doc(get_docs, wiki)
        all_sentence.update(get_word_sentence(length, get_docs, get_all_sentence, wiki))
        search_answer.append(doc_index)
    print(time.time()-t0)
    return search_answer, all_sentence
    

if __name__ == '__main__':
    wiki = load_data()
    main(input_processing,wiki)
