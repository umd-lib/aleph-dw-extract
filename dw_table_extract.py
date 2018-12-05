#!/lims/22/bin/python

import cx_Oracle
import subprocess
from subprocess import Popen, PIPE
import sys, getopt
import re
import pdb
from datetime import datetime


# get vars from cli arguments
if (len(sys.argv) != 6):
     print "Bad number of parameters.\n" 
library = sys.argv[1]
table = sys.argv[2]
infile = sys.argv[3]
outfile = sys.argv[4]
suffix = sys.argv[5]

# function to set up the SQL
def setup_sql():
    in_sql = "sql/" + table
    sql = ''
    try:
        with open(in_sql, 'r') as in_sql:
            for line in in_sql:
                line = line.rstrip()
		# look for ? and change to :key
		line = line.replace('?', ':key')
                keylength_match = re.match('keylength=(\d+)$', line)
                if bool(keylength_match):
                    keylength = keylength_match[0]
                else:
                    sql = sql + line + ' '
            #sql = in_sql.read()
            return sql
    except:
        print "Could not open in_sql file"
    
def oracle_connect(library, password):
    connection = cx_Oracle.connect(library, password)
    connection.autocommit = False
    return connection

def get_ora_passwd():
    # get the oracle password
    session  = Popen(['get_ora_passwd', library], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = session.communicate()
    password = output
    return password
    
# concatenate parts of SQL together from the infile
sql = setup_sql()
# connect to Oracle
password = get_ora_passwd().rstrip()
connection = oracle_connect(library, password)
# prepare cursor
cursor = connection.cursor()
cursor.prepare(sql)


class FileReadException(Exception):
    def __init__(self, file_name, file, error_str):
	Exception.__init__(self, "Failed to open " + file_name + ", error: " + error_str)

# read infile
def read_in_file(infile):
    try:
	with open(infile, "rb") as file:
            in_contents = file.read().decode('utf-8').splitlines()
    except IOError as e:
        raise FileReadException("infile", infile, e.strerror)
    return in_contents

def open_out_file(outfile):
    try:
        out_outfile = open(outfile, 'w')
    except IOError as e:
        raise FileReadException("outfile", outfile, e.strerror)
    return out_outfile
    
#  try opening in and outfile. raises an uncatched FileReadException. 
in_contents = read_in_file(infile)
OUT = open_out_file(outfile)

# write header first line
OUT.write('H\t' + 'DW Extract Job Number(work on this)\t' + str(suffix) + '\t' + outfile + '\n')

# get column names
cursor.execute('select * from ' + table)
col_names = [row[0] for row in cursor.description]
ts_columns = '\t'.join(map(str, col_names))
# write header second line with column names
OUT.write('H\t' + ts_columns + '\n') 

# count detail records
record_count = 0
# use the flag and key from the flag file to build SQL statements
for line in in_contents:
    #print line
    line = line.rstrip().encode('utf-8')
    flag = line[0]
    key = line[22:] # character 22 to the end
    # bind key to sql where the :key variable is
    cursor.execute(sql, key=key)
    row = cursor.fetchall()
    if row:
        row_data = row[0][0]
        if flag == 'D':
            print "Unexpected result for: " + str(flag) + ' ' + str(key)
        else:
            # write a D \t flag \t key \t data
            OUT.write('D\t' + str(flag)+'\t'+str(key)+'\t' + str(row_data) + '\n')
	    record_count+=1
    else:
        if flag == 'D':
            OUT.write('D\t' + str(flag)+'\t'+str(key)+'\n')
	    record_count+=1
        else:
            print "Unexpected missing record for: " + str(flag) + ' ' + str(key)


# end time
end_time = datetime.now()
# write trailer record
OUT.write('T\t' + str(end_time) + '\t' + str(record_count) + '\n')
# close OUT 
OUT.close()                    


