# import os.path
import os
import searchtools


# Purpose of this class is to run and make sure all the required files are in the projcted places
# Want to have one for shows so when adding the show folders are set up correctly and able to function
# properly later on


class authentication(object):

    def __init__(self,root_folder):

        self.root_folder = root_folder
        self.showsfolder = root_folder+"shows/"
        self.moviesfolder = root_folder+"movies/"

    def mainFiles(self):
        dirList = (searchtools.searchtools(self.root_folder)).__dict__.values()

        missing = []
        for dir in dirList:
            exists = os.path.exists(dir)

            if os.path.exists(dir) is False:
                # print("Dir exists: {}\n").format("Missing", dir)
                filename = (dir.split(os.sep))
                lookingfor = filename[-1]
                if lookingfor == '':
                    lookingfor = filename[-2]
                

                if self.isTextDoc(lookingfor) is True: 
                    f = open(dir,'w')
                    f.close()
                    lookingfor += " > text file"
                    
                    
                else:
                    os.mkdir(dir)
                    lookingfor+= " > folder"
                    

                missing.append(lookingfor)
                continue

            else:
                if dirList[-1] == dir: pass
                else: continue

            if len(missing) != 0:
                missingstr = "Number of missing files: {}\n".format(len(missing))
                for x in range(len(missing)):
                    missingstr += "\n[+] {}".format(missing[x])
                return missingstr
            

    def isTextDoc(self,dir):
        try:
            broke = dir.split(".")
            extension = broke[-1]
            if extension == 'txt': return True
            return False
        except:
            print 'Error: Something went wrong trying to identify the directory'

    def showFiles(self, isShow=True):
        decidepath = self.showsfolder if isShow else self.moviesfolder
        for name in os.listdir(decidepath):
            path = self.showsfolder+name if isShow else self.moviesfolder+name

            if os.path.isdir(path):
                pathlist = os.listdir(path)

                official_path = ["Content","cover.jpg","details.json"]
                if isShow: official_path.append("{} log.txt".format(name))

                path_compare = list( set(pathlist) ^ set(official_path))
                if len(path_compare) != 0:
                    print("\n{} (missing files)").format(name)
                    print '-'*80
                    for x in range(1,len(path_compare)+1):

                        reason = "MISSING" if path_compare[x-1] not in pathlist else "RANDOM FILE"
                        print "{:<5} {:<20} {:>50}".format(x,path_compare[x-1],reason)
                    
