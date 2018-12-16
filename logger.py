
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
            while True:
                try:
                    f = open(filepath,'w',)
                    f.write(message)
                except UnicodeDecodeError:
                    message = message.decode('utf-8')
                except UnicodeEncodeError:
                    message = message.encode('utf-8')
                finally:
                    f.write(message)
                    break

            
        else:
            t = open(filepath,'a')
            t.write(message)
            t.close()

