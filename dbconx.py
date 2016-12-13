#!/usr/bin/python

import mysql.connector
import sys

hostname = "localhost"
username = "rtooappusr"
password = "lab123"
db = "rtooappdb"

cnx = mysql.connector.connect(user=username, database=db,password=password,buffered=True)
