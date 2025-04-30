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
    #link from which data is downloaded
    url = "https://images-api.nasa.gov/search";

    #parameters
    params_q = {
        'q': qeury
    };

    #intallize the data
    response = requests.get(url, params=params_q);

    #check if data downloading the data was accomplished with success
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'nie udalo sie poprac danych, kod błedu {response.status_code}')


#application class
class Application(Frame):
    #bool variable of the main loop
    running = True;
    #the main window
    window = 0;
    Manager = 0;
    #width and height of the main window
    WIDTH, HEIGHT = 0, 0;
    #images and titles taken from url
    chosenItems = [];

    #initialize class
    def __init__(self, width, height):
        self.WIDTH, self.HEIGHT = width, height;
        #initialize python
        pygame.init();
        pygame.font.init();
        comicSans = pygame.font.SysFont('Comic Sans MS', 30);

        #create the main window
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT));
        self.running = True;

        self.Manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT));

        #text
        textSurface = comicSans.render('search:', False, (255,255,255));
        textInput = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((550,0), (400, 50)), manager=self.Manager, 
                                                        object_id = "#query")

        #main loop
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
        try:
            data = fetch_nasa_images(text);
            # print(data)
            items = data.get('collection', {}).get('items', []);
            # print(items)

            if not items:
                print("Brak wyników wyszukiwania");
                return # slowko skoku, ktore konczy dzialanie metody/funkcji

            #Create variable of row index and collumn index
            r_index = 0;
            c_index = 0;
            print("="*40)
            #index variable
            i = 0;
            #the loop searches for images and displayes them
            for item in items[:5]:
                i+=1;
                #check if it's time to increase the row index by one
                if(c_index >= 3):
                    r_index +=1;
                    c_index = 0;
                x, y = c_index*220, 200 + r_index*220;

                item_data = item.get('data',[]);

                #create virables of images and title
                photo = '';
                small_photo = '';
                title = '';

                #check if 'data' exists
                if item_data:
                    title = item_data[0].get('title', "brak tytulu");
                    
                links = item.get('links', [])
                if links:
                    href = links[0].get('href', 'brak linku');
                    pil_image = requests.get(href).content;
                    
                    #original and smaller version of the image
                    photo = io.BytesIO(pil_image);
                    small_photo = pygame.image.load(photo);
                    
                    #resize the small photo if it's too large
                    if(small_photo.size[0] > 200):
                        small_photo = pygame.transform.scale(small_photo, (200 ,small_photo.size[1]));
                    if(small_photo.size[1] > 200):
                        small_photo = pygame.transform.scale(small_photo, (small_photo.size[0], 200));
                    #Create images as buttons
                    imageButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x,y),(200,200)), text="", manager=self.Manager, object_id=f"{len(self.chosenItems)}");
                    #put data to chosen items variable.
                    img = (small_photo, pil_image, title, imageButton);
                    self.chosenItems.append(img)
                    #show images while loading
                    self.window.blit(small_photo, (x, y));

                    #Print links to images in console
                    print(href);
                    print("-"*40)
                #update UI manager to make sure images display while loading.
                UI_REFRESH_RATE = pygame.time.Clock().tick(60)/1000;
                self.Manager.update(UI_REFRESH_RATE);
                pygame.display.update();

                #increase a collumn index by one
                c_index+=1;
        #If there's an error it prints "Wystapil blad" in the console
        except Exception as e:
            print(f"Wystapil blad {e}");
    
    #creates a new window with a full sized image
    def ApearImage(self, item):
        #Create a new window using Tkinter (Pygame doesn's allow having two windows)
        newWindow = Tk();

        #convert image to make sure it works
        img = ImageTk.PhotoImage(Image.open(io.BytesIO(item[1])));
        #display image
        l_image = Label(newWindow, image=img);
        l_image.pack();
        #display tile of the image
        l_text = Label(newWindow, text=item[2]);
        l_text.pack();

        #main loop of the new window;
        newWindow.mainloop();      


def main():
    app = Application(1980, 1080);


if __name__ == "__main__":
    main();
