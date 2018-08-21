# SEI Project

Text search engine project in Systex Corporation. This is like Ctrl + F but more complicated. User can search keywords on their own way.

## Function

This search engine support the following searching methods:
1. ```+``` ,  ```-```  
```A - B + C```: articles contain keyword A and keyword C but not contain keyword B.  
2. ```AND```, ```OR```  
```(W) OR (X) AND (Y)```: articles satisfiy condition W or condition X and contidion Y. The precedence of ```AND``` is hgher than ```OR```.  
3. ```30, (A + B)```  
    Within 30 words, if it contains keyword A and keyword B, then this article is what we need.  
4. ```co#@4@#tion```  
    We allow keywords which contain **co** as prefix and **tion** as postfix and at most three letters between prefix and postfix. For example, articles contain **combination** or **collection** are what we need. Howerver, **communication** is not what we need.

## Prerequisites

Iinstall Python.

## Running

Run seach_engine_gui.py
## Authors
* 薛光佑 Alex ayo84616@gmail.com
* 賴冠宇 Gary sasuke11291@gmail.com
* 陳翰申 Sheng lf963@hotmail.com
