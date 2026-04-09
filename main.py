from random import choice
import csv
import glob
from nicegui import app, ui, events
from PIL import Image
import os, sys
from thefuzz import fuzz

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_images():
    # Read CSV with stdlib — no pandas/numpy overhead
    with open(resource_path('countrylookup.csv'), encoding='latin1') as f:
        lookup = {row['Code']: row['Country'] for row in csv.DictReader(f)}

    ignored = set(open('ignored_codes.csv').read().splitlines())
    separator = "/" if os.name != 'nt' else "\\"

    images = {}
    for i, image_file in enumerate(glob.glob(resource_path('Flags/*.png'))):
        code = image_file.split(separator)[-1].split(".")[0].upper()
        if code in ignored or code not in lookup:
            continue
        images[i] = {'name': lookup[code], 'code': code, 'file': image_file}
    return images


#-------------------UI--------------------#

class GUI():
    def __init__(self):
        self.flag_image = ui.image()
        self.answer_label = ui.label(f'').classes('text-2xl text-green-500')
        self.answer_label.visible = False
        self.image_info = dict()
        self.image_dict = get_images()
        
        ui.dark_mode(True)
        ui.page_title('Flag Quizzer')
        
        self.input_box = ui.input(label='Answer').on('keydown.enter', self.check_answer)

        ui.keyboard(on_key = lambda e: self.get_flag_image() if (e.key == "ArrowRight" and e.action.keydown) else None)
        
        with ui.row().classes('items-center gap-4'):
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
        self.input_box.enabled = False

        if fuzz.token_sort_ratio(answer.lower(), self.image_info['name'].lower()) > 80:
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
        if len(self.image_dict) == 0:
            self.answer_label.text = 'No more flags to show! Please restart the app to play again.'
            self.answer_label.visible = True
            self.input_box.enabled = False
            self.ignore_button.enabled = False
            return

        random_flag = choice(list(self.image_dict.keys()))
        self.image_info = self.image_dict.pop(random_flag)

        # Get dimensions without keeping the image decoded in memory
        image_divider = 5
        with Image.open(self.image_info['file']) as img:
            width  = round(img.width  / image_divider)
            height = round(img.height / image_divider)

        # Serve as a static URL — avoids base64-encoding the image in Python memory
        flag_url = f'/flags/{self.image_info["code"].lower()}.png'
        self.flag_image.set_source(flag_url)
        self.flag_image.props(f'width={width}px height={height}px')

        self.answer_label.visible = False
        self.answer_label.text = self.image_info['name']

        self.input_box.enabled = True
        self.input_box.value = ''
        self.input_box.run_method('focus')



@ui.page('/')
def main_page():
    GUI()

# Serve flag images as static files — browser fetches them directly, no Python memory used
app.add_static_files('/flags', resource_path('Flags'))

if __name__ == '__main__':
    ui.run(reload=False, port=8080, host='0.0.0.0', forwarded_allow_ips='*')


