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



def load_data():
    file_path = os.path.join(os.getcwd(),'wiki2.csv')
    wiki = pd.read_csv(file_path, header = None, index_col = 0)
    return wiki


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
    run = 0
    for doc in is_doc:
        print(run)
        slide_in_list = []
        slide_out_list = []
        for check in in_list:
            if type(check) == str:
                slide_in_list.append([m.start() for m in re.finditer(check,wiki[3][doc])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki[3][doc])]
                s_word = [m.start() for m in re.finditer(check[1],wiki[3][doc])]
                c_word = []
                
                for i in f_word:
                    for j in s_word:
                        if abs(i-j) <= len(check[0])+check[2]:
                            c_word.append(i)
                slide_in_list.append(c_word)
                
        for check in out_list:
            if type(check) == str:
                slide_out_list.append([m.start() for m in re.finditer(check,wiki[3][doc])])
            else:
                f_word = [m.start() for m in re.finditer(check[0],wiki[3][doc])]
                s_word = [m.start() for m in re.finditer(check[1],wiki[3][doc])]
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


def get_doc(is_doc, wiki):
    title = []
    for i in is_doc:
        title.append(wiki[3][i])
    return title, is_doc


def main(input_processing, wiki):
    t0 = time.time()
    search_answer = []
    for searching in input_processing:
        length = int(searching[0])
        is_doc = searching[1]
        in_list = searching[2]
        out_list = searching[3]
        title, doc_index = get_doc(processing(length, is_doc, in_list, out_list, wiki), wiki)
        search_answer.append(doc_index)
    print(time.time()-t0)
    return search_answer
    

if __name__ == '__main__':
    wiki = load_data()
    main(input_processing,wiki)
