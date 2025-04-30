import sys
import pygame
import pygame_gui
from tkinter import * 
from tkinter.ttk import * 
import pygame_gui.elements.ui_image
import pygame_gui.ui_manager
import requests
import json
import io
from PIL import ImageTk, Image

def fetch_nasa_images(qeury):
    #link z którego są pobierane dane
    url = "https://images-api.nasa.gov/search";

    #parametry
    params_q = {
        'q': qeury
    };

    #popierz dane
    response = requests.get(url, params=params_q);

    #sprawdź czy pobranie danych działa
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'nie udalo sie poprac danych, kod błedu {response.status_code}')


#applikacja
class Application(Frame):
    #utworzenie zmiennej
    running = True;
    #the main window
    window = 0;
    Manager = 0;
    #width and height of the main window
    WIDTH, HEIGHT = 0, 0;

    chosenItems = [];

    #inicjalizacja klasy
    def __init__(self, width, height):
        self.WIDTH, self.HEIGHT = width, height;

        pygame.init();
        pygame.font.init();
        comicSans = pygame.font.SysFont('Comic Sans MS', 30);

        #utwórz okno
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT));
        self.running = True;

        self.Manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT));

        #text
        textSurface = comicSans.render('search:', False, (255,255,255));
        textInput = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((550,0), (400, 50)), manager=self.Manager, 
                                                        object_id = "#query")

        #Główna pętla
        while self.running:
            UI_REFRESH_RATE = pygame.time.Clock().tick(60)/1000;
            #events
            events = pygame.event.get()
            #event loop
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False;
                self.Manager.process_events(event);
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_object_id == "#query":
                    self.Search(event.text);
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    #print(self.chosenItems[int(event.ui_object_id)][2]);
                    self.ApearImage(self.chosenItems[int(event.ui_object_id)]);
            #make sure that buttons display correct image
            for image in self.chosenItems:
                image[3].set_image(image[0]);


            self.window.blit(textSurface, (400, 0));

            self.Manager.draw_ui(self.window);

            self.Manager.update(UI_REFRESH_RATE);
            pygame.display.update();
        pygame.quit();
    

    def Search(self, text):
        #utwórz następne okno
        
        try:
            data = fetch_nasa_images(text);
            # print(data)
            items = data.get('collection', {}).get('items', []);
            # print(items)

            if not items:
                print("Brak wyników wyszukiwania");
                return # slowko skoku, ktore konczy dzialanie metody/funkcji

            #utwórz zmienne kolumny i wierszy dla obrazów
            r = 0;
            c = 0;
            print("="*40)

            i = 0;
            #pętla która wyszukiwuje czy są obrazy
            for item in items[:5]:
                i+=1;
                #sprawdź czy to następny wiersz
                if(c >= 3):
                    r +=1;
                    c = 0;
                x, y = c*220, 200 + r*220;

                item_data = item.get('data',[]);

                #utwórz zmienne obrazów i tytółu elementu
                photo = '';
                small_photo = '';
                t = '';

                #sprawdź czy 'data' istnieje
                if item_data:
                    title = item_data[0].get('title', "brak tytulu");
                    t = title;
                    
                links = item.get('links', [])
                if links:
                    href = links[0].get('href', 'brak linku');
                    pil_image = requests.get(href).content;
                    
                    #większa i mniejsza wersja obrazu
                    
                    photo = io.BytesIO(pil_image);
                    small_photo = pygame.image.load(photo);
                    
                    #obraz jest zmniejszany gdy jest za duży
                    if(small_photo.size[0] > 200):
                        small_photo = pygame.transform.scale(small_photo, (200 ,small_photo.size[1]));
                    if(small_photo.size[1] > 200):
                        small_photo = pygame.transform.scale(small_photo, (small_photo.size[0], 200));
                    #Create images as buttons
                    imageButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x,y),(200,200)), text="", manager=self.Manager, object_id=f"{len(self.chosenItems)}");
                    #put data to chosen items variable.
                    img = (small_photo, photo, t, imageButton);
                    self.chosenItems.append(img)

                    
                    self.window.blit(small_photo, (x, y));

                    #wyświetla linki do obrazów
                    print(href);
                    print("-"*40)

                UI_REFRESH_RATE = pygame.time.Clock().tick(60)/1000;
                self.Manager.update(UI_REFRESH_RATE);
                pygame.display.update();

                #zwiększ kolumnę o jeden
                c+=1;
            for item in self.chosenItems:
                print(item[2]);

        #gdy nastąpi bład wyświetla się w konsoli "Wystapil blad"
        except Exception as e:
            print(f"Wystapil blad {e}");
    
    #pokacują się obrazy na osobnym oknie.
    def ApearImage(self, item):
        #Create a new window using Tkinter (Pygame doesn's allow having two windows)
        newWindow = Tk();

        img = ImageTk.PhotoImage(Image.open(item[1]));

        l_image = Label(newWindow, image=img);
        l_image.pack();

        newWindow.mainloop();      


def main():
    
    app = Application(1980, 1080);


if __name__ == "__main__":
    main();
