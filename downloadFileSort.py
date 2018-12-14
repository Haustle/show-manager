import re
import os
import searchtools


root_folder = "/Users/ty/Desktop/fsociety/py_programs/showBot/"
download_folder = root_folder+"showDownloads/"
showFolders = root_folder+"shows/"
folderlist = os.listdir(download_folder)

s = searchtools.searchtools(None,root_folder)

print ""
# torShowName = 'Mr.Robot.S04E099.HDTV.x264-d1abl01'
if len(folderlist) > 0:
    for file in folderlist:
        if (file != '.DS_Store') and (file != 'downloadMoveLog.txt'):
            # print file
            identifier = re.findall(r'S(\d+)E(\d+)', file)
            nameSplit = file.split(".")
            if len(identifier) == 1:
                if len(identifier[0]) == 2:
                    file_extension = nameSplit[-1]
                    print "File Extension : {}".format(file_extension)
                    season = int(identifier[0][0])
                    episodenum = int(identifier[0][1])

                    findPhrase = re.compile(r'S(\d+)E(\d+)')
                    find = findPhrase.search(file)
                    epDetails = find.group()
                    indexOf = nameSplit.index(epDetails)
                    show = " ".join(nameSplit[:indexOf])

                    matchlist = s.matchinglist(show)

                    if (show in folderlist) or (matchlist[0][1] > 0.5):
                        show = matchlist[0][0]
                        seasons = []
                        showfolder = showFolders+show

                        for folder in os.listdir(showfolder):
                            if folder.startswith("Season "): seasons.append(folder)

                        if season <= len(seasons):
                            print '\nNumber of seasons: {}'.format(len(seasons))
                            episodes = os.listdir(showfolder+"/Season "+str(season))

                            if episodenum <= len(episodes):
                                episodefolder = ""
                                needEp = "E{}\t".format(episodenum) 
    
                                # print 'Wanted Episode : {}'.format(needEp)
                                for episode in episodes:
                                    # print 'hello'
                                    
                                    brokenEp = episode.split(" ")
                                    # print brokenEp
                                    if needEp in brokenEp:
                                        # print 'wtf'
                                        episodefolder = episode
                                        print '-'*45
                                        print 'Found Alleged Episode : {}'.format(episode)
                                        print '-'*45

                                    
                                filename = "{} - S{}E{}.{}".format(show,season,episodenum,file_extension)
                                # print 'This is the filename : {}'.format(filename)

                                folderdir = "{}/Season {}/{}/{}".format(show,season,episodefolder,filename)
                                print 'This is folderdir: {}'.format(folderdir)

                                downloadLocation = download_folder+file
                                moveTo = showFolders+folderdir
                                print 'This is moveTo: {}'.format(moveTo)

                                try:
                                    os.rename((downloadLocation),(moveTo))
                                except:
                                    print 'This directory doesn\'t exist'
                            else:
                                print '\'Episode {}\' doesn\'t exist(?). There are only {}'.format(episode,len(episodes))
                        else:
                            print '\'Season {}\' doesn\'t exist(?). There are only {}'.format(season,len(seasons))


                else:
                    
                    print 'The show file trying to be moved is not proper Title Format'
                    print 'Show.S0E0.mp4'


print ""