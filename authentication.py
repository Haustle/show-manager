import os.path
from searchtools import searchtools
class authentication(object):
    def __init__(self,root_folder):
        self.dirList = (searchtools(root_folder)).__dict__.values()

    def main(self):
        for dir in self.dirList:
            if os.path.exists(dir) is True: continue
            else:
                self.makeDir(path=dir)
            return False
        return True

        # return True
    def makeDir(self,path=dir):
        return True if os.isdir(dir) else False
    def isText(self,dir):
        pass
    def isFolder(self,dir):
        pass


projectFolder = os.getcwd()+"/"
a = authentication(projectFolder)

print a.main()

