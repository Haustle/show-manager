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

def otakuLink(original_name):

    name = "+".join(original_name.split(" "))
    base_url = "https://www.otakustream.tv/?s={}".format(name)

    result = requests.get(base_url)
    page = result.text
    soup = BeautifulSoup(page,'html.parser')
    
    
    shows = soup.find_all('div', class_="caption-category")
    link_to_show = None
    if len(shows) > 0:
        for show in shows:
            links = show.find_all('a', href=True)
            link_to_show = links[0]['href']
            
            print "\'{}\' was found on otakustream.tv".format(original_name)
            return link_to_show


    else:
        return None

def chooseDownload(driver,download_page_link):

    # print "This is download_page_link: {}".format(download_page_link)
    # print "This is the format of driver in choose download: {}".format(type(driver)) 
    # time.sleep(1)

    print "Session_id in choose download: {}".format(driver.session_id)
    print "_url from driver object in chosoedonw: {}".format(driver.command_executor._url)
    driver.get(download_page_link)

    # time.sleep(1)

    page = (driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")).encode("utf-8")
    soup = BeautifulSoup(page,'html.parser')
    server_links = soup.find_all('table', class_="table table-striped table-hover")
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

        page = (driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")).encode("utf-8")
        soup = BeautifulSoup(page,'html.parser')
        instantlink = soup.find_all('video', class_="vjs-tech")
        # driver.close()
        mp4Link = instantlink[0]['src']
        link = 'https://openload.co{}'.format(mp4Link)

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

def selenium_try():
   pass


def main(driver_import,anime_name,ep_num):
    # chrome_options.add_extension('C:\Users\haust\Desktop\uBlock-Origin_v1.17.4.crx')
    # chrome_options.headless = False
    
    # driver = webdriver.Chrome('F:\Program Files (x86)\Google\Chrome\Application\chromedriver', chrome_options=chrome_options)
    driver = driver_import
    # print "This is the format of driver in main: {}".format(type(driver))
    print "_url from driver object in main: {}".format(driver.command_executor._url)
    print "This is the session_id: {}".format(driver.session_id)

    show_link = otakuLink(anime_name)

    if show_link is not None:
        server_links = otakuDownloadPage(show_link,ep_num)
        openloadLink = chooseDownload(driver,server_links)

        mp4 = openloadMP4(driver,openloadLink)
        bat_file = None

        vlc_dir = 'C:\Program Files\VideoLAN\VLC'
        if os.path.isdir(vlc_dir) == False:
            vlc_dir = 'C:\Program Files (x86)\VideoLAN\VLC'
        bat_file = 'cd {}'.format(vlc_dir)
        bat_file += "\nvlc.exe {}".format(mp4)
        
    return bat_file
    
