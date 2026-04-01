from pathlib import Path
from random import randint
import pandas as pd
import glob
from nicegui import app, ui, native
from PIL import Image
import os, sys
import nicegui
import multiprocessing

multiprocessing.freeze_support()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

lookup_df = pd.read_csv(resource_path('countrylookup.csv'), encoding='latin1')

separator = "/" if os.name != 'nt' else "\\"

images = {}
for i, image_file in enumerate(glob.glob(resource_path('Flags/*.png'))):
    country_code = image_file.split(separator)[-1].split(".")[0].upper()
    country_name = lookup_df[lookup_df['Code'] == country_code]['Country'].iloc[0]
    images[i] = {'name': country_name, 'file': image_file}



#-------------------UI--------------------#

class GUI():
    def __init__(self):
        self.flag_image = ui.image()
        self.answer_label = ui.label(f'').classes('text-2xl text-green-500')
        self.answer_label.visible = False
        
        ui.dark_mode(True)
        ui.button('Show answer', on_click=lambda: self.true_visibility())
        ui.button('Next flag ->', on_click=lambda:self.get_flag_image())
        ui.page_title('Flag Quizzer')
        
        self.get_flag_image()

    def true_visibility(self):
        self.answer_label.visible = True

    @ui.refreshable
    def get_flag_image(self):
        random_flag = randint(0, len(images)-1)
        chosen_flag = images[random_flag]

        image_divider = 5

        with Image.open(chosen_flag['file']) as img:
            width, height = img.size
            width = round(width/image_divider)
            height = round(height/image_divider)
            self.flag_image.set_source(img)
            
            
        self.answer_label.visible = False
        self.answer_label.text = chosen_flag['name']
        self.flag_image.props(f'width={width}px height={height}px')
        self.flag_image.force_reload


@ui.page('/')
def main_page():
    GUI()

if __name__ == '__main__':
    ui.run(reload=False, root=main_page, port = native.find_open_port())


