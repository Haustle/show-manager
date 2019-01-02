import webbrowser
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

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
    
    result = requests.get(download_page_link)
    page = result.text
    soup = BeautifulSoup(page,'html.parser')
    server_links = soup.find_all('table', class_="table table-striped table-hover")
    print server_links

    
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
    
    # print 'This is the final url: {}'.format(final_url)
    webbrowser.open(final_url)
    return final_url




def main():
    show_link = otakuLink("Your lie in april")
    server_links = otakuDownloadPage(show_link,5)
    chooseDownload(server_links)


main()