#Data Migration
import cherrypy
import pyodbc
import psycopg2
from psycopg2 import DatabaseError

import os
import time


class Client_UI(object):
    @cherrypy.expose
    def index(self):
        return open("HTML\Index.html").read()

    @cherrypy.expose
    def user_input(self,databasenameSQL,databasenamePSQL,usernameSQL,usernamePSQL,passwordSQL,passwordPSQL,serverIPSQL,serverIPPSQL,portPSQL,tablenameSQL,tablenamePSQL):

        if not (databasenameSQL or databasenamePSQL or usernameSQL or usernamePSQL or passwordSQL or passwordPSQL or serverIPSQL or serverIPPSQL or portPSQL):
            return open("HTML\Error.html").read()
        elif not(databasenameSQL and databasenamePSQL and usernameSQL and usernamePSQL and passwordSQL and passwordPSQL and serverIPSQL and serverIPPSQL and portPSQL):
            return open("HTML\Error.html").read()
        else:
            #return open("HTML\confirmation.html").read().format(databasenameSQL,usernameSQL,passwordSQL,serverIPSQL,tablenameSQL,databasenamePSQL,usernamePSQL,passwordPSQL,serverIPPSQL,portPSQL,tablenamePSQL)
            try:

                item = 'SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection=no;'.format(serverIPSQL, databasenameSQL,
                                                                                           usernameSQL, passwordSQL)
                connSQL = pyodbc.connect('DRIVER={SQL Server};' + item)

                connPostgre = psycopg2.connect(database=databasenamePSQL,
                                               user=usernamePSQL,
                                               password=passwordPSQL,
                                               host=serverIPPSQL,
                                               port=portPSQL)

                cursorPostgre = connPostgre.cursor()
                cursorSQL = connSQL.cursor()

                cursorSQL.execute(
                    "select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'".format(tablenameSQL))

                for i in cursorSQL:
                    print(str(i).replace("(", "").replace("'", "").replace(",", "").replace(")", ""))

                    try:

                        cursorPostgre.execute('''CREATE TABLE {} ({});'''.format(tablenamePSQL,
                                                                                 str(i).replace("(", "").replace("'",
                                                                                                                 "").replace(
                                                                                     ",", "").replace(")", "")))
                        connPostgre.commit()

                    except:

                        connPostgre.rollback()
                        cursorPostgre.execute('''ALTER TABLE {} ADD {}'''.format(tablenamePSQL,
                                                                                 str(i).replace("(", "").replace("'",
                                                                                                                 "").replace(
                                                                                     ",", "").replace(")", "")))
                        connPostgre.commit()

                cursorSQL.execute("select * from data")

                for i in cursorSQL:
                    insert_query = "INSERT INTO {} VALUES {}".format(tablenamePSQL, i)

                    cursorPostgre.execute(insert_query)
                    connPostgre.commit()

            except:
                return "Some Error occcured please try again!"
            else:

                return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bootstrap Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
</head>
<body>

<div class="container">
  
  <div class="alert alert-success">
    <strong>Database Migrated Successfully!</strong> 
  </div>
</div>

</body>
</html>'''

cherrypy.config.update({'server.socket_port': 2421})

cherrypy.quickstart(Client_UI())


# from migration import *
# import time
# import progressbar
#
# widgets=[
#     ' [', progressbar.Timer(), '] ',
#     progressbar.Bar(),
#     ' (', progressbar.ETA(), ') ',
# ]
# print(iter(progressbar.progressbar(migration("data","OL88L"), widgets=widgets))
