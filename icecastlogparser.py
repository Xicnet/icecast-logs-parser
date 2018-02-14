#!/usr/bin/python

# icecastServerLogParser.py
# Alejandro Ferrari <support@wmconsulting.info>
# version 1.0


"""
Parser for ICECAST server log output, of the form:

190.49.XX.XX - - [25/Jun/2012:04:50:59 -0300]
"GET /Retromix_64.mp3?1340608279543.mp3 HTTP/1.1" 200 19143936
"http://player.domain.com/player/Flash/"
"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.5 (KH" 2385

You can then break it up as follows:
IP ADDRESS - -
Server Date / Time [SPACE]
"GET /path/to/stream
HTTP/Type Request"
Success Code
Bytes Sent To Client
Referer
Clien Software/User-Agent
Session Duration Time
"""

from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
import string
import glob
import sys
from psycopg2.extras import execute_values
import pygeoip
import time
import re
from datetime import datetime
from datetime import timedelta
from socket import gethostname

#################################################
# Configurations
#################################################
# Server Name for identify where the Hit was
server_name = gethostname().lower()

# glob supports Unix style pathname extensions
# Here need to put the Access log file name you need parse
python_files = glob.glob("/var/log/icecast2/access.log")

# Put the correct path to your .DAT GeoIP DB
gi  = pygeoip.GeoIP('/usr/share/GeoIP/GeoIP.dat')
gic = pygeoip.GeoIP('/usr/share/GeoIP/GeoLiteCity.dat')

# DB Params
db_host = "localhost"
db_user = "icelog"
db_passwd = "icelog"
db_name  = "icelog"

# Filters (Skip this lines if match, using regex)
filter_ip = r'54.146.35|10.10'

# Number of inserts per query
HIST_PER_QUERY = 10


#################################################
# Dont modify below this line
#################################################

try:
    import MySQLdb
    try:
        print "Trying MySQL..."
        conn = MySQLdb.connect (host = db_host, user = db_user, passwd = db_passwd, db = db_name)
        db_type = "mysql"
    except MySQLdb.Error, e:
        print "Error using MySQL %d: %s" % (e.args[0], e.args[1])
except:
    import psycopg2
    try:
        print "Trying Postgres..."
        conn = psycopg2.connect("dbname=icelog user=icelog password=icelog host=localhost")
        cursor = conn.cursor()
        db_type = "pg"
    except Exception, e:
        print "Error using Postgres: ", str(e)
        sys.exit (1)

def insert_to_mysql(values_to_insert):
    global conn, db_type
    cursor = conn.cursor()
    try:
        # Execute the SQL command
        query = "INSERT INTO icecast_logs (datetime_start, datetime_end, ip, country_code, mount, status_code, duration, sent_bytes, agent, referer, server, auth_user, auth_pass) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, values_to_insert)
        # Commit your changes in the database
        conn.commit()
    except MySQLdb.Error, e:
        # Rollback in case there is any error
        print "An error has been passed. %s" % e
        conn.rollback()
        cursor.close()
        hits_counter = 0
        query = ""

def insert_to_pg(values_to_insert):
    global conn, db_type
    cursor = conn.cursor()
    try:
        query = "INSERT INTO icecast_logs (datetime_start, datetime_end, ip, country_code, mount, status_code, duration, sent_bytes, agent, referer, server, auth_user, auth_pass) VALUES %s"
        execute_values (
            cursor, query, values_to_insert, template=None, page_size=100
        )
        # Commit your changes in the database
        conn.commit()
    except Exception, e:
        # Rollback in case there is any error
        print "An error has been passed: %s" % str(e)
        conn.rollback()
        cursor.close()
        hits_counter = 0
        query = ""

if db_type == "mysql":
    insert_to_db = insert_to_mysql
else:
    insert_to_db = insert_to_pg

def getCmdFields( s, l, t ):
    t["method"],t["requestURI"],t["protocolVersion"] = t[0].strip('"').split()

logLineBNF = None
def getLogLineBNF():
    global logLineBNF

    if logLineBNF is None:
        integer = Word( nums )
        ipAddress = delimitedList( integer, ".", combine=True )

        timeZoneOffset = Word("+-",nums)
        month = Word(string.uppercase, string.lowercase, exact=3)
        serverDateTime = Group( Suppress("[") + Combine( integer + "/" + month + "/" + integer + ":" + integer + ":" + integer + ":" + integer ) + timeZoneOffset + Suppress("]") )

        # 10.0.1.1 - - [14/Feb/2018:16:58:00 +0000] "GET /live.mp3 HTTP/1.0" 200 17059093 "-" "MPlayer 1.2.1 (Debian), built with gcc-5.3.1" 1063
        logLineBNF = ( ipAddress.setResultsName("ipAddr") +
                       Suppress("-") +
                       ("-" | Word( alphas+nums+"@._" )).setResultsName("auth") +
                       serverDateTime.setResultsName("timestamp") +
                       dblQuotedString.setResultsName("cmd").setParseAction(getCmdFields) +
                       (integer | "-").setResultsName("statusCode") +
                       (integer | "-").setResultsName("numBytesSent")  +
                       (dblQuotedString | "-").setResultsName("referer").setParseAction(removeQuotes) +
                       dblQuotedString.setResultsName("userAgent").setParseAction(removeQuotes) +
		       (integer | "-").setResultsName("numDurationTime"))
    return logLineBNF
# Variable definition
hits_counter = 0
query = ""
values_to_insert = []
for file_name in sorted(python_files):
    with open(file_name) as f:
        for line in f:
		if not line: continue
	    	fields = getLogLineBNF().parseString(line)
        	countryCode = gi.country_code_by_addr(fields.ipAddr)
	        streamName = fields.requestURI.strip('/').split('?')
	
	        if re.match(filter_ip, fields.ipAddr, flags=0):
	            continue
	        else:
	            datetime_end = datetime.strptime(fields.timestamp[0],"%d/%b/%Y:%H:%M:%S")
	            datetime_start = datetime_end - timedelta(seconds=int(fields.numDurationTime))
	
	        if hits_counter == HIST_PER_QUERY:
	            # prepare a cursor object using cursor() method
                    insert_to_db(values_to_insert)
	        else:
	            #query = query + "INSERT INTO icecast_logs (datetime_start, datetime_end, ip, country_code, mount, status_code, duration, sent_bytes, agent, referer, server, auth_user, auth_pass) \
		#			VALUES('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, {7}, '{8}', '{9}', '{10}', '{11}', '{12}');".format(datetime_start, datetime_end, fields.ipAddr, countryCode, streamName[0], fields.statusCode, fields.numDurationTime, fields.numBytesSent, fields.userAgent, fields.referer, server_name, fields.userName, fields.password)
		    values_to_insert.append((datetime_start, datetime_end, fields.ipAddr, countryCode, streamName[0], fields.statusCode, fields.numDurationTime, fields.numBytesSent, fields.userAgent, fields.referer, server_name, fields.userName, fields.password))
	            hits_counter+=1
#		    print query
conn.close ()

