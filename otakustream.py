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
    link_to_show = ""
    if len(shows) > 0:
        for show in shows:
            links = show.find_all('a', href=True)
            link_to_show = links[0]['href']
            
            print "\'{}\' was found on otakustream.tv".format(original_name)
            return link_to_show

    else:
        
        return None

def videoLink(show_link,ep_number):
    ep_string = "episode-{}/".format(str(ep_number))
    # print ep_string
    base_url = show_link + ep_string

    result = requests.get(base_url)
    page = result.text

    soup = BeautifulSoup(page,'html.parser')
#     print soup
    idk = soup.find_all('div', id="video-wrap")
    print idk
 





videoLink(otakuLink("megalo box"),5)