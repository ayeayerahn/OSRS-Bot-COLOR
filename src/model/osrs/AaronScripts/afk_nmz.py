import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point, RuneLiteObject
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSafk_nmz(AaronFunctions):
    def __init__(self):
        bot_title = "AFK NMZ"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1000 # Set to True to disable options, 1 otherwise
        self.options_set = True

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
        api_morg = MorgHTTPSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.check_hp()
            
            
            
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def check_hp(self):
        current_hp = self.get_hp()
        if current_hp > 1:
            # click rock cake once
            pag.moveTo(self.win.inventory_slots[0].random_point())
            pag.click()
        return
    
    def check_boosted(self, api_morg=MorgHTTPSocket):
        if not api_morg.get_is_boosted(self, skill="Attack"):
            self.log_msg("Boost expired. Drinking another dose of super combat.")
            