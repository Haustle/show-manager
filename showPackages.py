import re, os, subprocess
import time


#MAKING A FUNCTION (THAT TAKES IN THE NEW SHOW). EVERYTIME A FOLDER IS ADDED RE-RUN THE LOOP THAT PRINTS THE FOLDER NAMES INTO A TEXT FILE
#INSTEAD OF TYPING THE NAME OF THE SHOW INTO THE TEXT FILE AND ADDING THE FOLDER
#CLOSES THE GAP OF ERROR IF ITS ONLY BASED OFF THE FOLDERS PRESENT


def grammarCheck(showName):
    titleshit = re.findall(r'vs|the|and|of|at|by|down|for|from|in|into|like|near|off|on|into|to|with|till|when|yet|or|so|a', showName)
    # print titleshit
    splitShow = showName.split(" ")
    i = 0
    if titleshit > 0:
        for item in splitShow:
            wordIndex = splitShow.index(item.lower())
            if item not in titleshit:
                item = item.title()

                splitShow[wordIndex] = item
                # This checks to see if there are any 's in the word
                if "\'" in splitShow[wordIndex]:
                    # I need to figure out the length of the string so I can make everything after the ' lower case
                    # I can than make a loop minusing 1 for the placemnet to lowercase the letter and joining them back together.
                    wordlist = list(item)
                    something = wordlist.index("\'")
                    for letter in wordlist[something:]:
                        letNum = wordlist.index(letter)
                        wordlist[letNum] = wordlist[letNum].lower()
                        # print wordlist[letNum]
                    item = ''.join(wordlist)
                    splitShow[wordIndex] = item





            # Checks to see if the first word includes any of the titleshit words. if they do they are capitalized
            elif (item in titleshit and splitShow[0].lower()) and i == 0:

                wordIndex = splitShow.index(item)
                splitShow[wordIndex] = splitShow[wordIndex].title()



            i+=1

        showName = " ".join(splitShow)

    else:
        showName = showName.title()

    return showName

#This function should be run at the very bottom of the py_programs

def folderBalance(folderpath, showTxtFile, appendShowList,bookmarklist):
    import os

    for show in appendShowList:

        newShowLoc = folderpath + show
        if os.path.isdir(newShowLoc) == True:
            print '\'%s\' already exists' %(show)
            continue
        else:
            os.mkdir(newShowLoc)
            showpath = "%s/%s log.txt" %(newShowLoc,show)
            f = open(showpath,"w+")
            f.close()


    showsFolderList = os.listdir(folderpath)
    file = open(showTxtFile,"w")
    showsFolderList = sorted(showsFolderList)
    [file.write(show+"\n") for show in showsFolderList] 
    file.close()

    bookmarkfile = sorted(open((folderpath+"[BOOKMARKED SHOWS].txt"),"w"))
    [bookmarkfile.write(show + "\n") for show in bookmarklist]
    bookmarkfile.close()

def showOptions(show, folderpath, showlist, bookmarklist):

    import os, webbrowser, shutil
    print '\n'*4
    print show
    print '-'*10
    print ''
    print 'a. Print show directory details'
    print 'b. Open the folder of the show'
    print 'c. Check for missing Episodes'
    print 'd. Bookmark this show'
    print 'e. Delete the show'

    whatNext = raw_input("\nChoose one of the above options: ")

    if whatNext.lower() == 'a':
        print 'Show Details : \'%s\'' %(show)
        filesInPath = sorted(os.listdir(folderpath+show))
        # print filesInPath
        seasonCount = []
        for file in filesInPath:
            if file.startswith("Season "):
                # print file
                seasonCount.append(file)
        print ''
        if len(seasonCount) > 0:
            for season in seasonCount:
                lenForSeason = len(os.listdir(folderpath+show+'/'+season))
                # numOfEpisodes+= lenForSeason

                print '%s: %d Episodes' %(season, lenForSeason)
        else:
            print 'No seasons were found'


    elif whatNext.lower() == 'b':
        print ('Opening {} \'folder\'...'.format(show))       
        subprocess.call(["open","-R", folderpath+show+"/"])
        print folderpath+show+"/"
        print 'We opened \'%s\'' % (show)

    elif whatNext.lower() == 'c':

        # Checking for new seasons and episodes
        # Upon running this command tell the user how many episodes they are missing
        # Then ask them if they'd like to add episodes to to a specific season or all
        # Check if the season they want to add already has episodes
        # Allow the user to enter '1-15 and 2-34' so they can download in groups (maybe limit them to 25 at a time)

        print 'SHOW UPDATE'
        print ''
        print 'a. Check if you have all seasons'
        print ''
        seasonUpdate = raw_input("Do you want to see if you have the latest season").lower()
        if seaosnUpdate == 'yes':
            if currentSeas < newSeasons:
                print 'You are missing season(s) %d ' %(newSeasons - currentSeas)
            else:
                print 'Don\'t worry you have all current seasons.'

    elif whatNext.lower() == 'd':

        # Read the file into a list
        # If statement to check to see if the show is bookmarked already

        if show in bookmarklist:
            print '\nThis show is already bookmarked'
        else:
            bookmarklist.append(show)
            print '\nThis show is now BOOKMARKED'

    elif whatNext.lower() == 'e':
        if show in bookmarklist:
            print '\nIt\'s here'
            bookmarklist.remove(bookmarklist[bookmarklist.index(show)])
            print bookmarklist
        print '\nDeleting \'%s\'...' %(show)
        shutil.rmtree(folderpath+show)
        showlist.remove(showlist[showlist.index(show)])

        currentTime = time.strftime("%c")
        log = "/Users/ty/Desktop/fsociety/py_programs/showBot/log.txt"
        logString = "%s \t[DELETED] %s \n" % (currentTime, show)

        l = open(log,"r")
        lastline = l.readlines()
        l.close()
        lastline = lastline[len(lastline)-1]
        lastLog = lastline.split(" ")
        if len(lastLog)>0:
            # print lastLog
            for part in lastLog:
                # Because  [NEW SHOW] is split in half we're only checking for the first part
                if part == '\t[NEW':
                    logString = "\n"+logString
                    break

        l = open(log,'a')
        l.write(logString)
        l.close()
        print '[-]This show has been deleted'



    else:
        print 'The previous input was invalid.'


def likeToAdd(newshowlist, show):

    addShow = raw_input("We couldn\'t find \'%s\' in our database'. Would you like to add it?: " % show)
    if addShow.lower() == 'yes':
        foundshow = onlyShow(show)
        foundshow = foundshow.encode('utf-8')
        #ADD an option for them to match to the first show found on moviedb, but only show
        #if the two options don't match the show found.
        range = 2
        print '\n[1] Keep the original name:\t\'%s\'' %(show)
        print '[2] Get a title case name:\t\'%s\'' %(grammarCheck(show))

        if foundshow != show and grammarCheck(show):
            range = 3
            print '[3] MovieDB name match:\t\t\'%s\'' %(foundshow)

        titleChoice = int(raw_input("\nChoose one of the above options: "))
        if titleChoice == 1:
            newshowlist.append(show)
        elif titleChoice == 2:
            newshowlist.append(grammarCheck(show))
        elif titleChoice == 3 and range == 3:
            newshowlist.append(foundshow)
        else:
            print 'That is not an option'

def onlyShow(show):
    import tmdbsimple as tmdb
    api = '7e022dc2338ac2988670ddb93ccff401'
    tmdb.API_KEY = '7e022dc2338ac2988670ddb93ccff401'
    search = tmdb.Search()
    reponse = search.tv(query=show)
    if len(search.results) > 0:
        something = search.results[0]
        name = something['name']
        return name



def additionalShowInfo(list):
    # print list
    import urllib
    import os
    import tmdbsimple as tmdb
    import requests

    showfoldpath = "/Users/ty/Desktop/fsociety/py_programs/showBot/shows/"
    textFilePath = "/Users/ty/Desktop/fsociety/py_programs/showBot/show_list.txt"

    with open(textFilePath,'r') as f:
        showList = [line.strip() for line in f]

    sortedList = showList.sort()

    api = '7e022dc2338ac2988670ddb93ccff401'
    tmdb.API_KEY = '7e022dc2338ac2988670ddb93ccff401'
    search = tmdb.Search()
    count = 1
    for show in list:
        # print 'Show : %s' %(show)
        nameshow = show

        response = search.tv(query=nameshow)


        # Naruto 26260
        #This code came from the official github page
        # print search.results[genre_ids]

        posterBase = 'https://image.tmdb.org/t/p/w500'
        if len(search.results) > 0:
            something = search.results[0]
            showpath = showfoldpath+show+"/"
            # print something
            # poster = search.results[0].poster_path
            # overview = (something['overview'])


            # PRINTS OUT THE OVERVIEW OF THE SHOW INTO A TEXT FILE

            overview = something['overview']
            overviewtext = showfoldpath+nameshow+"/"+"overview.txt"
            f = open(overviewtext,'w',)
            f.write(overview.encode('utf8'))
            f.close()




            id = (something['id'])
            poster = (something['poster_path'])
            if poster is None:
                print '%s contained None' %(show)
                count+=1
                continue

            posterLink = posterBase + poster
            # print s['name']
            # webbrowser.open(posterLink)

            if os.path.isdir(showpath) == True:
                if os.path.exists(showpath+"cover.jpg") == True:

                    print '%d %s has a picture already' %(count,show)

                else:
                    urllib.urlretrieve(posterLink,(showpath+"cover.jpg"))

                    url = "https://api.themoviedb.org/3/tv/%d?api_key=%s&language=en-US" % (id,api)
                    payload = "{}"
                    json_data = requests.get(url).json()
                    seasonnum = json_data['number_of_seasons']
                    y = 0
                    while(y<seasonnum):
                        newSeason = "Season %d" %(y+1)
                        os.mkdir(showpath+newSeason)
                        y+=1

                    print '[+]%d %s retreived' %(count, show)
                    currentTime = time.strftime("%c")
                    log = "/Users/ty/Desktop/fsociety/py_programs/showBot/log.txt"
                    logString = "%s \t[NEW SHOW] %s (%d seasons)\n" % (currentTime, show, seasonnum)
                    l = open(log,"r")
                    lastline = l.readlines()
                    l.close()
                    lastline = lastline[len(lastline)-1]
                    lastLog = lastline.split(" ")
                    if len(lastLog)>0:
                        # print lastLog
                        for part in lastLog:
                            if part == '\t[DELETED]':
                                logString = "\n"+logString
                                break



                    l = open(log,'a')
                    l.write(logString)
                    l.close()
            else:
                print '%s path doesn\'t exist' %(show)


        else:
            print '%s was not found.' %(show)
        count+=1

def websiteListScraper(providerLink):
    from bs4 import BeautifulSoup
    import requests, re
    importListProvider = ['MyAnimeList.net','Anilist.co','Netflix.com','IMDB.com']
    # providerLink = "https://myanimelist.net/animelist/haustle".lower()

    showlist = []
    for provider in importListProvider:

        for y in range(len(providerLink)-len(provider)):
            if providerLink[y:y+len(provider)] == provider.lower():

                if provider == 'MyAnimeList.net':

                    # Added a way to sort the shows that are finished and those that are
                    # currently still being watched
                    # url = 'myanimelist.net/animelist/haustle'

                    profile_name = re.search('myanimelist.net/animelist/(.{0,100})',providerLink)
                    if len(profile_name.groups()) > 0:
                        providerLink = 'http://www.'+ profile_name.group(0)
                        resp = requests.get(providerLink)
                        page_code = resp.status_code
                        if page_code == 404:
                            print 'Error 404: The page could not be found'
                        elif page_code == 429:
                            print 'Error 429: There are too many requests on MyAnimeList right now. Try again in a couple minute(s)'
                        elif page_code == 200:
                            try:
                                username = profile_name.group(1)
                                soup = (resp.text, 'html.parser')
                                for x in range(len(soup)-1):
                                    code = str(soup[x])
                                    profileShowFormula = re.findall(r'anime_title&quot;:&quot;(.{0,100})&quot;,&quot;anime_num_episodes',code)
                                    foundAnimeList = False
                                    counter = 0
                                    while (foundAnimeList == False) and (counter < 10):
                                        if len(profileShowFormula) > 0:
                                            foundAnimeList = True
                                            print 'The anime list for \'%s\' (%d shows)' %(username,len(profileShowFormula))
                                            print '-'*20
                                            print ' '
                                            for show in profileShowFormula:
                                                showlist.append(show)
                                                # print show
                                            # print '\nThe page code(s) is: %d' %(page_code)
                                        else:
                                            print counter
                                            counter +=1

                            except:
                                # This can determine if the page is 404 and not found in the database
                                # print resp.status_code
                                print 'Error %d: No list could be found' % (resp.status_code)



                    else:
                        print 'Error: The link provided is not in the correct format'
                        print 'ex. myanimelist.net/animelist/[insert username]'


                # For links that are anilist.co
                elif provider == 'Anilist.co':

                    # Everything listed for the myanimelist but for this site

                    print 'anilist.co will be worked on soon'
                # For links that are netflix.com
                elif provider == 'Netflix.com':

                    # Need to find a way to tell the user how to get the list of shows
                    # They have on their list
                    print 'Netflix.com Not sure what to do here'
                # For links that are IMDB.com
                elif provider == 'IMDB.com':
                    #Simply copy the list that someone has made on IMDB and put it in the program.
                    print 'IMDB.com This shouldn\'t be too bad'

                else:
                    print 'hello, this should never get printed'
    print '\nThe page code(s) is: %d' %(page_code)
    for show in showlist:
        print show



def similarStrings(name,shows,rankinglist, otherlist):
    savedParts = []
    for x in range(len(name)):
        partOfname = name[x:x+2]
        savedParts.append(partOfname)

    rankings = []
    counter = 1
   
    if len(shows) > 0:
        try:
            savedParts = []
            for x in range(len(name)):
                partOfname = name[x:x+2]
                savedParts.append(partOfname)

            rankings = []
            # Counter counts how many different pairs of strings they have in common
            counter = 1
            for show in shows:
                counter = 1
                showParts = []
                for x in range(len(show)):
                    partOfname = show[x:x+2]
                    showParts.append(partOfname)

                notrange = []
                for x in range(len(savedParts)):
                    for y in range(len(showParts)):
                        if savedParts[x].lower() == showParts[y].lower() and (y not in notrange):
                            notrange.append(y)
                            # print show +" " + savedParts[x] + " " + showParts[y]
                            counter +=1
                            break

                if counter > 1:
                    counter = float(counter - 1)
                    points = (counter)/(float(len(savedParts)+len(showParts)-counter))
                    # print 'show: %s\tpoints: %0.2f fraction: %d/%d' %(show,points,counter,(len(savedParts)+len(showParts)-int(counter)))
                    # print str(len(savedParts)) + " " + str(len(showParts))

                    rankings.append([show,points])
                    # print notrange
            rankings = sorted(rankings,key=lambda x: x[1], reverse=True)
        
            for x in range(21):
                # This determines how much wait the string needs in order ot be rput into the list.
                # For now the weight of the string needs to have atlest a 20% in stirng similarity

                if rankings[x][1] > 0.2:
                    rankinglist.append(rankings[x][0])
                    continue
                
                elif rankings[x][1] < 0.2:
                    # print rankings[x][0]
                    otherlist.append(rankings[x][0])
                    # print otherlist

            print "\nTop Results"
            print '-'*15
            for z in range(len(rankinglist)):
                print "(%d) \t%s" %(z+1, rankinglist[z])
                # print len(rankinglist)
            print "\nSimilar Results"
            print "-"*15

            for y in range(len(otherlist)):
                # print y
                print "(%d) \t%s" %(y+len(rankinglist)+1, otherlist[y])
              

        except:
            print 'Error: String Similarity Failed!'

def showSearch(askShow):

    if askShow is None:
        askShow = raw_input("Search for a show: ")
        originalName = askShow
        askShow = grammarCheck(askShow)
    else:
        originalName = askShow
        askShow = grammarCheck(askShow)

    rankinglist = []
    mightShow = []
    newShows = []

    similarStrings(askShow,showList,rankinglist,mightShow)

    if len(rankinglist) == 0 and len(mightShow) == 0:
        likeToAdd(newShows, originalName)
    else:
        showAbove = raw_input("\nIs the show you were looking for listed above?: ").lower()
        if showAbove == 'yes':
            whatNum = int(raw_input("Enter the integer of the show: "))
            if whatNum <= (len(rankinglist) + len(mightShow)):
                whatNum -= 1
                if whatNum >= len(rankinglist):
                    showfound = mightShow[whatNum-len(rankinglist)]
                    showOptions(showfound, showfoldpath,showList,bookmarklist)
                else:
                    showfound = rankinglist[whatNum]
                    showOptions(showfound, showfoldpath, showList, bookmarklist)
            else:
                print 'Error: The number (%d) entered is out of index.' %(whatNum)
        else:
            likeToAdd(newShows, originalName)