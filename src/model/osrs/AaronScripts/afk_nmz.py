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
            self.check_absorption()
            self.check_hp()
            self.check_ovl()
            
            
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def check_absorption(self):
        absorption_1_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "absorption_(1).png")
        absorption_2_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "absorption_(2).png")
        absorption_3_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "absorption_(3).png")
        absorption_4_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "absorption_(4).png")
        if self.chatbox_text_BLACK(contains="absorption potion"):
            pass
        elif self.chatbox_text_ABSORPTION(contains="absorption"):
            if absorption_1 := imsearch.search_img_in_rect(absorption_1_img, self.win.control_panel):
                self.log_msg("Found 1 dose absorption")
                self.mouse.move_to(absorption_1.random_point())
                self.mouse.click()
                time.sleep(1)
            elif absorption_2 := imsearch.search_img_in_rect(absorption_2_img, self.win.control_panel):
                self.log_msg("Found 2 dose absorption")
                self.mouse.move_to(absorption_2.random_point())
                self.mouse.click()
                time.sleep(1)
            elif absorption_3 := imsearch.search_img_in_rect(absorption_3_img, self.win.control_panel):
                self.log_msg("Found 3 dose absorption")
                self.mouse.move_to(absorption_3.random_point())
                self.mouse.click()
                time.sleep(1)
            elif absorption_4 := imsearch.search_img_in_rect(absorption_4_img, self.win.control_panel):
                self.log_msg("Found 4 dose absorption")
                self.mouse.move_to(absorption_4.random_point())
                self.mouse.click()
                time.sleep(1)
            else:
                self.log_msg("No absorptions left.")
            time.sleep(10)

    def check_hp(self):
        current_hp = self.get_hp()           
        if current_hp == 2 or current_hp == 3:
            # click rock cake once
            pag.moveTo(self.win.inventory_slots[0].random_point())
            pag.click()
            time.sleep(1)
        return
                
    def check_ovl(self):
        if self.chatbox_text_RED(contains="overload"):
            overload_1_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "overload_(1).png")
            overload_2_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "overload_(2).png")
            overload_3_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "overload_(3).png")
            overload_4_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "overload_(4).png")
            
            current_hp = self.get_hp()
            if current_hp > 50:
                if overload_1 := imsearch.search_img_in_rect(overload_1_img, self.win.control_panel):
                    self.log_msg("Found 1 dose ovl")
                    self.mouse.move_to(overload_1.random_point())
                    self.mouse.click()
                    time.sleep(1)
                elif overload_2 := imsearch.search_img_in_rect(overload_2_img, self.win.control_panel):
                    self.log_msg("Found 2 dose ovl")
                    self.mouse.move_to(overload_2.random_point())
                    self.mouse.click()
                    time.sleep(1)
                elif overload_3 := imsearch.search_img_in_rect(overload_3_img, self.win.control_panel):
                    self.log_msg("Found 3 dose ovl")
                    self.mouse.move_to(overload_3.random_point())
                    self.mouse.click()
                    time.sleep(1)
                elif overload_4 := imsearch.search_img_in_rect(overload_4_img, self.win.control_panel):
                    self.log_msg("Found 4 dose ovl")
                    self.mouse.move_to(overload_4.random_point())
                    self.mouse.click()
                    time.sleep(1)
                time.sleep(10)