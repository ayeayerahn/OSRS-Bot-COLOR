import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Rectangle, Point, RuneLiteObject
from utilities.imagesearch import search_img_in_rect


class OSRSanvil_smith(AaronFunctions):
    def __init__(self):
        bot_title = "Anvil Smither"
        description = "Set camera east. Don't need to set options"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 500
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
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.open_bank_af()
            self.withdraw_bars()
            self.click_anvil()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def withdraw_bars(self):
        self.deposit_all()
        addy_bar_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "adamantite_bar_bank.png")
        if addy_bar := imsearch.search_img_in_rect(addy_bar_img, self.win.game_view):
            pag.moveTo(addy_bar.random_point())
            pag.click()
        else:
            self.log_msg("Addy bar not found in bank. Stopping script")
            self.stop()
        counter = 0
        while True:
            counter += 1
            if counter == 100:
                return self.withdraw_bars()
            if self.search_slot_28():
                break
            time.sleep(0.1)
        pag.press("escape")
        
    def click_anvil(self):
        counter = 0
        while counter != 100:
            if anvil := self.get_all_tagged_in_rect(self.win.game_view, color=clr.GREEN):
                anvil = sorted(anvil, key=RuneLiteObject.distance_from_rect_center)
                pag.moveTo(anvil[0].random_point())
                if not self.mouseover_text(contains="Smith", color=clr.OFF_WHITE):
                    continue
                else:
                    pag.click()
                    break
            time.sleep(0.1)
            counter += 1
        counter = 0
        while True:
            if self.smelt_interface():
                break
            counter += 1
            time.sleep(0.1)
            if counter == 100:
                return self.main_loop()
        pag.press("space")
        time.sleep(14.5)
            
    def smelt_interface(self):
        if ocr.find_text("make", self.win.game_view, ocr.BOLD_12, clr.OFF_ORANGE):
            self.log_msg("Text found")
            return True
        else:
            self.log_msg("Could not find fishing text")