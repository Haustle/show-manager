import os, re, subprocess, urllib, urllib2
import tmdbsimple as tmdb
import webbrowser, shutil, requests, time, ssl
from logger import Logger



#Need to add folderBalance need to find a simpler way to do it
class searchtools(object):
    isShow = False
    

    def __init__(self,root_folder):

        self.showsfolder = root_folder + "shows/"
        self.showtxt = root_folder + "showlist.txt"
        self.bookmarktxt = self.showsfolder + "[BOOKMARKED SHOWS].txt"
        self.logtxt = root_folder + "log.txt"
        self.downfolder = root_folder+"downloads"
        self.moviesfolder = root_folder + "movies/"
        self.movietxt = root_folder + "movielist.txt"
        self.bookmarkmovies = self.moviesfolder + "[BOOKMARKED MOVIES].txt"
        
    def getTextFile(self):
        return self.movietxt if searchtools.isShow is False else self.showtxt
        
        
    def localDelete(self):
        currentTime = time.strftime("%c")
        with open(self.getTextFile(),'r') as f:
            logShowList = [line.strip() for line in f]

        folderlist = self.getMediaList()
        for show in logShowList:
            if show not in folderlist:

                logString = "\n%s \t[LOCAL DELETE] %s \n" % (currentTime, show)
                l = open(self.logtxt,'a')
                l.write(logString)
                l.close()
        


    def grammarCheck(self,show):
        titleshit = re.findall(r'vs|the|and|of|at|by|down|for|from|in|into|like|near|off|on|into|to|with|till|when|yet|or|so|a', show)
        showName = show
        splitShow = showName.split(" ")
        # searchtools.isMovie = True
        # print searchtools.isMovie
        i = 0
        if titleshit > 0:
            for item in splitShow:
                wordIndex = splitShow.index(item.lower())
                if item not in titleshit:
                    item = item.title()

                    splitShow[wordIndex] = item
                    if "\'" in splitShow[wordIndex]:

                        wordlist = list(item)
                        something = wordlist.index("\'")
                        for letter in wordlist[something:]:
                            letNum = wordlist.index(letter)
                            wordlist[letNum] = wordlist[letNum].lower()

                        item = ''.join(wordlist)
                        splitShow[wordIndex] = item

                elif (item in titleshit and splitShow[0].lower()) and i == 0:
                    wordIndex = splitShow.index(item)
                    splitShow[wordIndex] = splitShow[wordIndex].title()

                i+=1

            showName = " ".join(splitShow)

        else:
            showName = showName.title()
        return showName
    
    def showOptions(self,show):
        logger = Logger()
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




        if whatNext.lower() == 'a' and searchtools.isShow:
            print 'Show Details : \'%s\'' %(show)
            filesInPath = sorted(os.listdir(self.showsfolder+show))
            # print filesInPath
            seasonCount = []
            for file in filesInPath:
                if file.startswith("Season "):
                    # print file
                    seasonCount.append(file)
            print ''
            if len(seasonCount) > 0:
                for season in seasonCount:
                    lenForSeason = len(os.listdir(self.showsfolder+show+'/'+season))
                    # numOfEpisodes+= lenForSeason
                    print '%s: %d Episodes' %(season, lenForSeason)
            else:
                print 'No seasons were found'






        elif whatNext.lower() == 'b':
            print ('Opening {} \'folder\'...'.format(show))       
            subprocess.call(["open","-R", self.showsfolder+show+"/Season 1"])
            print " "
            print  self.showsfolder+show+"/"
            print 'We opened \'%s\'' % (show)

        elif whatNext.lower() == 'c':

            # Checking for new seasons and episodes
            # Upon running this command tell the user how many episodes they are missing
            # Then ask them if they'd like to add episodes to to a specific season or all
            # Check if the season they want to add already has episodes
            # Allow the user to enter '1-15 and 2-34' so they can download in groups (maybe limit them to 25 at a time)

            print 'SHOW UPDATE'
            print '\na. Check if all seasons are up to date'
            print 'b. Chceck specific seasons'

            options = raw_input("\nChoose one of the above options: ")

            
            # options = raw_input(" ")
            filesInPath = sorted(os.listdir(self.showsfolder+show))

            # Turn this into a function to just find out how many seasons there are
            # Not sure how many times I've used this function

            seasonCount = []
            for file in filesInPath:
                if file.startswith("Season "):
                    seasonCount.append(file)

            showId = (self.onlyShow(show))[0][1]
            # showId = showId[0][1]
            
            if options == 'a':
                firsttime = True
                for x in range(1,len(seasonCount)+1):
                    missingEpisodes = []
                    full_season_list = self.episodeList(x,showId,losteps=True)
                    season = "/Season {}".format(x)
                    episodes_in_folder = os.listdir(self.showsfolder+show+season)
                    missingEpisodes = set(full_season_list) ^ set(episodes_in_folder)
                    # if len(missingEpisodes) == 0:
                    #     print '\nThere are no missing episodes in \'Season {}\''.format(x)
                    if len(missingEpisodes)>0:
                        print ''
                        missingEpisodes = self.forbiddenFiles(missingEpisodes)
                        self.missingTable(x,missingEpisodes, firstime=firsttime)
                        firsttime = False


            elif options == 'b':
                try:
                    whatSeason = (raw_input("\nWhat season do you want to check?: "))
                    missingEpisodes = []
                    if whatSeason.isdigit() and int(whatSeason) <= seasonCount:
                        full_season_list = self.episodeList(int(whatSeason),showId,losteps=True)
                        season = "/Season {}".format(whatSeason)
                        episodes_in_folder = os.listdir(self.showsfolder+show+season)
                        missingEpisodes = set(full_season_list) ^ set(episodes_in_folder)
                        self.forbiddenFiles(missingEpisodes)
                        if len(missingEpisodes) == 0:
                            print 'There are no missing episodes in \'Season {}\''.format(whatSeason)
                        else:
                            missingEpisodes = self.forbiddenFiles(missingEpisodes)
                            self.missingTable(whatSeason,missingEpisodes)

                    else:
                        print 'Error: Either the input is not in the season range or it\'s not a number.' 
                except:
                    print 'Can\'t check this season'
            


        elif whatNext.lower() == 'd':
            if show in bookmarklist:
                print '\nThis show is already bookmarked'
            else:
                bookmarklist.append(show)
                print '\nThis show is now BOOKMARKED'




        elif whatNext.lower() == 'e':
            with open(self.bookmarktxt,'r') as f:
                bookmarklist = [line.strip() for line in f]
            if show in bookmarklist:
                print '\nIt\'s here'
                bookmarklist.remove(bookmarklist[bookmarklist.index(show)])
                print bookmarklist

            print '\nDeleting \'%s\'...' %(show)
            shutil.rmtree(self.showsfolder+show)

            currentTime = time.strftime("%c")
            log = self.logtxt
            logString = "%s \t[DELETE] %s \n" % (currentTime, show)

            l = open(self.logtxt,"r")
            lastline = l.readlines()
            l.close()
            lastline = lastline[len(lastline)-1]
            lastLog = lastline.split(" ")
            if len(lastLog)>0:
                # print lastLog
                for part in lastLog:
                    # Because  [NEW SHOW] is split in half we're only checking for the first part
                    if part == '\t[NEW':
                        logString = "\n\n"+logString
                        break


            logger.writeLog(self.logtxt,message=logString)
            print '[-]This show has been deleted'
        else:
            print 'The previous input was invalid.'




    def showSearch(self,show=None):
        self.localDelete()

        medialist = self.getMediaList()

        rankinglist = []
        mightShow = []

        if len(medialist) > 0:
            self.similarStrings(rankinglist,mightShow,show)
            if len(rankinglist) == 0 and len(mightShow) == 0:
                self.likeToAdd(show)

            else:
                showAbove = raw_input("\nIs the result you were looking for listed above?: ").lower()
                if showAbove == 'yes':
                    whatNum = int(raw_input("Enter the integer of the show: "))
                    if whatNum <= (len(rankinglist) + len(mightShow)):
                        whatNum -= 1
                        if whatNum >= len(rankinglist):
                            showfound = mightShow[whatNum-len(rankinglist)]
                            self.showOptions(showfound)
                        else:
                            showfound = rankinglist[whatNum]
                            self.showOptions(showfound)
                    else:
                        print '[!] Error: The number (%d) entered is out of index.' %(whatNum)
                else:
                    self.likeToAdd(show)
                    # print 'o wow'
        else:
            self.likeToAdd(show)
                
    def similarStrings(self,rankinglist,otherlist,show):

        rankings = self.matchinglist(show)
        norm_list_length = 21
        if len(rankings) < norm_list_length: norm_list_length = len(rankings)

        for x in range(norm_list_length):
            if rankings[x][1] > 0.2:
                rankinglist.append(rankings[x][0])
                continue
            
            elif rankings[x][1] < 0.1:
                otherlist.append(rankings[x][0])


        dash = "-"*15
        print "\nTop Results"
        print '-'*70
        print "{:<8}{}\n".format("RANK","NAME")
        # print dash


        if len(rankinglist) > 0:
            for z in range(len(rankinglist)):
                print "%d \t%s" %(z+1, rankinglist[z])
        else:
            print 'none'

        
        # print dash
        if len(otherlist) > 0:
            print "\nSimilar Results"
            print '-'*70
            print "{:<8}{}\n".format("RANK","NAME")
            for y in range(len(otherlist)):
                print "%d \t%s" %(y+len(rankinglist)+1, otherlist[y])
        # else:
            # print 'none'

    def matchinglist(self,name):
        shows = self.getMediaList()
        shows.sort()
        if name == None: name = self.show
        

        savedParts = []
        for x in range(len(name)):
            partOfname = name[x:x+2]
            savedParts.append(partOfname)

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
                    if show == '[BOOKMARKED SHOWS].txt': continue
                    counter = 1
                    showParts = []
                    # print 'mynow'
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


                        rankings.append([show,points])
                        # print notrange

                rankings = sorted(rankings,key=lambda x: x[1], reverse=True)
                return rankings
            except:
                print '\n[!] Error: String Similarity Failed!'
        
    

    def newDir(self,show):
        folderloc = (self.showsfolder+show) if searchtools.isShow is True else (self.moviesfolder+show)
        os.mkdir(folderloc)
        global showlogfile
        if searchtools.isShow is True:
            showlogfile = "%s/%s log.txt" %(folderloc,show)
            f = open(showlogfile,"w+")
            f.close()
        self.addShowInfo(show)

    def onlyShow(self,show):
        tmdb.API_KEY = '7e022dc2338ac2988670ddb93ccff401'
        search = tmdb.Search()
        reponse = search.tv(query=show)
        list_results = []
        if len(search.results) > 0:
            for x in range(len(search.results)):
                list_results.append([((search.results[x])['name']).encode('utf-8'), search.results[x]['id']])
            return list_results
    def onlyMovie(self,movie):
        tmdb.API_KEY = '7e022dc2338ac2988670ddb93ccff401'
        search = tmdb.Search()
        reponse = search.movie(query=movie)
        list_results = []
        if len(search.results)>0:
            for x in range(len(search.results)):
                list_results.append([((search.results[x])['title']).encode('utf-8'), search.results[x]['id']])
            return list_results


    def likeToAdd(self,show):
        addShow = raw_input("Would you like to add \'%s\'?: " % show)
        if addShow.lower() == 'yes':


            print ''
            print '[1] Keep the original name:\t\'%s\'' %(show)
            print '[2] Get a title case name:\t\'%s\'' %(self.grammarCheck(show))

            foundshows = self.onlyShow(show) if searchtools.isShow else self.onlyMovie(show)

            if foundshows != None : 
                whatisit = "show" if searchtools.isShow else "movie"
                print'[3] Closest real {}:\t\t\'{}\''.format(whatisit,foundshows[0][0])
                # print len(foundshows)
                print '\n...More options'


            else: print '\n\n[!] Error: This show was not found in MovieDB database. Maybe try and re-spell'

            
            # try:
            titleChoice = raw_input("\nChoose one of the above options: ")
            if titleChoice == '1':
                if self.exists(show) == False:
                    self.newDir(show)

            elif titleChoice == '2':
                
                if self.exists(self.grammarCheck(show)) == False:
                    self.newDir(self.grammarCheck(show))
                else:
                    print '[!] Error: The show is already in the database'
                
            elif titleChoice == '3' and foundshows!= None:
                if self.exists(foundshows[0][0]) == False:
                    self.newDir(foundshows[0][0])
                else:
                    print '[!] Error: The show is already in the database'

            elif titleChoice == 'more' and foundshows != None:
                if len(foundshows) > 1:
                    for x in range(len(foundshows)):
                        print("({})\t{}").format(x+1,foundshows[x][0])
                else:
                    print '[!] Error: There are no more similar shows'
            
            else:
                print 'That option is out of range'
            # except:
            #     print 'That is not an option'

    def exists(self,something):
        medialist = [item.lower() for item in self.getMediaList()]
        return True if something.lower() in medialist else False


    def getMediaList(self):
        medialist = []

        if searchtools.isShow:
            medialist = os.listdir(self.showsfolder)        
        else:
            medialist = os.listdir(self.moviesfolder)

        # print medialist
        return self.forbiddenFiles(medialist)
        

    def addShowInfo(self,show):
        logger = Logger()
        global api 
        api = '7e022dc2338ac2988670ddb93ccff401'
        search = tmdb.Search()
        count = 1

       
        response = search.tv(query=show) if searchtools.isShow is True else search.movie(query=show)
        showpath = (self.showsfolder+show+"/") if searchtools.isShow is True else (self.moviesfolder+show+"/")

        posterBase = 'https://image.tmdb.org/t/p/w500'
        if len(search.results) > 0:
            something = search.results[0]
           
            overview = something['overview']
            overviewpath = ""
            if searchtools.isShow is True:
                overviewpath = self.showsfolder+show+"/overview.txt"
            else:
                overviewpath = self.moviesfolder+show+"/overview.txt"
            logger.writeLog(overviewpath, message=overview, overview=True)

            show_id = (something['id'])
            poster = (something['poster_path'])
            if poster is None:
                print '%s contained None' %(show)

            posterLink = posterBase + poster

            if os.path.isdir(showpath) == True:
                if os.path.exists(showpath+"cover.jpg") == True:
                    print '\'%s\' already has a picture' %(show)

                else:
                    # ,(showpath+"cover.jpg")
                    context = ssl._create_unverified_context()
                    imgDownload = urllib2.urlopen(posterLink, context=context)

                    imgfile = open((showpath+"cover.jpg"),'wb')
                    imgfile.write(imgDownload.read())
                    imgfile.close()

                    if searchtools.isShow is True:
                        url = "https://api.themoviedb.org/3/tv/%d?api_key=%s&language=en-US" % (show_id,api)
                        payload = "{}"
                        json_data = requests.get(url).json()
                        seasonnum = json_data['number_of_seasons']
                        for y in range(1,seasonnum+1):
                            newSeason = "Season {}".format(y)
                            seasonpath = showpath+newSeason
                            os.mkdir(seasonpath)
                            self.addEpisodes(show_id,seasonpath,y)

                            #THIS WHERE THE EPISODES NEEDS TO BE ADDED FOR THE SHOW


                        print '[+] %s retreived' %(show)
                        currentTime = time.strftime("%c")
                        logString = "%s \t[NEW SHOW] %s (%d seasons)\n" % (currentTime, show, seasonnum)
                        l = open(self.logtxt,"r")
                        lastline = l.readlines()
                        l.close()
                        if len(lastline) > 0:
                            lastline = lastline[len(lastline)-1]
                            lastLog = lastline.split(" ")

                            if len(lastLog)>0:
                                for part in lastLog:
                                    if part == '\t[DELETED]':
                                        logString = "\n"+logString
                                        break


                        logger.writeLog(self.logtxt,message=logString)
                    
            else:
                print '%s path doesn\'t exist' %(show)
        else:
            print '[!] Error: Poster, overview, and season was not found for \'%s\' ' %(show)
            seasonAmount = raw_input("Enter the amount of seasons this show has: ")
            if seasonAmount.isdigit():
                for i in range(0,int(seasonAmount)):
                    newSeason = "Season %d" %(i+1)
                    os.mkdir(showpath+newSeason)

    def addEpisodes(self,show_id,seasonpath,seasonNum):
        logger = Logger()
        epdetails = self.episodeList(seasonNum,show_id,losteps=False)
        for x in range(len(epdetails)):

            ep_name = epdetails[x][0]
            ep_over = epdetails[x][1]

            newepfolder = seasonpath+"/"+ep_name
            newoverview = newepfolder+"/overview.txt"

            try:
                os.mkdir(newepfolder)
                logger.writeLog(newoverview,message=ep_over,overview=True)

            except:
                LOG_MESSAGE = "\n\nError: Adding \'{}\' \nSUPPOSED FILEPATH: \'{}".format(ep_name, newepfolder)
                print LOG_MESSAGE
                logger.writeLog(showlogfile,message=LOG_MESSAGE)
                continue



    def episodeList(self,seasonNum,show_id,losteps=True):
        api = '7e022dc2338ac2988670ddb93ccff401'
        url = "https://api.themoviedb.org/3/tv/{}/season/{}?api_key={}&language=en-US".format(show_id,seasonNum,api)
            
        eplist = []
        resp = requests.get(url)
        json_data = requests.get(url).json()
        
        for episode in json_data["episodes"]:

            epnum = int(episode["episode_number"])
            epname = episode["name"].encode('utf-8')
            # print type(epnum), type(epname)
            if epnum < 10: epnum = "0"+str(epnum)


            #WANT TO CHANGE THIS TO HAVE ACTUAL FORMATING AND NOT HAVING TO ADD 0 IN FRONT OF NUMBERMU
            filename = "E{} - {}".format(epnum,epname)

            if losteps == False: eplist.append([filename,episode["overview"].encode('utf-8')])
            else: eplist.append(filename)

        return eplist

    #Just to make sure lists don't contain any of these files 
    def forbiddenFiles(self, list_taken):
        newlist = list(list_taken)
    
        for file in newlist:
            if (file.startswith(".") or (file == '[BOOKMARKED SHOWS].txt') or (file == '[BOOKMARKED MOVIES].txt')): 
                newlist.remove(newlist[newlist.index(file)])            
        return newlist

    def breakEpName(self, epname):
        indentifier = re.findall(r'E(\d+) - (.*)',epname)
        epnum = indentifier[0][0]
        epbane = indentifier[0][1]
        return epnum, epname

    def missingTable(self,season,epnames,firstime=True):
        if firstime is True:
            print("\n{:<10} {:<10} {}").format("Season","EP #", "EP. NAME")
            print ' '
        
        for x in range(len(epnames)):
            indentifier = re.findall(r'E(\d+) - (.*)',epnames[x])
            epnum = indentifier[0][0]
            epname = indentifier[0][1]
            if x == 0:
                print("{:<10} {:<10} {}").format(season,epnum, epname)
            else:
                 print("{:<10} {:<10} {}").format(" ",epnum, epname)

            # print '-'*60
        print '-'*70

            