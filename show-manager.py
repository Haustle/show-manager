import os
import searchtools, time
from authentication import authentication
from logger import Logger


# the root folder
projectFolder = (os.getcwd()+"/")
logger = Logger()


# Authenticates and makes sure all files are in the current directory
s = authentication(projectFolder)
missingMainfiles = s.mainFiles()
if missingMainfiles != None: print missingMainfiles #prints if there is a missing file

time.sleep(1)
# s.showFiles(isShow=True)
print 'show-manager by Tyrus Miles'

s = searchtools.searchtools(projectFolder)
while True:
    

    command = (raw_input("\n\nEnter command (type help): ").lower()).split(" ")
    # try:
    if command[0] == '':
        break
    elif (command[0] == 'b') or (command[0] == 'bookmarks'):
        print ''
        print 'BOOKMARKS'
        print '-'*10
        for x in range(len(bookmarklist)):
            print '(%d) %s' %(x+1, bookmarklist[x])
            x+=1

        showAbove = raw_input("\nIs the show you are looking for above: ").lower()
        if showAbove == 'yes':
            whatNum = raw_input("Please enter the integer the show is at: ")
            if whatNum.isdigit() == True:
                whatNum = int(whatNum)-1
                if whatNum <= len(bookmarklist):
                    foundshow = bookmarklist[whatNum]
                    showOptions(foundshow,showfoldpath, showList, bookmarklist)
                else:
                    print '\nThe inputed integer is out of index (length of list: %d)' %(len(bookmarklist))
            else:
                print '\nThe user input is not a digit.'
        wantContinue = raw_input('\nDo you want to continue running the program?')
        if wantContinue.lower() == 'yes':
            continue
        else:
            '\nThanks for using the program!'


    elif (command[0] == 's') or (command[0] == 'search'):

        filepath =""
        if len(command) > 1:
            if command[1] == '-s' or command[1] == '-m':
                # This for commands that have the length required for a command search
                
                if len(command) > 2:
                    reassignName = ""
                    if command[1] == "-s":

                        askShow = " ".join(command[2:])
                        searchtools.searchtools.isShow = True
                        s.showSearch(show=askShow)

                    else:
                        askMovie = " ".join(command[2:])
                        searchtools.searchtools.isShow = False
                        s.showSearch(show=askMovie)



                elif len(command) == 2:

                    if command[1] == '-s':
                        askShow = raw_input("What show do you want to search for: ")
                        searchtools.isShow = True
                        s.showSearch(show=askShow)
                        

                    elif command[1] == '-m':
                        
                        askMovie = raw_input("What movie do you want to search for: ")
                        searchtools.isShow = False
                        s.showSearch(show=askMovie)
                        
                    else:
                        print 'This is not an option'

            else:
                print 'Error: The second variable in that command \'%s\' was not recognized' %(command[1])
            

        medialist = sorted(s.getMediaList())
        filepath = s.getTextFile()
        open(filepath,'w').close()
        for file in medialist:
            logger.writeLog(filepath,message=file+"\n")


    elif (command[0] == 'a') or (command[0] == 'add'):
        print 'Make sure the links you send are to public profiles (private profiles don\'t work)'
        print 'The supported websites you can import are listed below'
        print '-'*10
        print '\n'

        providerLink = raw_input("Enter the link to the list here: ").lower()
        websiteListScraper(providerLink)

    elif (command[0] == 'help') or (command[0] == 'h'):
        print 'This is for help'
    else:
        print 'The initial command is not correct'
    # except ValueError:
    #     print '\n\'%s\' The inputed command does not work.'

print '#'*10 + " THE END " + '#'*10
print '\nBonsoir Elliot!'
