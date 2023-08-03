import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSwines(AaronFunctions):
    def __init__(self):
        bot_title = "Wines"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1

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
            # Open bank, withdraw supplies and close the bank
            self.open_bank()
                       
            # Make wines
            self.make_wines()
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def make_wines(self):
        grapes_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "grapes.png")
        jug_of_water_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "jug_of_water.png")
        if grapes := self.wait_until_img(grapes_img, self.win.control_panel):
            self.mouse.move_to(grapes.random_point())
            self.mouse.click()
            if jug_of_water := self.wait_until_img(jug_of_water_img, self.win.control_panel):
                self.mouse.move_to(jug_of_water.random_point())
                self.mouse.click()
            else:
                self.log_msg("Couldn't find jugs of water. Stopping script.")
                return self.main_loop()
        else:
            self.log_msg("Couldn't find grapes. Stopping script.")
            return self.main_loop()
        time.sleep(1)
        pag.press('space')
        time.sleep(16.8)
        
    def open_bank(self):
        self.open_bank_af()
        grapes_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "grapes_bank.png")
        jug_of_water_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "jug_of_water_bank.png")
        self.deposit_all()
        if grapes := imsearch.search_img_in_rect(grapes_bank_img, self.win.game_view):
            self.mouse.move_to(grapes.random_point())
            if self.mouseover_text(contains="Release"):
                self.log_msg("Ran out of grapes. Stopping script.")
                self.stop()
            self.mouse.click()
        else:
            self.log_msg("Ran out of grapes. Stopping script.")
            self.stop()            


        if jug_of_water := imsearch.search_img_in_rect(jug_of_water_bank_img, self.win.game_view):
            self.mouse.move_to(jug_of_water.random_point())
            if self.mouseover_text(contains="Release"):
                self.log_msg("Ran out of jug of water. Stopping script.")
                self.stop()
            self.mouse.click() 
        else:
            self.log_msg("Ran out of grapes. Stopping script.")
            self.stop()

        if self.search_slot_28():
            self.log_msg("Inventory full. Closing bank.")
            pag.press("escape")
        else:
            self.log_msg("Inventory was not full so the bank did not close. Stopping the script.")
            self.stop()