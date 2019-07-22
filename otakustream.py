import webbrowser ,requests, config, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome impor
from bs4 import BeautifulSoup
import time

global driver
driver = None

global chrome_options 
chrome_options = None





# NEED TO GO BACK AND SCAREP FOR SPAN > EP-NO
# NEED TO CHECK FOR THE RELEASE DATE OF EACH SEASON
# SO I CAN SEARCH
#   



def otakuLink(original_name,tmdb_season_ep_count,release_date,totalEp):
    tmdb_season_ep_count = int(tmdb_season_ep_count)

    name = "+".join(original_name.split(" "))
    base_url = "https://www.otakustream.tv/?s={}".format(name)

    result = requests.get(base_url)
    page = result.text
    soup = BeautifulSoup(page,'html.parser')
    
    
    shows = soup.find_all('div', class_="ep-box")
    link_to_show = None
    all_ep = False
    if len(shows) > 0:
        for x in range(len(shows)):
            ep_count = shows[x].find_all('span', class_="ep-no")
            if len(ep_count) == 1:
                ep_count = ((ep_count[0].text).split(" "))[-1]
                if ep_count.isdigit():
                    if ((int(ep_count) == totalEp) or int(ep_count) == (tmdb_season_ep_count)) or ((int(ep_count)+1) == tmdb_season_ep_count) or ((int(ep_count)-1) == tmdb_season_ep_count):
                        if (int(ep_count) == totalEp): 
                            all_ep = True
                        links = shows[x].find_all('a', href=True)
                        link_to_show = links[0]['href']

                        # print (link_to_show)
                        premierbox = shows[x].find_all('div', class_= "cch-content")
                        for y in range(len(premierbox)):
                            ps = premierbox[y].find_all('p', class_= None)
                            for p in ps:
                                allATagss = p.find_all('a', class_= None)
                                for x in range(len(allATagss)):
                                    if (allATagss[x].text) == str(release_date):
                                        print ("\n\n\'{}\' was found on otakustream.tv".format(original_name))
                                        
                                        return link_to_show, all_ep





                    
                                
            if (x+1) != len(shows): continue
                
    # print("We are returning link: {} \nall_ep: {}".format(link_to_show, all_ep))
    return link_to_show, all_ep

def chooseDownload(driver,download_page_link):



    # time.sleep(1)
    # print "\nThis is the download_page_link: {}\n".format(download_page_link)
    driver.get(download_page_link)
    page = (driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")).encode("utf-8")
    soup = BeautifulSoup(page,'html.parser')
    # print "This is the start of soup: {}".format(soup)
    server_links = soup.find_all('table', class_="table table-striped table-hover")
    # print "This is the list to server_links: {}".format(server_links)
    tds = server_links[0].find_all("td")
    link = None
    for x in range (len(tds)):
        currentd = tds[x].text
        if currentd == 'Openload': link = tds[x+1].text

    return link



def openloadMP4(driver,link):
    if link is not None:
        driver.get(link)
        for x in range(3):
            # print 'This is run through number: {}'.format(x)
            try:
                driver.find_element_by_id("videooverlay").click()
                # print 'I just tried to click'
            except:
                continue
                # print 'The click failed'
            finally:
                time.sleep(1)
        try:
            page = (driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")).encode("utf-8")
            soup = BeautifulSoup(page,'html.parser')
            instantlink = soup.find_all('video', class_="vjs-tech")
            # driver.close()
            mp4Link = instantlink[0]['src']
            link = 'https://openload.co{}'.format(mp4Link)
        except:
            link = None
        finally:
            return link

def otakuDownloadPage(show_link,ep_number):
    ep_string = "episode-{}/".format(str(ep_number))
    base_url = show_link + ep_string
    result = requests.get(base_url)
    page = result.text
    soup = BeautifulSoup(page,'html.parser')
    download_links = soup.find_all('a', title="Download episode")
    downloadlink = download_links[0]['href']
    base_url = 'http://www.otakustream.tv/user'
    final_url = base_url+downloadlink
    
    return final_url


def main(driver_import,anime_name,ep_num,show_link):
    # print ('We are trying to add the episodes')
    
    driver = driver_import # import this into searchtools and run it before hand    

    if show_link is not None:
        server_links = otakuDownloadPage(show_link,ep_num)
        time.sleep(1)
        openloadLink = chooseDownload(driver,server_links)
        time.sleep(1)
        mp4 = openloadMP4(driver,openloadLink)
        if mp4 != None:
            bat_file = None
            vlc_dir = 'C:\Program Files\VideoLAN\VLC'
            if os.path.isdir(vlc_dir) == False:
                vlc_dir = 'C:\Program Files (x86)\VideoLAN\VLC'
            bat_file = 'cd {}'.format(vlc_dir)
            bat_file += "\nvlc.exe {}".format(mp4)
            return bat_file
            
    return None
    
