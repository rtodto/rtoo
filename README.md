A commond line tool which has several utilities e.g

- Commmand reference tool
- notepad tool
- flash card tool


Type help to list all commands
Available commands: flash|faq|bookmark|contact|cref|note

rtoo> bookmark
Syntax: bookmark {add|del|search}
Usage:

           >bookmark add <URL> <description> <tags> [other]
           >bookmark search <search string> [url|desc|tags|other]  #By default we search in all fields if field option isn't provided
           >bookmark del <entry ID>
           >bookmark update <entry id> <url|desc|tags|other> <new value>

rtoo> cref
Syntax: cref {add|del|search}
Usage:

           >cref add <command> <description> <tags> [other]
           >cref search <search string> [command|desc|tags|other]  #By default we search in all fields if field option isn't provided
           >cref del <entry ID>
           >cref update <entry id> <command|desc|tags|other> <new value>


