import os, re, subprocess, urllib, config, webbrowser, shutil, requests, time, ssl, json
import tmdbsimple as tmdb
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from logger import Logger

# from otakustream import show
import otakustream



class searchtools(object):
    # IF SCRIPT IS DEALING WITH MOVIES OR SHOWS
    isShow = False
    api = config.api_key
    

    def __init__(self,root_folder):

        self.showsfolder = os.path.join(root_folder,"shows")
        self.showtxt = os.path.join(root_folder,"showlist.txt")
        self.bookmarktxt = os.path.join(self.showsfolder,"[BOOKMARKED SHOWS].txt")
        self.logtxt = os.path.join(root_folder,"log.txt")
        self.downfolder = os.path.join(root_folder,"downloads")
        self.moviesfolder = os.path.join(root_folder ,"movies")
        self.movietxt = os.path.join(root_folder ,"movielist.txt")
        self.bookmarkmovies = os.path.join(self.moviesfolder,"[BOOKMARKED MOVIES].txt")
        
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

        return data

    # TURNS A NAME OF A SHOW/MOVIE INTO PROPER TITLE CASE
    def grammarCheck(self,show):
        title_words = re.findall(r'vs|the|and|of|at|by|down|for|from|in|into|like|near|off|on|into|to|with|till|when|yet|or|so|a', show)
        showName = show
        splitShow = showName.split(" ")
        # print (title_words)
        i = 0
        if len(title_words) > 0:
            for item in splitShow:
                wordIndex = splitShow.index(item.lower())
                if item not in title_words:
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

                elif (item in title_words and splitShow[0].lower()) and i == 0:
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
        print('\n')*4
        print (name)
        print('-')*10
        print ('')
        print('Print {} details').format(towards)
        print('Open the folder of {}').format(towards)
        if searchtools.isShow: print('Check for missing Episodes')
        print('Bookmark this {}').format(towards)
        print('Delete this {}').format(towards)


    def showOptions(self,show):
        logger = Logger()
        self.printOptions(show)
        whatNext = input("\nChoose one of the above options: ")



        # PRINT DETAILS OF THE MOVIE/SHOW
        if whatNext.lower() == 'a':
            print('Show Details : \')%s\'' %(show))
            seasonCount = sorted(os.listdir(os.path.normpath(self.showsfolder+show+"/Content")))            
            print ('')
            if len(seasonCount) > 0:
                for season in seasonCount:
                    lenForSeason = len(os.listdir(os.path.normpath(self.showsfolder+show+'/'+season)))

                    print('%s: %d Episodes') %(season, lenForSeason)
            else:
                print('No seasons were found')





        # WILL OPEN THE DIRECTORY OF THE FILE
        elif whatNext.lower() == 'b':
            print ('Opening {} \'folder\'...'.format(show))       
            subprocess.call(["open","-R", os.path.normpath(self.showsfolder+show+"/Season 1")])
            print(" ")
            print  (os.path.normpath(self.showsfolder+show+"/"))
            print('We opened \')%s\'' % (show))


        # CHECKS THE FOLDER FOR MISSING EPISODES
        elif whatNext.lower() == 'c' and searchtools.isShow:


            print('SHOW UPDATE')
            print('\na. Check if all seasons are up to date')
            print('b. Chceck specific seasons')

            options = input("\nChoose one of the above options: ")

            
            seasonCount = sorted(os.listdir(os.path.join(self.showsfolder,show,"Content")))

            showId = (self.tmdbShowResults(show))[0][1]

            
            # CHECKS ALL FOLDERS FOR MISSING EPISODES
            if options == 'a':
                firsttime = True
                for x in range(1,len(seasonCount)+1):
                    missingEpisodes = []
                    full_season_list = self.episodeList(x,showId,losteps=True)
                    season = "/Season {}".format(x)
                    episodes_in_folder = os.listdir(os.path.join(self.showsfolder,show,season))
                    missingEpisodes = set(full_season_list) ^ set(episodes_in_folder)

                    if len(missingEpisodes)>0:
                        print ('')
                        missingEpisodes = self.forbiddenFiles(missingEpisodes)
                        self.missingTable(x,missingEpisodes, firstime=firsttime)
                        firsttime = False

            # CHECKS FOR MISSING EPISODES OF A SPECIFIC SEASON
            elif options == 'b':
                try:
                    whatSeason = (input("\nWhat season do you want to check?: "))
                    missingEpisodes = []
                    if whatSeason.isdigit() and int(whatSeason) <= seasonCount:
                        full_season_list = self.episodeList(int(whatSeason),showId,losteps=True)
                        season = "/Season {}".format(whatSeason)
                        episodes_in_folder = (os.listdir(os.path.join(self.showsfolder,show,season)))
                        missingEpisodes = set(full_season_list) ^ set(episodes_in_folder)
                        self.forbiddenFiles(missingEpisodes)
                        if len(missingEpisodes) == 0:
                            print('There are no missing episodes in \'Season {}\''.format(whatSeason))
                        else:
                            missingEpisodes = self.forbiddenFiles(missingEpisodes)
                            self.missingTable(whatSeason,missingEpisodes)

                    else:
                        print('Error: Either the input is not in the season range or it\'s not a number.' )
                except:
                    print('Can\'t check this season')
            

        # BOOKMARKS THE SHOW OR MOVIE
        elif whatNext.lower() == 'd':
            if show in bookmarklist:
                print('\nThis show is already bookmarked')
            else:
                bookmarklist.append(show)
                print('\nThis show is now BOOKMARKED')



        # DELETES THE SHOW OR MOVIE
        elif whatNext.lower() == 'e':
            with open(self.bookmarktxt,'r') as f:
                bookmarklist = [line.strip() for line in f]
            if show in bookmarklist:
                print('\nIt\'s here')
                bookmarklist.remove(bookmarklist[bookmarklist.index(show)])
                print (bookmarklist)

            print('\nDeleting \'%s\'...') %(show)
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
            print('[-]This show has been deleted')
        else:
            print('The previous input was invalid.')



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
                showAbove = input("\nIs the result you were looking for listed above?: ").lower()
                if showAbove == 'yes':
                    whatNum = int(input("Enter the integer of the show: "))
                    if whatNum <= (len(rankinglist) + len(mightShow)):
                        whatNum -= 1
                        if whatNum >= len(rankinglist):
                            showfound = mightShow[whatNum-len(rankinglist)]
                            self.showOptions(showfound)
                        else:
                            showfound = rankinglist[whatNum]
                            self.showOptions(showfound)
                    else:
                        print('[!] Error: The number (%d) entered is out of index.') %(whatNum)
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
            print("\nTop Results")
            print('-'*70)
            print("{:<8}{}\n".format("RANK","NAME"))

            if len(rankinglist) > 0:
                for z in range(len(rankinglist)):
                    print("{} \t{}".format(z+1, rankinglist[z])) 
            print ('')
        
        # PRINTS OUT THE OTHER RESULTS
        if len(otherlist) > 0:
            print("\nOther Results")
            print (dash)
            print("{:<8}{}\n".format("RANK","NAME"))
            for y in range(len(otherlist)):
                print("{} \t{}".format(y+len(rankinglist)+1, otherlist[y])) 
        if len(otherlist) == 0 and len(rankinglist) == 0:
            print('\nNo results have been found in the database')

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
                print('\n[!] Error: String Similarity Failed!')
        
    
    # FUNCTION RESPONSIBLE OF CREATING FOLDER DIRECTORY
    def newDir(self,show,local=False):
        # print("This is the show before it goes to slashes: " + show)
        # show = show.decode('utf-8')
        # print ("This is the media name: {}".format(show))
        show = self.replacingSlashes(show)
        # print("This is the show after replacingSlashes: {}".format(show))
        # print show
        folderloc = (self.showsfolder) if searchtools.isShow is True else (self.moviesfolder)
        folderloc = os.path.join(folderloc,show)

        # print("This is the location of the folder: {}".format(folderloc))
        os.mkdir(folderloc)
        os.mkdir(os.path.join(folderloc,"Content"))


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
        print('Because this is a show created locally. We need to add some details to the show')
        print('Below are things that you need to edit manually: \n{}\n{}').format("cover.jg","overview (edit in deails.txt)")
        seasonAmount = input("\nEnter the amount of seasons this show has: ")
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
                # list_results.append([((search.results[x])['name']).decode('utf-8'), search.results[x]['id']])
                list_results.append([((search.results[x])['name']), search.results[x]['id']])

            return list_results

    # FUNCTION RETURNS LIST OF MOVIES FOUND IN TMDB SEARCH
    def tmdbMovieResults(self,movie):
        tmdb.API_KEY = searchtools.api
        search = tmdb.Search()
        reponse = search.movie(query=movie)
        list_results = []
        if len(search.results)>0:
            for x in range(len(search.results)):
                # print (search.results[x]['title'])
                list_results.append([((search.results[x])['title']), search.results[x]['id']])
            return list_results

    # FUNCTION RESPONSIBLE DECIDING WHICH NAME WILL BE USED FOR DIRECTORY
    def likeToAdd(self,show):
        addShow = input("Would you like to add \'%s\'?: " % show)
        if addShow.lower() == 'yes':


            print ('')
            print('[1] Keep the original name (local):\t%s' % show)
            print('[2] Get a title case name (local):\t%s' % self.grammarCheck(show))

            foundshows = self.tmdbShowResults(show) if searchtools.isShow else self.tmdbMovieResults(show)

            if foundshows != None : 
                whatisit = "show" if searchtools.isShow else "movie"
                print('[3] Closest real {}(api):\t\t{}'.format(whatisit,foundshows[0][0]))
                if len(foundshows) > 1 : print('\nMore')


            else: print('\n\n[!] Error: This show was not found in MovieDB database. Maybe try and re-spell')

            

            titleChoice = input("\nChoose one of the above options: ")

            if (titleChoice == 'more') and (len(foundshows) > 1):
                print ('')
                for x in range(1,len(foundshows)-1):
                    print("[{}]\t{}").format(3+x,foundshows[x][0])
                enterabove = int(input("\nChoose one of the above options (including 1-3): "))

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
                print('That option is out of range')

    # FUNCTION CHECKS TO SEE IF THE DIRECTORY IS PRE-EXISTING
    def exists(self,show):
        medialist = [item.lower() for item in self.getMediaList()]
        if show.lower() in medialist: 
            print('\n[!] Error: The show is already in the database')
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
        showpath = (os.path.join(self.showsfolder,show)) if searchtools.isShow is True else (os.path.join(self.moviesfolder,show))

        posterBase = 'https://image.tmdb.org/t/p/w500'
        start = time.time()

        if len(search.results) > 0:
            topresult = search.results[0]
           
            release_date = (topresult["first_air_date"] if searchtools.isShow else topresult["release_date"])
            listforJson = []
            listforJson.append(["overview",topresult['overview']])
            listforJson.append(["poster_path",topresult["poster_path"]])
            listforJson.append(["release_date", release_date])
            listforJson.append(["language",topresult["original_language"]])
            listforJson.append(["id",topresult['id']])
            listforJson.append(["locally_made",False])

            jsontext = self.jsonFormat(listforJson)
            directory = os.path.join(showpath,"details.json")
            # print('This is the current showpath: {}').format(showpath)
            # print('This is the projected JSON dir: {}').format(directory)

            with open(os.path.join(showpath,"details.json"),"w") as f:
                sometext = json.dumps(jsontext,indent=4)
                f.write(sometext)
                f.close()






            
            if topresult["poster_path"] is None:
                print('%s contained None') %(show)

            posterLink = posterBase + topresult["poster_path"]

            if os.path.isdir(showpath) == True:
                if os.path.exists(os.path.join(showpath,"cover.jpg")) == True:
                    print('\'%s\' already has a picture') %(show)

                else:
                    
                    context = ssl._create_unverified_context()
                    imgDownload = urlopen(posterLink, context=context)

                    imgfile = open(os.path.join(showpath,"cover.jpg"),'wb')
                    imgfile.write(imgDownload.read())
                    imgfile.close()
                    if searchtools.isShow is False: print('[+] {} retreived'.format(show))

                    if searchtools.isShow is True:
                        url = "https://api.themoviedb.org/3/tv/%d?api_key=%s&language=en-US" % (topresult["id"],api)
                        payload = "{}"
                        json_data = requests.get(url).json()

                        num_of_seasons = json_data['number_of_seasons'] 
                        self.addEpisodes(show,topresult["id"],showpath,num_of_seasons)

                        print('\n[+] {} retreived'.format(show))
                        

                        currentTime = time.strftime("%c")
                        logString = "{} \t[NEW SHOW] {} ({} seasons)\n".format(currentTime, show, num_of_seasons)
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
                        
                    end = time.time()
                    print('It took {:0.2f} seconds to add this directory'.format(end-start))
                    
            else:
                print('%s path doesn\'t exist') %(show)
       
    # FUNCTION CALLED CREATE DIRECTORIES OF EACH EPISODE IN EPISODELIST FUNCTION
    def addEpisodes(self,show,show_id,showpath,total_seasons):
       
        logger = Logger()

        options = Options()
        # Cant run chrome headless if you have extensions you want to add
        options.headless = True
        # options.add_extension(r"C:\Users\haust\Desktop\uBlock-Origin_v1.17.4.crx")
        driver = webdriver.Chrome(r"F:\Program Files (x86)\Google\Chrome\Application\chromedriver",chrome_options=options)
            
         # driver.set_window_position(-10000,0) # Remove this line if you want to see whats happening
            # ONLY NEEDED WHEN YOU WANT TO VIEW DOWNLOAD PAGE
            # SIGNING INTO OTAKU STREAM
            # driver.get('https://otakustream.tv/user/login/')
            # driver.find_element_by_id("user_login").send_keys(config.otaku_login)
            # driver.find_element_by_id("user_pass").send_keys(config.otaku_pass)
            # driver.find_element_by_id("wp-submit").click()
            # find_all = False
        totalEp = self.totalNumOfEpisodes(show_id,total_seasons)
        print ("This is the total number of episodes: {}".format(totalEp))




        # NEED TO JUST GRAB THE RELEASE DATE SO WE GOING TO GRAB THAT FROM THE FIRST SEASON
        epdetails,season_release_date = self.episodeList(1,show_id,losteps=False)
        season_release_date = (season_release_date.split("-"))[0]
        search = "{} {}".format(show,season_release_date)

        # print("\n\nThis is the search: {}".format(search))
        # print("There are \'{}\' episodes in Season {}".format(len(epdetails),seasonNum))


        otaku_results,find_all = otakustream.otakuLink(search,len(epdetails),season_release_date, totalEp)


        if (find_all == True):
            print("\n\nThis is the search: {}".format(search))
            # print ('THIS IS THE FIRST LOOP')
            count = 1
            for x in range(1,total_seasons+1):
                newSeason = "Season {}".format(x)
                seasonpath = os.path.join(showpath,"Content",newSeason)
                os.mkdir(os.path.normpath(seasonpath))
                epdetails,season_release_date = self.episodeList(x,show_id,losteps=False)
                print("\nThere are {} episodes in Season {}".format(len(epdetails), x))
                for z in range(len(epdetails)):
                    base_episode_url = "{}episode-{}".format(otaku_results,count)
                    print("This is the episode url: {}".format(base_episode_url))
                    count+=1

        else:
            # print ('THIS IS THE SECOND LOOP')
            
            for x in range(1,total_seasons+1):
                # Pulls the episode name and overview
                epdetails,season_release_date = self.episodeList(x,show_id,losteps=False)
                season_release_date = (season_release_date.split("-"))[0]

                if x == 1:
                    search = "{} {}".format(show, season_release_date)
                else:
                    search = "{} Season {} {}".format(show,x,season_release_date)
                # print("\n\nThis is the search: {}".format(search))
                # print ("THIS IS BEFORE OTAKU LINK")
                otaku_results,find_all2 = otakustream.otakuLink(search,len(epdetails),season_release_date, totalEp)

                print ("This is otaku_results: {}".format(otaku_results))
                if otaku_results is not None:

                    newSeason = "Season {}".format(x)
                    seasonpath = os.path.join(showpath,"Content",newSeason)
                    os.mkdir(os.path.normpath(seasonpath))
                    for z in range(len(epdetails)):
                        base_episode_url = "{}episode-{}".format(otaku_results,z+1)
                        print("This is the episode url: {}".format(base_episode_url))
                        ep_name = epdetails[z][0]
                        ep_name = self.replacingSlashes(ep_name)
                        ep_over = (epdetails[z][1]).decode('UTF-8')
                        # ep_link = otakustream.main(driver,show,x+1,otaku_results)

                        

                        newepfolder = os.path.join(seasonpath,ep_name)
                        newoverview = os.path.join(newepfolder,"overview.txt")
                        # neweplink = os.path.join(newepfolder,"WATCH.bat")

                        try:
                            os.mkdir(newepfolder)
                            # THIS LINE IS FOR SAVING THE LINK IN BAT FILE 
                            # if ep_link is not None: logger.writeLog(neweplink,message=ep_link,overview=True)
                            logger.writeLog(newoverview,message=ep_over,overview=True)

                        except:
                            LOG_MESSAGE = "\n\nError: Adding \'{}\' \nSUPPOSED FILEPATH: \'{}".format(ep_name, newepfolder)
                            logger.writeLog(showlogfile,message=LOG_MESSAGE)
                            continue
               
                    
        driver.close()






    def replacingSlashes(self,name):
        # print (name)
        try:
            name = list(name)
            forbid_characters = ['/','\\']
            other_chara = [">","<","\"","?","*",":"]

            for x in range(len(name)):
                if name[x] in forbid_characters:
                    name[x] = "&"
                elif name[x] in other_chara:
                    name[x] = ""
        except:
            print('Error changing name')
        finally:
            # print (name)
            name = "".join([str(i) for i in name])
            # print (name)
            return name
    # FUNCTION GOES THROUGH TMDB API TO GET EPISODE NAMES AND RETURNS A LIST OF FORMATTED EPISODE NAMES
    def episodeList(self,seasonNum,show_id,losteps=True):
        api = searchtools.api
        url = "https://api.themoviedb.org/3/tv/{}/season/{}?api_key={}&language=en-US".format(show_id,seasonNum,api)
            
        eplist = []
        resp = requests.get(url)
        json_data = requests.get(url).json()

        season_release_date = json_data["air_date"]

        for episode in json_data["episodes"]:

            epnum = int(episode["episode_number"])
            # epname = episode["name"].encode('utf-8')
            epname = episode["name"]

            if epnum < 10: epnum = "0"+str(epnum)


            #WANT TO CHANGE THIS TO HAVE ACTUAL FORMATING AND NOT HAVING TO ADD 0 IN FRONT OF NUMBERMU
            filename = "E{} - {}".format(epnum,epname)

            if losteps == False: eplist.append([filename,episode["overview"].encode('utf-8')])
            else: eplist.append(filename)

        return eplist,season_release_date

    # CHECKS A GIVEN LIST TO MAKE SURE THERE ARE NO FILES THAT SHOULDN'T BE THERE
    def forbiddenFiles(self, list_taken):
        newlist = list(list_taken)
    
        for file in newlist:
            if (file.startswith(".") or (file == '[BOOKMARKED SHOWS].txt') or (file == '[BOOKMARKED MOVIES].txt')): 
                newlist.remove(newlist[newlist.index(file)])            
        return newlist

    def totalNumOfEpisodes(self,show_id, how_many_seasons):
        api = searchtools.api
       
        totalEp = 0
        for x in range(1,how_many_seasons+1):
            url = "https://api.themoviedb.org/3/tv/{}/season/{}?api_key={}&language=en-US".format(show_id,x,api)
            resp = requests.get(url)
            json_data = requests.get(url).json()

            totalEp+= len(json_data["episodes"])
        return totalEp

    # FUNCTION THAT RECOGNIZES THE DIFFERENT ELEMENTS OF A FORMATTED EPISODE NAME
    def breakEpName(self, epname):
        indentifier = re.findall(r'E(\d+) - (.*)',epname)
        epnum = indentifier[0][0]
        epbane = indentifier[0][1]
        return epnum, epname

    # FUNCTION THAT DISPLAYS TABLE OF MISSING EPISODES
    def missingTable(self,season,epnames,firstime=True):
        if firstime is True:
            print("\n{:<10} {:<10} {}".format("Season","EP #", "EP. NAME"))
            print(' ')
        
        for x in range(len(epnames)):
            indentifier = re.findall(r'E(\d+) - (.*)',epnames[x])
            epnum = indentifier[0][0]
            epname = indentifier[0][1]
            if x == 0:
                print("{:<10} {:<10} {}".format(season,epnum, epname))
            else:
                 print("{:<10} {:<10} {}".format(" ",epnum, epname))

            # print('-')*60
        print('-'*70)

            