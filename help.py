class color:
 #colorize the outputs
 #to call from the child class use self.HEADER, self.OKBLUE etc directly
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


class helpd:

  def help_flash(self):
    print color.HEADER+"Syntax: flash {newdeck|listdecks|removedeck|add|del|get|one|show|training}"+color.ENDC
    print """Usage:"""
    print color.OKGREEN+"       ##DECK management##"+color.ENDC
    print """
       >flash newdeck <deckname>
       >flash listdecks
       >flash removedeck <deckname>

       - newdeck: creates a new deck to store flash cards
       - listdecks: list available decks
       - removedeck: deletes the deck specified
          """
    print color.OKGREEN+"       ##Card management##"+color.ENDC
    print """
       >flash add <deckname> <front_entry> <back_entry> [sentence] [flash note]
       >flash del <deckname> <front_entry>
       >flash get <deckname>
       >flash show <deckname> <front_entry> 
       >flash training <deckname> <number of cards> [interval(sec)]

       - add: adds a card to the deck
       - del: deletes a card from the deck
       - get: brings least displayed flash card
       - one: displays a random card from the deck
       - show: shows the contents of the card
       - training: displays words randomly at every 5 seconds by default indefinitely. If number of cards are provided, script stops after # of cards
     
    """

  def help_cref(self):
    """Command reference module to easily add/fetch cli commands"""
    print color.HEADER+"Syntax: cref {add|del|search}"+color.ENDC
    print """Usage:

           >cref add <command> <description> <tags> [other]
           >cref search <search string> [command|desc|tags|other]  #By default we search in all fields if field option isn't provided
           >cref del <entry ID>
           >cref update <entry id> <command|desc|tags|other> <new value>
 
          """
  def help_bookmark(self):
    """Bookmark application which we can use to save our URLs"""
    print color.HEADER+"Syntax: bookmark {add|del|search}"+color.ENDC
    print """Usage:

           >bookmark add <URL> <description> <tags> [other]
           >bookmark search <search string> [url|desc|tags|other]  #By default we search in all fields if field option isn't provided
           >bookmark del <entry ID>
           >bookmark update <entry id> <url|desc|tags|other> <new value>
          """

  def help_contact(self):
    """Contacts application which we can use to save our contacts"""
    print color.HEADER+"Syntax: contact {add|del|search}"+color.ENDC
    print """Usage:

           >contact add <name> <contact details> <tags> [other]
           >contact search <search string> [name|details|tags|other]  #By default we search in all fields if field option isn't provided
           >contact del <entry ID>
           >contact update <entry id> <name|details|tags|other> <new value>
          """

  def help_note(self):
    """Note and reminder app"""
    print color.HEADER+"Syntax: note {add|del|search}"+color.ENDC
    print """Usage:

           >note add <note> <tags> [reminder date] [email] #reminder date and email optional
           >note search <search string> [name|details|tags|other]  #By default we search in all fields if field option isn't provided
           >note del <entry ID>
          
           Example: 
           >note add "latest electricity counter 3455" "gas" 
           >note add "remember to clean your room" "room" "2015-10-12 14:00:00" "genco@example.com" <<<---reminder isn't implemented yet!!!

          """
 
 
  def help_faq(self):
    """Adds faq in any category. Command has an option to specify category"""
    
    print color.HEADER+"Syntax: faq {add|del|search}"+color.ENDC
    print """Usage:

           >faq add <question> <answer> <tags> [other]
           >faq search <search string> [question|answer|tags|other]  #By default we search in all fields if field option isn't provided
           >faq del <entry ID>
           >faq update <entry id> <question|answer|tags|other> <new value>
 
          """


  def help_quit(self):
    print "syntax: quit"

