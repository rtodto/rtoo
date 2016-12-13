#!/usr/bin/python

from cmd2 import Cmd
import sys,shlex,re
import os,time,datetime
from tabulate import tabulate
from dbconx import *
import help
import mysql.connector
import rto_network

#Experimental
import argparse

class Cli(Cmd,help.helpd,help.color):
  def __init__(self):
    Cmd.__init__(self)
    print "Type "+self.HEADER+"help"+self.ENDC+" to list all commands"
    print self.OKGREEN+"Available commands:"+self.ENDC+" flash|faq|bookmark|contact|cref|note\n"

    self.prompt = self.colorize('rtoo> ','green')

  def display_msg(self,message):
    """To stop processing and print a warning"""  
    self.message = message
    print ""
    print "WARNING: "+self.message
    print ""
  def missing_param(self):
    print ""
    print self.WARNING+" Missing option!!!"+self.ENDC
    print ""


  ######<BEGIN> FLASH APP, anything starts with do_ gets added to the list automatically#########
  def do_flash(self,args):
    """Flash card main module"""
    self.args = args
    arg_count = len(shlex.split(args))
    if not args:
      self.help_flash()
    else:
      arg = shlex.split(args)

      ##OPTIONS
      if arg[0] == "newdeck" and arg_count==2:
        self.flash_new_deck(arg[1])
      elif (arg[0] == "listdecks" or re.search(r'^l',arg[0]) and arg_count==1):
        self.flash_list_decks()
      elif (arg[0] == "removedeck" or re.search(r'^r',arg[0]) and arg_count==2):
        print arg[1] + " deck is going to be deleted. Please confirm ",
        answer = raw_input("y/n: ")
        if answer=="y":
          self.flash_del_deck(arg[1])
        else:
          print "Removal of the deck cancelled"
      elif arg[0] == "add" or re.search(r'^a',arg[0]):
        #here we need to check how many arguments passed to feed the function properly
        #sentence and flash_note are not mandatory
        if arg_count < 4:
          self.help_flash()
        elif arg_count==4:
          self.flash_add_card(arg[1],arg[2],arg[3],"","")
        elif arg_count==5:
          self.flash_add_card(arg[1],arg[2],arg[3],arg[4],"")
        elif arg_count==6:
          self.flash_add_card(arg[1],arg[2],arg[3],arg[4],arg[5])
      elif (arg[0] == "del" or re.search(r'^d',arg[0])) and arg_count==3:
        self.flash_del_card(arg[1],arg[2])
      elif (arg[0] == "get" or re.search(r'^g',arg[0])) and arg_count==2:
        self.flash_get_card(arg[1],"get")      
      elif (arg[0] == "one" or re.search(r'^o',arg[0]) and arg_count==2):
        self.flash_get_card(arg[1],"one")
      elif ( (arg[0] == "training" or re.search(r't',arg[0])) and arg_count>=3):
        if arg_count==3:
          self.flash_training(arg[1],arg[2],None)
        elif arg_count==4:
          self.flash_training(arg[1],arg[2],arg[3])
      elif ((arg[0] == "show" or re.search(r'^s',arg[0])) and arg_count==3):
        self.flash_show_card(arg[1],arg[2])

      else:
        #paremeter provided isn't valid, display help
        self.help_flash()
   
  def countdown(self,t): # in seconds
    for sec in range(t,0,-1):
        print 'Seconds left: %d\r' % sec,
        sys.stdout.flush()
        time.sleep(1)
 
  def flash_training(self,deckname,num_cards,interval):
    """It displays cards randomly at specified interval"""
    self.deckname_training = deckname
    self.num_cards = int(num_cards)
    if interval == None:
      self.interval = 5
    else:
      self.interval = int(interval)

    os.system('clear')
    count = self.num_cards
    for iter in range(self.num_cards):
      print "\n\n\n\n"
      print "Card # ", count
      self.flash_get_card(self.deckname_training,"get")
      print "\n"
      self.countdown(self.interval)
      os.system('clear')
      count -= 1

    print "####################"
    print "#TRAINING HAS ENDED#"
    print "####################"


  def flash_new_deck(self,deckname):
    """Create a new deck with flash_ prefix"""
    self.deckname = "flash_"+deckname
    if self.flash_deck_avail(self.deckname): 
      self.stdout.write("Deck already exists, please choose a different name\n")
      self.colorize("Test color\n",red)
       
    else:
      cur = cnx.cursor()
      new_deck_query = ( 
        """CREATE TABLE %s (id INT NOT NULL AUTO_INCREMENT,
         front_entry varchar(255) NOT NULL,
         back_entry varchar(255),
         sentence text,
         num_of_display INT DEFAULT 0,
         flash_note text,
         expr_level tinyint,
         next_display datetime,
         last_display datetime,
         img_url varchar(255),
         local_image blob,
         insert_date int,
         PRIMARY KEY (id),
         UNIQUE KEY (front_entry)
        )"""
      )
      #If single entry is fed, % required or comma to make it tuple
      cur.execute(new_deck_query % self.deckname)
      #can't check if the cur.execute run successfully or not, will check later
      if self.flash_deck_avail(self.deckname)>0:
        print self.deckname[6:] + " flash deck is created"
      cur.close()
      return

  def flash_deck_avail(self,deckname):
    """Checks if the table exists or not"""
    self.deckname = deckname
    cur = cnx.cursor()
    cur.execute("SHOW TABLES like %s", (self.deckname,))
    count = cur.rowcount
    cur.close()
    return count

  def flash_list_decks(self):
    """Displays the available decks"""
    cur = cnx.cursor()
    cur.execute("SHOW TABLES like 'flash_%'")
    rows = list(cur.fetchall()) #first return is a tuple
    
    count_decks = cur.rowcount
    
    if count_decks > 0:
      #We need to use list comprehension to remove flash_ prefix
      #brackets around the deckname is IMPORTANT as the element must be also a list to display
      #here rows_converted is a list of list. [ [dutch], [german] ] 
      rows_converted = [ [deckname[0][6:]] for deckname in rows ]
      
      #get number of entries on each deck
      deck_count = [] 
      for deck in rows_converted:
       cur.execute("SELECT id FROM flash_"+str(deck[0]))
       count = cur.rowcount
       deck_count.append([count])
 
      headers = ["Deck Name","# of entries"]

      #Merges counts and table names
      merged_rows = []
      for deck_row in rows_converted:
        for deck_count_row in deck_count:
          if rows_converted.index(deck_row)==deck_count.index(deck_count_row):
            merged_rows.append([deck_row[0],deck_count_row[0]])
 
         
      print tabulate(merged_rows,headers,tablefmt="grid")

      print "\nNumber of decks: "+ str(count_decks)
    else:
      print self.colorize("No deck is created yet","cyan")


  def flash_del_deck(self,deckname):
    """Deletes a flash deck"""
    self.deckname = deckname
    drop_deck_query = ("""DROP TABLE %s""")
    cur = cnx.cursor()
    flash_table="flash_"+self.deckname
    cur.execute(drop_deck_query % flash_table)
    print self.deckname+ " deck is deleted successfully\n"
    
    
  def flash_add_card(self,deckname,front_entry,back_entry,sentence,flash_note):
    """Adds a new card to the deck"""
    self.deckname = "flash_"+deckname
    self.front_entry = front_entry
    self.back_entry = back_entry
    self.sentence = sentence
    self.flash_note = flash_note
    cur = cnx.cursor()
    self.timestamp = int(time.time())     

    #Table name can't be added as a tuple!!!
    add_card_query = ("INSERT INTO "+self.deckname+ 
                      "(id,front_entry,back_entry,sentence,flash_note,insert_date) "
                      "VALUES ('',%s,%s,%s,%s,%s)")

    card_data = (self.front_entry,self.back_entry,self.sentence,self.flash_note,self.timestamp)
    cur.execute(add_card_query,card_data)
    cnx.commit() #we have to commit
    cur.close()
    print self.colorize("Card is added to the deck "+self.colorize(self.deckname[6:],"red"),"cyan")
    
  def flash_del_card(self,deckname,front_entry):
    """Deletes a flash card entry from the specified deck"""
    self.deckname = "flash_"+deckname
    self.front_entry = front_entry
    cur = cnx.cursor()
    del_card_query = ("DELETE from "+self.deckname+" where front_entry=%s")
    card_data = (self.front_entry,)
    cur.execute(del_card_query,card_data)
    cnx.commit()
    cur.close()
    print self.colorize(self.front_entry,"red") + " is deleted from deck "+self.colorize(self.deckname[6:],"green")     

  def flash_get_card(self,deckname,fetchoption):
    """Fetchs a card which has been least number of displayed based on the num_of_display column"""
    """This logic doesn't work well if you display words e.g 1K times and later add a new word, then old words will almost never show up"""
    """add also the last display to the account"""

    self.deckname = "flash_"+deckname
    self.fetchoption = fetchoption
    cur = cnx.cursor()
    if self.fetchoption == "get":
      get_card_query = ("SELECT front_entry,back_entry,sentence,num_of_display from "+self.deckname+" order by num_of_display limit 1") #default sort is ascending   
    elif self.fetchoption == "one":
      get_card_query = ("SELECT front_entry,back_entry,sentence,num_of_display from "+self.deckname+" order by RAND() limit 1")

    cur.execute(get_card_query)
    headers = ["Front","Back","Sentence","Display counter"]
    card =  [ [row[0],row[1],row[2],row[3] ]  for row in cur ] 
    #we take the result set and create a list of list e.g [[front,end,counter]] so element itself is a list too.It is a must
    current_counter = card[0][3]
    sentence = card[0][2]
    front_entry = card[0][0]
    new_counter = current_counter + 1
    cur.close()

    #we get the card entry, increase num_of_display
    cur = cnx.cursor() 
    update_card_counter = ("UPDATE "+self.deckname+" set num_of_display=%s where front_entry=%s")
    card_update_data = (new_counter,front_entry)
    cur.execute(update_card_counter,card_update_data)
    cnx.commit() 
    print tabulate(card,headers,tablefmt="grid")
    

  def flash_show_card(self,deckname,front_entry):
    """displays a flash card when the front side is provided"""
    
    self.deckname = "flash_"+deckname
    self.front_entry = front_entry
    cur = cnx.cursor()
    show_card_query = ("SELECT front_entry,back_entry,sentence,flash_note,num_of_display from "+self.deckname+" where front_entry=%s")
    cur.execute(show_card_query,(self.front_entry,))
    count = cur.rowcount
    if count >0:
      card = [ [row[0],row[1],row[2],row[3],row[4] ] for row in cur ]
      headers = ["Front","Back","Sentence","Notes","# of display"]
      print tabulate(card,headers,tablefmt="grid")
    else:
      print "There is no such record\n"
      

  #####<END> FLASH APP#####



  ####<BEGIN> RTOO APP####
  def rtoo_add(self,app_type,rtoo_pri,rtoo_sec,rtoo_tags,rtoo_other):
    """Adding records from command reference, bookmark, contacts and reminder applications"""
    self.app_type = app_type
    self.rtoo_pri = rtoo_pri
    self.rtoo_sec = rtoo_sec
    self.rtoo_tags = rtoo_tags
    self.rtoo_other = rtoo_other
   
    #It shouldn't cause much trouble to check if the relavent app table exists or not and create it on the fly, or it can?
    #first check if the table for this module is created or not, we can reuse the flash_deck_avail func.
    if self.flash_deck_avail(self.app_type) == 0:
      cur = cnx.cursor()
      #Create the table
      new_rtoo_query = (
          """CREATE TABLE %s (id INT NOT NULL AUTO_INCREMENT,
           rtoo_pri text NOT NULL,
           rtoo_sec text,
           rtoo_tags varchar(255),
           rtoo_other text,
           rtoo_datetime int,
           PRIMARY KEY (id)
          )"""
        )
      cur.execute(new_rtoo_query % self.app_type)
      cur.close()
      #table must have been created here

    
    #Now we add the entry
    cur = cnx.cursor()
    rtoo_add_query = ( 
        """INSERT INTO """+self.app_type+""" (id,rtoo_pri,rtoo_sec,rtoo_tags,rtoo_other) 
           VALUES ('',%s,%s,%s,%s)""")
    cur.execute(rtoo_add_query,(self.rtoo_pri,self.rtoo_sec,self.rtoo_tags,self.rtoo_other))
    cnx.commit()
    cur.close()
    print self.HEADER+self.app_type+self.ENDC+" entry is added\n" 

  def rtoo_add_note(self,app_type,rtoo_note,rtoo_tags,rtoo_reminder,rtoo_email):
    """This is an app to take quick notes and if enabled send a reminder email about the note"""
    #Table structure is different than other apps, hence couldn't reuse rtoo function

    self.app_type = app_type
    self.rtoo_note = rtoo_note
    self.rtoo_tags = rtoo_tags
    self.rtoo_reminder = rtoo_reminder
    self.rtoo_email = rtoo_email

    cur = cnx.cursor()
    if self.flash_deck_avail(self.app_type) == 0:
      #Create the table
      new_rtoo_query = (
          """CREATE TABLE %s (id INT NOT NULL AUTO_INCREMENT,
             rtoo_note text NOT NULL,
             rtoo_datetime datetime,
             rtoo_tags varchar(255),
             rtoo_reminder datetime,
             rtoo_email varchar(255),
             PRIMARY KEY (id)
            )"""
          )
      cur.execute(new_rtoo_query % self.app_type)
      #table must have been created here
 

    rtoo_datetime=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    rtoo_add_query = (
        """INSERT INTO """+self.app_type+""" (id,rtoo_note,rtoo_datetime,rtoo_tags,rtoo_reminder,rtoo_email) 
           VALUES ('',%s,%s,%s,%s,%s)""")
    cur.execute(rtoo_add_query,(self.rtoo_note,rtoo_datetime,self.rtoo_tags,self.rtoo_reminder,self.rtoo_email))
    cnx.commit()
    cur.close()
    print self.HEADER+self.app_type+self.ENDC+" entry is added\n"

  def rtoo_search(self,app_type,search_string,search_field):
    """By default we search on every field for the given string"""
    self.app_type = app_type
    self.search_string = search_string
    self.search_field = search_field


    #we need to convert app specific data(each app has its speficif column names) to rtoo module structure
    ##APPSPECIFIC conditions
    if self.app_type=='faq':
        headers = ["#","Question","Answer","Tags","Other"]
        search_field_dict = {'question':'rtoo_pri','answer':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='cref':
        headers = ["#","Command","Description","Tags","Other"]   
        search_field_dict = {'command':'rtoo_pri','desc':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='bookmark': 
        headers = ["URL","Description","Tags","Other"]
        search_field_dict = {'url':'rtoo_pri','desc':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='contact': 
        headers = ["Name","Details","Tags","Other"]
        search_field_dict = {'name':'rtoo_pri','details':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}

 
    cur = cnx.cursor()
    #we can't use FULLTEXT search as it only works on MyISAM
    if search_field=="empty":    
      rtoo_search_query = ("SELECT rtoo_pri,rtoo_sec,rtoo_tags,rtoo_other,id from "+self.app_type+" WHERE rtoo_pri LIKE '%s' OR rtoo_sec LIKE '%s' OR rtoo_tags LIKE '%s' OR rtoo_other LIKE '%s'")
      rtoo_search_data = ("%"+self.search_string+"%",)*3 + ("%"+self.search_string+"%",)  #the last comma is required to make it tuple for concatenation
    else:
      rtoo_search_query = ("SELECT rtoo_pri,rtoo_sec,rtoo_tags,rtoo_other,id from "+self.app_type+" WHERE %s LIKE '%s'")  
      rtoo_search_data = (search_field_dict[self.search_field],"%"+self.search_string+"%")

    

    cur.execute(rtoo_search_query % rtoo_search_data)
    #feedback: for some reason, "," instead of % didn't work if argument is sent to LIKE in mysql query.
    if cur.rowcount==0:
      print self.WARNING+"No entry found!!!\n"+self.ENDC
      cur.close()
    else:
      result = [ [ column[4],column[0],column[1],column[2],column[3] ] for column in cur ]
      print tabulate(result,headers,tablefmt="grid")
         
  def rtoo_note_search(self,app_type,search_string,search_field):
    """By default we search on every field for the given string"""
    self.app_type = app_type
    self.search_string = search_string
    self.search_field = search_field

    headers = ["#","note","Tags","Date of entry","Reminder","email"]
    search_field_dict = {'note':'rtoo_note','tags':'rtoo_tags','date':'rtoo_datetime','reminder':'rtoo_reminder','email':'rtoo_email'} 

    cur = cnx.cursor()
    if search_field=="empty":
      rtoo_search_query = ("SELECT id,rtoo_note,rtoo_tags,rtoo_datetime,rtoo_reminder,rtoo_email FROM "+self.app_type+" WHERE rtoo_note LIKE '%s' OR rtoo_datetime LIKE '%s' OR rtoo_tags LIKE '%s' OR rtoo_reminder LIKE '%s' OR rtoo_email LIKE '%s'")
      rtoo_search_data = ("%"+self.search_string+"%",)*4 + ("%"+self.search_string+"%",)
    else:
      rtoo_search_query = ("SELECT id,rtoo_note,rtoo_tags,rtoo_datetime,rtoo_reminder,rtoo_email FROM "+self.app_type+" WHERE %s LIKE '%s'")
      rtoo_search_data = (search_field_dict[self.search_field],"%"+self.search_string+"%")



    cur.execute(rtoo_search_query % rtoo_search_data)
    #feedback: for some reason, "," instead of % didn't work if argument is sent to LIKE in mysql query.
    if cur.rowcount==0:
      print self.WARNING+"No entry found!!!\n"+self.ENDC
      cur.close()
    else:
      result = [ [ col[0],col[1],col[2],col[3],col[4],col[5] ] for col in cur ]
      print tabulate(result,headers,tablefmt="grid")


  def rtoo_del(self,app_type,entry_id):
    """Deletes the entry from the respective app, only accepts ID"""
    self.entry_id = entry_id
    self.app_type = app_type
   
    #Check if a valid integer id is given 
    try:
      int(self.entry_id)
    except ValueError:
      print "Invalid entry ID!!!"
      sys.exit()

    cur = cnx.cursor()
    rtoo_del_query = ("DELETE from "+self.app_type+" where id=%s")
    rtoo_del_data = (self.entry_id,)
    cur.execute(rtoo_del_query,rtoo_del_data)
    cnx.commit()

    print "Entry ID "+self.OKGREEN+self.entry_id+self.ENDC+" is deleted" 


  def rtoo_update(self,app_type,entry_id,field,field_value):
    """Updates the fields"""
    self.app_type = app_type
    self.entry_id = entry_id
    self.field_value = field_value
    

    #we need to convert app specific data(each app has its speficif column names) to rtoo module structure
    ##APPSPECIFIC conditions
    if self.app_type=='faq':
        headers = ["#","Question","Answer","Tags","Other"]
        search_field_dict = {'question':'rtoo_pri','answer':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='cref':
        headers = ["#","Command","Description","Tags","Other"]
        search_field_dict = {'command':'rtoo_pri','desc':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='bookmark':
        headers = ["URL","Description","Tags","Other"]
        search_field_dict = {'url':'rtoo_pri','desc':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    if self.app_type=='contact':
        headers = ["Name","Details","Tags","Other"]
        search_field_dict = {'name':'rtoo_pri','details':'rtoo_sec','tags':'rtoo_tags','other':'rtoo_other'}
    
    #Get the real field name
    self.field = search_field_dict[field]
 
    cur = cnx.cursor()
    rtoo_search_query = ("SELECT id,rtoo_pri,rtoo_sec,rtoo_tags,rtoo_other FROM "+self.app_type+" WHERE id=%s")
    rtoo_search_data = (self.entry_id,)
    cur.execute(rtoo_search_query,rtoo_search_data)
    if cur.rowcount==1:
      #cur.close()
      #cur = cnx.cursor()
      rtoo_update_query = ("UPDATE "+self.app_type+" set "+self.field+"=%s where id=%s")
      rtoo_update_data = (self.field_value,self.entry_id)
      cur.execute(rtoo_update_query,rtoo_update_data)
      cnx.commit()
      print "Entry id "+self.entry_id+" is updated"
          
      


  def rtoo(self,args,app_type):
    """Primary rtoo function which calls associated rtoo functions"""
    name_help_function="self.help_"+app_type
    if not args:
      eval(name_help_function)() #we need to call the function based on the input
      sys.exit()
    arg = shlex.split(args)
    arg_count = len(arg)
    if arg[0]=="add" or re.search(r'^a',arg[0]):
      if arg_count==4:
        #other field is missing
        self.rtoo_add(app_type,arg[1],arg[2],arg[3],None)
      if arg_count==5:
        self.rtoo_add(app_type,arg[1],arg[2],arg[3],arg[4])
      if arg_count<4:
        print self.WARNING+"Missing paramater!!!"+self.ENDC
        
    elif arg[0]=="search" or re.search(r'^s',arg[0]):
      if arg_count<2:
        name_help_function="self.help_"+app_type
        eval(name_help_function)() 
      if arg_count==2:
        search_field="empty"
        #no search field is provided , max index 1
        self.rtoo_search(app_type,arg[1],search_field)
      if arg_count==3:
        #we know the search field now
        self.rtoo_search(app_type,arg[1],arg[2])
    elif arg[0]=="del" or re.search(r'^d',arg[0]):
      if arg_count<2:
        name_help_function="self.help_"+app_type
        eval(name_help_function)()
      else:
        self.rtoo_del(app_type,arg[1])
    elif ( (arg[0]=="update" or re.search(r'^u',arg[0])) and arg_count==4 ):
      self.rtoo_update(app_type,arg[1],arg[2],arg[3])

    else:
      eval(name_help_function)()
      sys.exit()


  def rtoo_note(self,args,app_type):
    """note main module"""
    if not args:
      name_help_function="self.help_"+app_type
      eval(name_help_function)() #we need to call the function based on the input
      sys.exit()
    arg = shlex.split(args)

    if arg[0]=="add" or re.search(r'^a',arg[0]):
      if len(arg)==3:
        #no reminder
        self.rtoo_add_note(app_type,arg[1],arg[2],None,None)
      if len(arg)==5:
        #we have reminder
        self.rtoo_add_note(app_type,arg[1],arg[2],arg[3],arg[4])
      if len(arg)==4 or len(arg)<3:
        print self.WARNING+"Missing paramater!!!"+self.ENDC
        self.help_note()

    if arg[0]=="del" or re.search(r'^d',arg[0]):
     if len(arg)<2:
       name_help_function="self.help_"+app_type
       eval(name_help_function)()
     else:
       self.rtoo_del(app_type,arg[1])

   
    if arg[0]=="search" or re.search(r'^s',arg[0]):
     if len(arg)<2:
       name_help_function="self.help_"+app_type
       eval(name_help_function)()
     if len(arg)==2:
       search_field="empty"
       #no search field is provided , max index 1
       self.rtoo_note_search(app_type,arg[1],search_field)
     if len(arg)==3:
       #we know the search field now
       self.rtoo_note_search(app_type,arg[1],arg[2])
 

  def do_faq(self,args):
    app_type = 'faq'
    self.rtoo(args,app_type)
 
  def do_cref(self,args):
    app_type ='cref'
    self.rtoo(args,app_type)
  def do_contact(self,args):
    app_type = 'contact'
    self.rtoo(args,app_type)
  def do_bookmark(self,args):
    app_type = 'bookmark'
    self.rtoo(args,app_type)
  def do_note(self,args):
    app_type = 'note'
    self.rtoo_note(args,app_type)

  ####<END> RTOO APP####


  ####<BEGIN> NETWORKING APP###
  
  def do_ip(self,args):
    arg = shlex.split(args)
    parser = argparse.ArgumentParser(description='Multi purpose IP tool',prog="ip")
    subparsers = parser.add_subparsers(help='Available commands')

    #Convert
    convert_parser=subparsers.add_parser('convert',help='convert to ip formats')
    convert_parser.add_argument('toint {ipaddr}',action='store',help='interger conversion')



    args = parser.parse_args(arg)
    
    


##INSTANCE 
cli = Cli()
cli.cmdloop()
