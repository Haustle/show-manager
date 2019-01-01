import webbrowser ,requests, config, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome impor
from bs4 import BeautifulSoup
import time

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

def chooseDownload(download_page_link):

    options = Options()
    options.headless = True

    driver = webdriver.Chrome('F:\Program Files (x86)\Google\Chrome\Application\chromedriver',chrome_options=options)

    driver.get('https://otakustream.tv/user/login/')
    driver.find_element_by_id("user_login").send_keys(config.otaku_login)
    driver.find_element_by_id("user_pass").send_keys(config.otaku_pass)
    driver.find_element_by_id("wp-submit").click()

    time.sleep(1)
    driver.get('https://otakustream.tv/user/download/?episode_id=5385')
    time.sleep(1)

    page = (driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")).encode("utf-8")
    soup = BeautifulSoup(page,'html.parser')
    server_links = soup.find_all('table', class_="table table-striped table-hover")
    tds = server_links[0].find_all("td")
    link = None
    for x in range (len(tds)):
        currentd = tds[x].text
        if currentd == 'Openload': link = tds[x+1].text

    return link



def openloadMP4(link):
    chrome_options = Options()
    chrome_options.add_extension('C:\Users\haust\Desktop\uBlock-Origin_v1.17.4.crx')
    # chrome_options.add_argument('window-size=1920x1080')
    chrome_options.headless = False

    driver = webdriver.Chrome('F:\Program Files (x86)\Google\Chrome\Application\chromedriver', chrome_options=chrome_options)
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
    driver.close()
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


def main():
    vlc_dir = 'C:\Program Files\VideoLAN\VLC\\'
    show_link = otakuLink("Your lie in april")
    server_links = otakuDownloadPage(show_link,2)
    openloadLink = chooseDownload(server_links)
    print 'hello'
    mp4 = openloadMP4(openloadLink)
    print mp4
    os.system('cd {}'.format(vlc_dir))
    os.system('vlc.exe {}'.format(mp4))
    


main()