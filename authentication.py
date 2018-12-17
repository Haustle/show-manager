import os
from searchtools import searchtools
class authentication(object):
    def __init__(self,root_folder):
        self.root_folder = root_folder
        self.showsfolder = root_folder + "shows/"
        self.showtxt = root_folder + "show_list.txt"
        self.bookmarktxt = self.showsfolder + "[BOOKMARKED SHOWS].txt"
        self.logtxt = root_folder + "log.txt"

    def main(self):
        dirList = self.listOfFolders
    def dirExists(self,dir):
        return True if os.isdir(dir) else False

    def listOfFolders(self):
        return [self.root_folder, self.showsfolder, self.showtxt, self.logtxt]


projectFolder = os.getcwd()+"/"
a = authentication(projectFolder)
print a.root_folder
instance_variables = a.__dict__.keys()
s = searchtools(None,projectFolder)
print type(s)
# for dir in instance_variables:
#     print s.(dir)
