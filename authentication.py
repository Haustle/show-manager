import os.path
import os
from searchtools import searchtools
class authentication(object):
    def __init__(self,root_folder):
        self.dirList = (searchtools(root_folder)).__dict__.values()

    def main(self):

        for dir in self.dirList:
            exists = os.path.exists(dir)
            
                
            if os.path.exists(dir) is False:
                print("Dir exists: {}\n").format("Missing", dir)
                filename = (dir.split("/"))[-1]

                if self.isText(filename) is True: 
                    f = open(dir,'w')
                    f.close()
                    
                else:
                    os.mkdir(dir)
                    
                print("\t[!]Missing \'{}\' --> [+]Added \'{}\'").format(filename,filename)
                print("\tFilepath: {}").format(dir)
                print ''
            

    def isText(self,dir):
        try:
            broke = dir.split(".")
            extension = broke[-1]
            if extension == 'txt': return True
            return False
        except:
            print 'Error: Something went wrong trying to identify the directory'



projectFolder = os.getcwd()+"/"
# a = authentication(projectFolder)

authentication(projectFolder).main()

