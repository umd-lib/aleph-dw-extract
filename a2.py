#!/usr/bin/env python
import fileinput
import pdb
import sys


# class to parse lines
class ParsedLine:
    def __init__(self, line_string):
        self.line = line_string.rstrip()
        self.flag = self.line[0]
        self.timestamp = self.line[3:23]
        self.table = self.line[25:35]
        self.key = self.line[37:]
        
# class to save series of actions on an item
class ActionSeries:
    def __init__(self, parsed_line):
        self.key = parsed_line.key
	self.table = parsed_line.table
	self.lines = [parsed_line]
	self.flags = parsed_line.flag
    
    def add_line(self, parsed_line):
	self.lines.append(parsed_line)
	self.flags += parsed_line.flag
    
    def print_final_data(self):
        # determine final flag action
	first = self.flags[0]
	last = self.flags[-1]
	if (first == 'D' and last == 'I'):
	    option = 'U'
	elif (first == 'I' and last == 'D'):
	    option = 'Z'
	elif (first ==  'U' and last == 'D'):
	    option = 'D'
	else:
	    option = first
	
        # format and write output
        print(option.ljust(10) + ' ' + self.table + ' ' + self.key)
    
# create ParsedLine object for every line in input file
#lines = [ParsedLine(line) for line in fileinput.input()]
lines = []
for line in fileinput.input():
    lines.append(ParsedLine(line))
# initialize an empty list for action series
all_action_series = []

# create action series if lines refer to same item
for line in lines:
    # check for first iteration
    if all_action_series:
	# add lines with matching key to action series
        last_action_series = all_action_series[-1]
        if (last_action_series.key == line.key and last_action_series.table == line.table):
            last_action_series.add_line(line)
            continue
    # create new action series for non-matching or first iteration line
    all_action_series.append(ActionSeries(line))

# write to standard output
for a in all_action_series:
    a.print_final_data()
    
