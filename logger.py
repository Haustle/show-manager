
class Logger(object):

    def getSplitLastLine(self,textfile):

        l = open(textfile,"r")
        lastline = l.readlines()
        l.close()
        lastline = lastline[len(lastline)-1]
        brokenLastLine = lastline.split(" ")
        return brokenLastLine
    
    def writeLog(self,filepath, message=None, overview=False):

        if overview is True: 
            try:
                f = open(filepath,'w',)
                f.write(message)
            except Exception as e:
                print 'Error: There was an error when trying to write into the file'
                print str(e)
            finally:
                 f.close()
            
        else:
            t = open(filepath,'a')
            t.write(message)
            t.close()


