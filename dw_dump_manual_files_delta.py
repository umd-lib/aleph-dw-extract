from datetime import datetime, timedelta
import sys
from os import listdir
import os
import pdb

"""
Script that dumps only the incremental changes to manual files to the data/{date} directory. 

It gets the latest line from the previous day's mpf files, and uses that line to 
grab only the newer lines from files in the manual-files directory. 
Then only the changed lines are written to today's mpf files.  

"""
# get today's date
today = datetime.today()
next_date = today.strftime('%Y%m%d')

# figure out previous date
yesterday = today - timedelta(days=1)
previous_date = yesterday.strftime('%Y%m%d')

mpf_files = [
    'item-status-dimension.txt',
    'item-process-status-dimension.txt',
    'library-collection-dimension.txt',
    'library-entity-dimension.txt',
    'material-form-dimension.txt',
    'member-library-dimension.txt'
    ]


'''
get the first lines out of each previous mpf file and put into a dict
'''
first_lines = {}

for file in mpf_files:
    # get yesterday's filename
    filename = 'mpf_' + file
    previous_date_path = os.path.join('data', previous_date, filename)

    with open(previous_date_path) as f:
        line1 = f.readline() # header1
        line2 = f.readline() # header 2
        first_line = f.readline()

        first_lines[filename] = first_line


'''
use first lines to write new file of only incremental changes for today's date
'''
# read the MPF file until the same line is reached and stop.
for file in mpf_files:
    manual_file = os.path.join('manual-files', file)

    # output file
    output_filename = 'mpf_' + file

    # use the first_line from previous file from the first_lines dict
    line_to_match = first_lines[output_filename]

    output_lines = []

    with open(manual_file) as f:
        output_lines.append(f.readline()) # header 1
        output_lines.append(f.readline()) # header 2

        line = f.readline()
        has_new_lines = False

        # Use the first_line of the older file to create a list of all new lines
        while line:
            if line != line_to_match:
                output_lines.append(line)
                has_new_lines = True
            else:
                break
            line = f.readline()

        # create new file for the new lines (empty at first)
        new_file_path = os.path.join('data', next_date, output_filename)
        #new_file_path = os.path.join('temp', next_date, output_filename)
	open(new_file_path, 'a').close()

        # write new lines to the output file in data/{next_date}
        if has_new_lines:
            new_file = open(new_file_path, 'w')
            with new_file as f:
                for line in output_lines:
                    f.write(line)

