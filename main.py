from os import link
from fastapi import FastAPI, Request, Response
from bs4 import BeautifulSoup
from fastapi.responses import HTMLResponse
import lxml
import requests
import json
import re
from requests_html import HTMLSession
import requests

def Filter(text: str):
    K = text.split(" ")
    K.remove(K[0])
    result = " ".join(K)
    return result
       
def get_search_results(query):  
        try:
            mangalink = f"http://kissmanga.nl/search?q={query}"
            response = requests.get(mangalink)
            response_html = response.text
            soup = BeautifulSoup(response_html, 'lxml')
            source_url = soup.findAll("div", {"class": "media-body"})
            res_search_list = []
            for links in source_url:
                a = links.find('a')
                title = a.find('h4').text
                mangaId = a['href']
                mangaid = mangaId.split("/").pop()
                res_search_list.append({"title":f"{title}","mangaid":f"{mangaid}"})           
            return res_search_list
        except requests.exceptions.ConnectionError:
            return {"status":"404", "reason":"Check the host's network Connection"}


def get_manga_details(mangaid):  
        try:
            mangalink = f"http://kissmanga.nl/manga/{mangaid}"
            response = requests.get(mangalink)
            plainText = response.text
            soup = BeautifulSoup(plainText, "lxml")
            mangainfo = soup.find("div", {"class": "media-body"})
            manga = soup.find("p", {"class": "description-update"}).text
            image = soup.find("div", {"class": "media-left cover-detail"})
            imageurl = image.find('img')['src']
            description = soup.find("div", {"class": "manga-content"}).p.text.strip()
            title = mangainfo.h1.text
            manSplit = manga.split("\n")
            genres = []          
            status = []
            alternative = []
            view = []
            author = []
            status = []
            for i in manSplit:
                if "Alternative" in i:
                    alternative.append(Filter(i.strip()))
                if "View" in i:
                    view.append(Filter(i.strip()))
                if "Author(s)" in i:       
                    author.append(Filter(i.strip()[:-1]))
                if "Status" in i:               
                    status.append(Filter(i.strip()))
                if "\r" in i:
                    genres.append(i.strip()[:-1])
                genrek = ", ".join(genres)
                statusk = ", ".join(status)
                alternativek = ", ".join(alternative)
                viewk = ", ".join(view)
                authork = ", ".join(author)
                res_search_list = {"title":f"{title}","description":f"{description}","image":f"{imageurl}","status":f"{statusk}","view":f"{viewk}","author":f"{authork}","alternative":f"{alternativek}","genre":f"{genrek}"}          
            return res_search_list
        except AttributeError:
            return "Wrong Mangaid"
        except requests.exceptions.ConnectionError:
            return {"status":"404", "reason":"Check the host's network Connection"}


def get_manga_chapter(mangaid, chapNumber):  
        try:
            mangalink = f"http://kissmanga.nl/{mangaid}-chapter-{chapNumber}"
            response = requests.get(mangalink)
            response_html = response.text
            soup = BeautifulSoup(response_html, 'lxml')
            source_url = soup.find("p", id="arraydata")
            totalPages = source_url.text.split(",")
            res_search_list = {"totalPages":f"{totalPages}"}
            return res_search_list
        except AttributeError:
            return "Invalid Mangaid or chapter number"
        except requests.exceptions.ConnectionError:
            return {"status":"404", "reason":"Check the host's network Connection"}
       
def read_html(lol):  # returns list of image links of pages of full chapter [imglink1, imglink2, full chapter]
        try:
            url = f"{lol}"
            response = requests.get(url)
            response_html = response.text
            soup = BeautifulSoup(response_html, 'lxml')
            chapter_pages = soup.find("p", id="arraydata")
            pages = chapter_pages.text.split(",")
            return pages
        except AttributeError:
            return "Invalid Mangaid or chapter number"
        except requests.exceptions.ConnectionError:
            return "Check the host's network Connection"
       



app = FastAPI()
@app.get('/')
def root(request: Request):
    return {"root": request.url.hostname}

@app.get('/search')
async def search(q):
    manga_search = get_search_results(query=q)
    return manga_search

@app.get('/chatbot')
async def chatbot(message: str):
    data = kuki_request(message)
    return {'message': data}



@app.get('/readmanga')
async def read(manga, chapter):
    chapurl = f"http://kissmanga.nl/{manga}-chapter-{chapter}"
    chap = read_html(chapurl)
    x = '''<div class="mangaapi" style="background-color:black">'''
    for i in chap:
        x = f'''{x}
    <div class="image">
      <img src="{i}" style="width:100%"><br>
      <br>
    </div>
        '''
    return HTMLResponse(content=x, status_code=200)
    
    

@app.get('/details')
def manga_detail(id):
    manga_details = get_manga_details(mangaid=id)
    return manga_details


@app.get('/chapter')
def episode_link(id, ch):
    manga_chapter = get_manga_chapter(mangaid=id, chapNumber=ch)    
    return manga_chapter
