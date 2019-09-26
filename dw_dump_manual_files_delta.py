from datetime import datetime, timedelta
import sys
from os import listdir
from shutil import copyfile
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
today_date = today.strftime('%Y%m%d')
today_date_path = os.path.join('data', today_date)

# figure out previous date
yesterday = today - timedelta(days=1)
yesterday_date = yesterday.strftime('%Y%m%d')
yesterday_date_path = os.path.join('data', yesterday_date)

# path to manual files
mpf_path = 'manual-files'

mpf_files = [
    'item-status-dimension.txt',
    'item-process-status-dimension.txt',
    'library-collection-dimension.txt',
    'library-entity-dimension.txt',
    'material-form-dimension.txt',
    'member-library-dimension.txt'
    ]

# copy all mpf files into today's directory
for filename in mpf_files:
    manual_file_path = os.path.join(mpf_path, filename)
    destination_file_path = os.path.join(today_date_path, filename) 
    copyfile(manual_file_path, destination_file_path)

'''
get the first lines out of each previous mpf file and put into a dict
'''
first_lines = {}

for filename in mpf_files:
    # get yesterday's filepath
    yesterday_file = os.path.join(yesterday_date_path, filename)
    with open(yesterday_file) as f:
        line1 = f.readline() # header1
        line2 = f.readline() # header 2
        first_line = f.readline()
        first_lines[filename] = first_line


'''
use first lines to write new file of only incremental changes for today's date
'''
# read the MPF file until the same line is reached and stop.
for filename in mpf_files:

    # output file
    output_filename = 'mpf_' + filename

    # use the first_line from previous cumulative mpf file from the first_lines dict
    line_to_match = first_lines[filename]

    output_lines = []
    
    today_file = os.path.join(today_date_path, filename)
    with open(today_file) as f:
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
	new_file_path = os.path.join(today_date_path, output_filename)
        open(new_file_path, 'a').close()

        # write new lines to the output file in data/{next_date}
        if has_new_lines:
            new_file = open(new_file_path, 'w')
            with new_file as f:
                for line in output_lines:
                    f.write(line)

