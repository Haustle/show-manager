import os, re, subprocess, urllib, urllib2, config
import tmdbsimple as tmdb
import webbrowser, shutil, requests, time, ssl, json
from logger import Logger
from pprint import pprint



class searchtools(object):
    # IF SCRIPT IS DEALING WITH MOVIES OR SHOWS
    isShow = False
    api = config.api_key
    

    def __init__(self,root_folder):

        self.showsfolder = os.path.normpath(root_folder + "shows/")
        self.showtxt = os.path.normpath(root_folder + "showlist.txt")
        self.bookmarktxt = os.path.normpath(self.showsfolder + "[BOOKMARKED SHOWS].txt")
        self.logtxt = os.path.normpath(root_folder + "log.txt")
        self.downfolder = os.path.normpath(root_folder+"downloads")
        self.moviesfolder = os.path.normpath(root_folder + "movies/")
        self.movietxt = os.path.normpath(root_folder + "movielist.txt")
        self.bookmarkmovies = os.path.normpath(self.moviesfolder + "[BOOKMARKED MOVIES].txt")
        
    # RETURNS THE TEXT FILE PATH THAT CONTAINS LIST OF SHOWS/MOVIES IN A DIRECTORY
    def getTextFile(self):
        return os.path.normpath(self.movietxt) if searchtools.isShow is False else os.path.normpath(self.showtxt)
        
    # THIS FUNCTION CHECKS TO SEE IF A USER DELETED A MOVIE/SHOW LOCALLY (NOT WHILE SCRIPT WAS RUNNING)    
    
    def localDelete(self):
        currentTime = time.strftime("%c")
        with open(os.path.normpath(self.getTextFile()),'r') as f:
            logShowList = [line.strip() for line in f]

        folderlist = self.getMediaList()
        for show in logShowList:
            if show not in folderlist:

                logString = "\n%s \t[LOCAL DELETE] %s \n" % (currentTime, show)
                l = open(self.logtxt,'a')
                l.write(logString)
                l.close()
    
    def jsonFormat(self,somelist):
        
        data ={
            "details": {
                
            }
        }
        detail = data["details"]
        for line in somelist:
            detail[line[0]] = line[1]
        # pprint(data)
        return data

    # TURNS A NAME OF A SHOW/MOVIE INTO PROPER TITLE CASE
    def grammarCheck(self,show):
        titleshit = re.findall(r'vs|the|and|of|at|by|down|for|from|in|into|like|near|off|on|into|to|with|till|when|yet|or|so|a', show)
        showName = show
        splitShow = showName.split(" ")

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
    
    # PRINT THE LIST OF OPTIONS DEPENDING ON IF THE SEARCH IS TOWARDS MOVIES OR SHOWS
    def printOptions(self,name):
        towards = "show" if searchtools.isShow else "movie"
        print '\n'*4
        print name
        print '-'*10
        print ''
        print 'Print {} details'.format(towards)
        print 'Open the folder of {}'.format(towards)
        if searchtools.isShow: print 'Check for missing Episodes'
        print 'Bookmark this {}'.format(towards)
        print 'Delete this {}'.format(towards)


    def showOptions(self,show):
        logger = Logger()
        self.printOptions(show)
        whatNext = raw_input("\nChoose one of the above options: ")



        # PRINT DETAILS OF THE MOVIE/SHOW
        if whatNext.lower() == 'a':
            print 'Show Details : \'%s\'' %(show)
            seasonCount = sorted(os.listdir(os.path.normpath(self.showsfolder+show+"/Content")))            
            print ''
            if len(seasonCount) > 0:
                for season in seasonCount:
                    lenForSeason = len(os.listdir(os.path.normpath(self.showsfolder+show+'/'+season)))

                    print '%s: %d Episodes' %(season, lenForSeason)
            else:
                print 'No seasons were found'





        # WILL OPEN THE DIRECTORY OF THE FILE
        elif whatNext.lower() == 'b':
            print ('Opening {} \'folder\'...'.format(show))       
            subprocess.call(["open","-R", os.path.normpath(self.showsfolder+show+"/Season 1")])
            print " "
            print  os.path.normpath(self.showsfolder+show+"/")
            print 'We opened \'%s\'' % (show)


        # CHECKS THE FOLDER FOR MISSING EPISODES
        elif whatNext.lower() == 'c' and searchtools.isShow:


            print 'SHOW UPDATE'
            print '\na. Check if all seasons are up to date'
            print 'b. Chceck specific seasons'

            options = raw_input("\nChoose one of the above options: ")

            
            seasonCount = sorted(os.listdir(os.path.normpath(self.showsfolder+show+"/Content")))

            showId = (self.tmdbShowResults(show))[0][1]

            
            # CHECKS ALL FOLDERS FOR MISSING EPISODES
            if options == 'a':
                firsttime = True
                for x in range(1,len(seasonCount)+1):
                    missingEpisodes = []
                    full_season_list = self.episodeList(x,showId,losteps=True)
                    season = "/Season {}".format(x)
                    episodes_in_folder = os.listdir(os.path.normpath(self.showsfolder+show+season))
                    missingEpisodes = set(full_season_list) ^ set(episodes_in_folder)

                    if len(missingEpisodes)>0:
                        print ''
                        missingEpisodes = self.forbiddenFiles(missingEpisodes)
                        self.missingTable(x,missingEpisodes, firstime=firsttime)
                        firsttime = False

            # CHECKS FOR MISSING EPISODES OF A SPECIFIC SEASON
            elif options == 'b':
                try:
                    whatSeason = (raw_input("\nWhat season do you want to check?: "))
                    missingEpisodes = []
                    if whatSeason.isdigit() and int(whatSeason) <= seasonCount:
                        full_season_list = self.episodeList(int(whatSeason),showId,losteps=True)
                        season = "/Season {}".format(whatSeason)
                        episodes_in_folder = os.path.normpath(os.listdir(self.showsfolder+show+season))
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
            

        # BOOKMARKS THE SHOW OR MOVIE
        elif whatNext.lower() == 'd':
            if show in bookmarklist:
                print '\nThis show is already bookmarked'
            else:
                bookmarklist.append(show)
                print '\nThis show is now BOOKMARKED'



        # DELETES THE SHOW OR MOVIE
        elif whatNext.lower() == 'e':
            with open(self.bookmarktxt,'r') as f:
                bookmarklist = [line.strip() for line in f]
            if show in bookmarklist:
                print '\nIt\'s here'
                bookmarklist.remove(bookmarklist[bookmarklist.index(show)])
                print bookmarklist

            print '\nDeleting \'%s\'...' %(show)
            shutil.rmtree(os.path.normpath(self.showsfolder+show))

            currentTime = time.strftime("%c")
            log = self.logtxt
            logString = "%s \t[DELETE] %s \n" % (currentTime, show)

            l = open(self.logtxt,"r")
            lastline = l.readlines()
            l.close()
            lastline = lastline[len(lastline)-1]
            lastLog = lastline.split(" ")
            if len(lastLog)>0:

                for part in lastLog:
                    # Because  [NEW SHOW] is split in half we're only checking for the first part
                    if part == '\t[NEW':
                        logString = "\n\n"+logString
                        break


            logger.writeLog(self.logtxt,message=logString)
            print '[-]This show has been deleted'
        else:
            print 'The previous input was invalid.'



    # FUNCTION THAT ACCEPTS ONE PARAMENTER A SHOW/MOVIE AND CHECKS DIRECTORIES FOR SIMILARLY NAMED
    def showSearch(self,show=None):
        self.localDelete()

        medialist = self.getMediaList()

        rankinglist = []
        mightShow = []

        # THIS CONDITION FOR WHEN NO FILE IN DIRECTORY
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
                    
        else:
            self.likeToAdd(show)
    

    # PRINTS OUT THE TWO RANKING LIST
    def similarStrings(self,rankinglist,otherlist,show):
        rankings = self.matchinglist(show)
        norm_list_length = 21
        if len(rankings) < norm_list_length: norm_list_length = len(rankings)

        for x in range(norm_list_length):

            # WEIGHTS TO DECIDE WHAT LIST SHOWS/MOVIES ARE PLACED ON
            if rankings[x][1] > 0.2:
                rankinglist.append(rankings[x][0])
                continue
            
            elif rankings[x][1] < 0.1:
                otherlist.append(rankings[x][0])


        dash = "-"*70

        # PRINTS OUT THE TOP RESULTS
        if len(rankinglist) > 0:
            print "\nTop Results"
            print '-'*70
            print "{:<8}{}\n".format("RANK","NAME")

            if len(rankinglist) > 0:
                for z in range(len(rankinglist)):
                    print "%d \t%s" %(z+1, rankinglist[z])
            print ''
        
        # PRINTS OUT THE OTHER RESULTS
        if len(otherlist) > 0:
            print "\nOther Results"
            print dash
            print "{:<8}{}\n".format("RANK","NAME")
            for y in range(len(otherlist)):
                print "%d \t%s" %(y+len(rankinglist)+1, otherlist[y])
        if len(otherlist) == 0 and len(rankinglist) == 0:
            print '\nNo results have been found in the database'

    # FUNCTIONS GOES THROUGH THE LIST OF SET MEDIA AND FINDS SIMILARITIES BETWEEN THE SHOWS
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
                    
                    for x in range(len(show)):
                        partOfname = show[x:x+2]
                        showParts.append(partOfname)

                    notrange = []
                    for x in range(len(savedParts)):
                        for y in range(len(showParts)):
                            if savedParts[x].lower() == showParts[y].lower() and (y not in notrange):
                                notrange.append(y)
                               
                                counter +=1
                                break

                    if counter > 1:
                        counter = float(counter - 1)
                        points = (counter)/(float(len(savedParts)+len(showParts)-counter))


                        rankings.append([show,points])
                        

                rankings = sorted(rankings,key=lambda x: x[1], reverse=True)
                return rankings
            except:
                print '\n[!] Error: String Similarity Failed!'
        
    
    # FUNCTION RESPONSIBLE OF CREATING FOLDER DIRECTORY
    def newDir(self,show,local=False):
        folderloc = (self.showsfolder) if searchtools.isShow is True else (self.moviesfolder)
        print folderloc






        # print os.path.exists(folderloc)
        folderloc = os.path.join(folderloc,show)
        print folderloc
        # folderloc = os.path.normpath(folderloc)
        # print folderloc
        # print repr(folderloc)
        # print repr(os.path.normpath(folderloc))
        os.mkdir(folderloc)
        # os.mkdir(os.path.normpath(folderloc+"/Content"))













        global showlogfile
        if searchtools.isShow is True:
            showlogfile = "%s/%s log.txt" %(folderloc,show)
            f = open(showlogfile,"w+")
            f.close()
        # DECIDES WHETHER TO CREATE A SPECIALIZED DIRECTORY OR ONE CREATED BY API
    
        self.addShowInfo(show) if local is False else self.localShow(show)

    # WHEN NO MOVIES/SHOWS ARE FOUND BUT THE USER STILL WANTS TO ADD THEM TO THE LIST.
    def localShow(self,show):
        folderloc = (self.showsfolder+show) if searchtools.isShow is True else (self.moviesfolder+show)
        print 'Because this is a show created locally. We need to add some details to the show'
        print 'Below are things that you need to edit manually: \n{}\n{}'.format("cover.jg","overview (edit in deails.txt)")
        seasonAmount = raw_input("\nEnter the amount of seasons this show has: ")
        if seasonAmount.isdigit():
            for i in range(0,int(seasonAmount)):
                newSeason = "Season %d" %(i+1)
                os.mkdir(os.path.normpath(folderloc+"/Content/"+newSeason))

    # FUNCTION RETURNS LIST OF SHOWS FOUND IN TMDB SEARCH
    def tmdbShowResults(self,show): 
        tmdb.API_KEY = searchtools.api
        search = tmdb.Search()
        reponse = search.tv(query=show)
        list_results = []
        if len(search.results) > 0:
            for x in range(len(search.results)):
                list_results.append([((search.results[x])['name']).encode('utf-8'), search.results[x]['id']])
            return list_results

    # FUNCTION RETURNS LIST OF MOVIES FOUND IN TMDB SEARCH
    def tmdbMovieResults(self,movie):
        tmdb.API_KEY = searchtools.api
        search = tmdb.Search()
        reponse = search.movie(query=movie)
        list_results = []
        if len(search.results)>0:
            for x in range(len(search.results)):
                list_results.append([((search.results[x])['title']).encode('utf-8'), search.results[x]['id']])
            return list_results

    # FUNCTION RESPONSIBLE DECIDING WHICH NAME WILL BE USED FOR DIRECTORY
    def likeToAdd(self,show):
        addShow = raw_input("Would you like to add \'%s\'?: " % show)
        if addShow.lower() == 'yes':


            print ''
            print '[1] Keep the original name (local):\t%s' %(show)
            print '[2] Get a title case name (local):\t%s' %(self.grammarCheck(show))

            foundshows = self.tmdbShowResults(show) if searchtools.isShow else self.tmdbMovieResults(show)

            if foundshows != None : 
                whatisit = "show" if searchtools.isShow else "movie"
                print'[3] Closest real {}(api):\t\t{}'.format(whatisit,foundshows[0][0])
                if len(foundshows) > 1 : print '\nMore'


            else: print '\n\n[!] Error: This show was not found in MovieDB database. Maybe try and re-spell'

            

            titleChoice = raw_input("\nChoose one of the above options: ")

            if (titleChoice == 'more') and (len(foundshows) > 1):
                print ''
                for x in range(1,len(foundshows)-1):
                    print("[{}]\t{}").format(3+x,foundshows[x][0])
                enterabove = int(raw_input("\nChoose one of the above options (including 1-3): "))

                if enterabove == 1:
                    if self.exists(show) is False: self.newDir(show,local=True)

                elif enterabove == 2:
                    show = self.grammarCheck(show)
                    if self.exists(show) is False: self.newDir(show,local=True)

                elif enterabove > 2 and enterabove <= len(foundshows)+2:
                    enterabove -=3
                    if self.exists(foundshows[enterabove][0]) is False:
                        self.newDir(foundshows[enterabove][0])


            elif titleChoice == '1':
                if self.exists(show) == False:
                    self.newDir(show,local=True)

            elif titleChoice == '2':
                if self.exists(self.grammarCheck(show)) == False:
                    show = self.grammarCheck(show)
                    self.newDir(show,local=True)
                
            elif titleChoice == '3' and foundshows!= None:
                if self.exists(foundshows[0][0]) == False:
                    self.newDir(foundshows[0][0])
                
                
            
            else:
                print 'That option is out of range'

    # FUNCTION CHECKS TO SEE IF THE DIRECTORY IS PRE-EXISTING
    def exists(self,show):
        medialist = [item.lower() for item in self.getMediaList()]
        if show.lower() in medialist: 
            print '\n[!] Error: The show is already in the database'
            return True
        return False

    # FUNCTION RETURNS EITHER LIST OF LOCAL MOVIES OR SHOWS DEPENDING ON WHAT USER SEARCHED
    def getMediaList(self):
        medialist = []

        if searchtools.isShow:
            medialist = os.listdir(os.path.normpath(self.showsfolder))        
        else:
            medialist = os.listdir(os.path.normpath(self.moviesfolder))

        # print medialist
        return self.forbiddenFiles(medialist)
        

    # FUNCTION GOES THROUGH API TO FIND COVER, EPISODE NAMES, OVERVIEW AND SAVES THEM LOCALLY
    def addShowInfo(self,show):
        logger = Logger()
        global api 
        api = searchtools.api
        search = tmdb.Search()
        count = 1

       
        response = search.tv(query=show) if searchtools.isShow is True else search.movie(query=show)
        showpath = (os.path.normpath(self.showsfolder+show+"/")) if searchtools.isShow is True else (os.path.normpath(self.moviesfolder+show+"/"))

        posterBase = 'https://image.tmdb.org/t/p/w500'
        if len(search.results) > 0:
            topresult = search.results[0]
           

            listforJson = []
            listforJson.append(["overview",topresult['overview']])
            listforJson.append(["poster_path",topresult["poster_path"]])
            listforJson.append(["release_date", (topresult["first_air_date"] if searchtools.isShow else topresult["release_date"])])
            listforJson.append(["language",topresult["original_language"]])
            listforJson.append(["id",topresult['id']])
            listforJson.append(["locally_made",False])

            jsontext = self.jsonFormat(listforJson)
            with open(os.path.join(showpath,"details.json"),"w") as f:
                sometext = json.dumps(jsontext,indent=4)
                f.write(sometext)
                f.close()






            
            if topresult["poster_path"] is None:
                print '%s contained None' %(show)

            posterLink = posterBase + topresult["poster_path"]

            if os.path.isdir(showpath) == True:
                if os.path.exists(os.path.normpath(showpath+"cover.jpg")) == True:
                    print '\'%s\' already has a picture' %(show)

                else:
                    
                    context = ssl._create_unverified_context()
                    imgDownload = urllib2.urlopen(posterLink, context=context)

                    imgfile = open(os.path.normpath(showpath+"cover.jpg"),'wb')
                    imgfile.write(imgDownload.read())
                    imgfile.close()
                    if searchtools.isShow is False: print '[+] %s retreived' %(show)

                    if searchtools.isShow is True:
                        url = "https://api.themoviedb.org/3/tv/%d?api_key=%s&language=en-US" % (topresult["id"],api)
                        payload = "{}"
                        json_data = requests.get(url).json()





                        seasonnum = json_data['number_of_seasons']
                        for y in range(1,seasonnum+1):
                            newSeason = "Season {}".format(y)
                            seasonpath = showpath+"Content/"+newSeason
                            os.mkdir(os.path.normpath(seasonpath))
                            self.addEpisodes(topresult["id"],seasonpath,y)

                            


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
       
    # FUNCTION CALLED CREATE DIRECTORIES OF EACH EPISODE IN EPISODELIST FUNCTION
    def addEpisodes(self,show_id,seasonpath,seasonNum):
        logger = Logger()
        epdetails = self.episodeList(seasonNum,show_id,losteps=False)
        for x in range(len(epdetails)):

            ep_name = epdetails[x][0]
            ep_over = epdetails[x][1]

            newepfolder = os.path.normpath(seasonpath+"/"+ep_name)
            newoverview = os.path.normpath(newepfolder+"/overview.txt")

            try:
                os.mkdir(newepfolder)
                logger.writeLog(newoverview,message=ep_over,overview=True)

            except:
                LOG_MESSAGE = "\n\nError: Adding \'{}\' \nSUPPOSED FILEPATH: \'{}".format(ep_name, newepfolder)
                print LOG_MESSAGE
                logger.writeLog(showlogfile,message=LOG_MESSAGE)
                continue


    # FUNCTION GOES THROUGH TMDB API TO GET EPISODE NAMES AND RETURNS A LIST OF FORMATTED EPISODE NAMES
    def episodeList(self,seasonNum,show_id,losteps=True):
        api = searchtools.api
        url = "https://api.themoviedb.org/3/tv/{}/season/{}?api_key={}&language=en-US".format(show_id,seasonNum,api)
            
        eplist = []
        resp = requests.get(url)
        json_data = requests.get(url).json()
        
        for episode in json_data["episodes"]:

            epnum = int(episode["episode_number"])
            epname = episode["name"].encode('utf-8')
            if epnum < 10: epnum = "0"+str(epnum)


            #WANT TO CHANGE THIS TO HAVE ACTUAL FORMATING AND NOT HAVING TO ADD 0 IN FRONT OF NUMBERMU
            filename = "E{} - {}".format(epnum,epname)

            if losteps == False: eplist.append([filename,episode["overview"].encode('utf-8')])
            else: eplist.append(filename)

        return eplist

    # CHECKS A GIVEN LIST TO MAKE SURE THERE ARE NO FILES THAT SHOULDN'T BE THERE
    def forbiddenFiles(self, list_taken):
        newlist = list(list_taken)
    
        for file in newlist:
            if (file.startswith(".") or (file == '[BOOKMARKED SHOWS].txt') or (file == '[BOOKMARKED MOVIES].txt')): 
                newlist.remove(newlist[newlist.index(file)])            
        return newlist

    # FUNCTION THAT RECOGNIZES THE DIFFERENT ELEMENTS OF A FORMATTED EPISODE NAME
    def breakEpName(self, epname):
        indentifier = re.findall(r'E(\d+) - (.*)',epname)
        epnum = indentifier[0][0]
        epbane = indentifier[0][1]
        return epnum, epname

    # FUNCTION THAT DISPLAYS TABLE OF MISSING EPISODES
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

            