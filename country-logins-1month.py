#!/usr/bin/python
#
# list of countries an ftp account has logged in from in the last X months (right now 1 month)
#

# ignores private LAN IP ranges, and a few accounts we aren't concerned with.

# example crontab entry:
# 55 11 * * sun	python country-logins-1month.py | sort -rn | mail -s "ftp logins by country last month" sysadmins@company.com

#
# this is very rough code, but also serves as an example of GeoIP and UTMP (last log file) info extraction in Python
#


import fileinput, GeoIP, pprint


gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)


import utmp
from UTMPCONST import *
import time
import socket
import struct

import datetime
one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
sixmonthsago = datetime.date.today() - datetime.timedelta(days=(365 / 2))
onemonthago = datetime.date.today() - datetime.timedelta(days=(365 / 12))

a = utmp.UtmpRecord(WTMP_FILE)

localnets = [['10', '10'],
             ['0', '0'],
             ['172','22'],
             ['127', '0']]

ignorelogins = ['fred',
                'mary',
                'bill',
                'sue']             

countries = {}

while 1:
    b = a.getutent()
    if not b:
        break
    if datetime.date.fromtimestamp(b.ut_tv[0]) > onemonthago and b[0] == USER_PROCESS:
        ip = socket.inet_ntoa(struct.pack('I',b.ut_addr_v6[0] & 0xFFFFFFFF))
        # print ip.split('.')[0:2]
        if b.ut_line[0:4] == 'ftpd' and ip.split('.')[0:2] not in localnets and b.ut_user not in ignorelogins:
           # print "%-10s %-10s %-30s %-20s " % (b.ut_user, b.ut_line, b.ut_host, time.ctime(b.ut_tv[0])),ip,gi.country_code_by_addr(ip)
           if countries.has_key(b.ut_user):
              if countries[b.ut_user].has_key(gi.country_code_by_addr(ip)):
                 countries[b.ut_user][gi.country_code_by_addr(ip)] = countries[b.ut_user][gi.country_code_by_addr(ip)] + 1
              else:
                 countries[b.ut_user][gi.country_code_by_addr(ip)] = 1
           else:
              countries[b.ut_user] = {gi.country_code_by_addr(ip) : 1}
           
           
a.endutent()
for username in countries:
   print len(countries[username]),username,countries[username]
