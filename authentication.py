# import os.path
import os
from searchtools import searchtools


# Purpose of this class is to run and make sure all the required files are in the projcted places
# Want to have one for shows so when adding the show folders are set up correctly and able to function
# properly later on


class authentication(object):
    def __init__(self,root_folder):
        self.dirList = (searchtools(root_folder)).__dict__.values()

    def main(self):

        missing = []
        for dir in self.dirList:
            exists = os.path.exists(dir)

            if os.path.exists(dir) is False:
                # print("Dir exists: {}\n").format("Missing", dir)
                filename = (dir.split("/"))
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
                if self.dirList[-1] == dir: pass
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



