from pathlib import Path
from random import randint
import pandas as pd
import glob
from nicegui import app, ui, native, events
from PIL import Image
import os, sys
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

all_images = glob.glob(resource_path('Flags/*.png'))
all_images = [img for img in all_images if img.split(separator)[-1].split(".")[0].upper() not in open('ignored_codes.csv').read().splitlines()]

for i, image_file in enumerate(all_images):
    country_code = image_file.split(separator)[-1].split(".")[0].upper()
    country_name = lookup_df[lookup_df['Code'] == country_code]['Country'].iloc[0]
    images[i] = {'name': country_name, 'code': country_code, 'file': image_file}



#-------------------UI--------------------#

class GUI():
    def __init__(self):
        self.flag_image = ui.image()
        self.answer_label = ui.label(f'').classes('text-2xl text-green-500')
        self.answer_label.visible = False
        self.image_info = dict()
        
        ui.dark_mode(True)
        ui.page_title('Flag Quizzer')
        
        self.input_box = ui.input(label='Answer').on('keydown.enter', self.check_answer)
        
        
        with ui.row().classes('items-center gap-4'):
            ui.button('Show answer', on_click=lambda: self.true_visibility())
            ui.button('Next flag ->', on_click=lambda:self.get_flag_image())
        
        self.ignore_button = ui.button('Ignore this flag forever', color = 'red', on_click=lambda: self.ignore_flag())

        self.score_tracker_numerator = 0
        self.score_tracker_denominator = 0
        self.score_label = ui.label(f'Score: {self.score_tracker_numerator}/{self.score_tracker_denominator}').classes('text-lg text-blue-500')
        
        self.get_flag_image()


    def update_score(self):
        self.score_label.text = f'Score: {self.score_tracker_numerator}/{self.score_tracker_denominator}'

    def true_visibility(self):
        self.answer_label.visible = True

    def ignore_flag(self):
        with open('ignored_codes.csv', 'a') as f:
            f.write(self.image_info['code'] + '\n')

    def check_answer(self):
        answer = self.input_box.value
        if answer.lower() == self.image_info['name'].lower():
            self.answer_label.text = 'Correct!'
            self.answer_label.props('color = green')
            self.score_tracker_numerator += 1

        else:
            self.answer_label.text = f'Wrong! The correct answer is {self.image_info["name"]}.'
            self.answer_label.props('color = red')

        self.score_tracker_denominator += 1
        self.update_score()
        self.true_visibility()


    @ui.refreshable
    def get_flag_image(self):
        random_flag = randint(0, len(images)-1)
        self.image_info = images[random_flag]

        image_divider = 5

        with Image.open(self.image_info['file']) as img:
            width, height = img.size
            width = round(width/image_divider)
            height = round(height/image_divider)
            self.flag_image.set_source(img)
            
        
        self.answer_label.visible = False
        self.answer_label.text = self.image_info['name']
        self.flag_image.props(f'width={width}px height={height}px')
        self.flag_image.force_reload

        self.input_box.value = ''


@ui.page('/')
def main_page():
    GUI()

if __name__ == '__main__':
    ui.run(reload=False, root=main_page, port = 8080)


