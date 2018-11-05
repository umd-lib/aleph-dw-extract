#!/usr/bin/env python
import fileinput
import pdb
import sys
#pdb.set_trace()


flags = ''
old_flag = ''
old_table = ''
old_key = ''
global table, key
table = ''
key = ''

lst_filename = sys.argv[1]
lib = lst_filename.split('_')[0]
tab = lst_filename.split('_')[1].split('.')[0]
filename = lib + "_" + tab + "_b"
f = open(filename, 'w+')

def dump_it(table, key):
    global flags, old_table, old_key, old_flag
    if flags:
        option = '?'
        first = flags[0]
        last = flags[-1]
        if (first == 'D' and last == 'I'):
            option = 'U'
        elif (first == 'I' and last == 'D'):
            option = 'Z'
        elif (first =='U' and  last == 'D'):
            option = 'D'
        else:
            option = first
    	# format output
    	f.write(option.ljust(10) + ' ' + old_table + ' ' + old_key +'\n')
    flags = ''
    old_table = table
    old_key = key
    old_flag = '' 

for line in fileinput.input():
    line = line.rstrip()
    flag = line[0]
    timestamp = line[3:23]
    table = line[25:35]
    key = line[37:]
    
    if (key!=old_key or table != old_table):
        dump_it(table, key)
    if (flag != old_flag):
        flags = flags + flag
        old_flag = flag
dump_it(table, key)
f.close()
