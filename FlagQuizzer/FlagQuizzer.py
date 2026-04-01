from pathlib import Path
from random import randint
import pandas as pd
import glob
from nicegui import app, ui, native
from PIL import Image
import os, sys
import nicegui


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

lookup_df = pd.read_csv(resource_path('countrylookup.csv'), encoding='latin1')

images = {}
for i, image_file in enumerate(glob.glob(resource_path('Flags/*.png'))):
    country_code = image_file.split("\\")[-1].split(".")[0].upper()
    country_name = lookup_df[lookup_df['Code'] == country_code]['Country'].iloc[0]
    images[i] = {'name': country_name, 'file': image_file}

# flag_folder = resource_path('./Flags/')
# count = len([p for p in Path(flag_folder).iterdir() if p.is_file()])
# flag_pics = glob.glob(flag_folder + '*.png')





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
        # self.answer_label.text = lookup_df[lookup_df['Code'] == chosen_flag.split('\\')[1].split('.')[0]]['Country'].iloc[0]
        self.answer_label.text = chosen_flag['name']
        self.flag_image.props(f'width={width}px height={height}px')
        self.flag_image.force_reload


@ui.page('/')
def main_page():
    GUI()

ui.run(reload=False, root=main_page, port = native.find_open_port())


