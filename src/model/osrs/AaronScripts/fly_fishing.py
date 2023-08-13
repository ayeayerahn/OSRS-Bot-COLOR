import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point


class OSRSfishing(AaronFunctions):
    def __init__(self):
        bot_title = "Fishing"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1000

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if self.activate_special():
                self.click_color(clr.GREEN)
            else:
                self.click_color(color=clr.GREEN)
            while not self.search_slot_28():
                if self.activate_special():
                    # return self.main_loop()
                    self.click_color(color=clr.GREEN)
                time.sleep(1)
            self.drop_all(skip_rows=0, skip_slots=[0, 1])

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()