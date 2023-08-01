import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSpotionmaker(OSRSBot):
    def __init__(self):
        bot_title = "Potion Maker"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.potion_list = ['Prayer', 'Super Restore']

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("potion_to_make", "Select potion", self.potion_list)
        
    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "potion_to_make":
                self.potion_to_make = options[option]
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
                       
            # Make potions
            self.make_potions()
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
    
    def get_primary_bank_img(self):
        if self.potion_to_make == 'Prayer':
            primary_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ranarr_potion_(unf)_bank.png")
        elif self.potion_to_make == 'Super Restore':
            primary_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "snapdragon_potion_(unf)_bank.png")
        return primary_bank_img
    
    def get_secondary_bank_img(self):
        if self.potion_to_make == 'Prayer':
            secondary_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "snape_grass_bank.png")
        elif self.potion_to_make == 'Super Restore':
            secondary_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "red_spiders'_eggs_bank.png")

        return secondary_bank_img 
    
    def make_potions(self):
        primary_img = self.get_primary_bank_img() 
        secondary_img = self.get_secondary_bank_img() 
        if primary := self.wait_until_img(primary_img, self.win.control_panel):
            if secondary := self.wait_until_img(secondary_img, self.win.control_panel):
        # if primary := imsearch.search_img_in_rect(primary_img, self.win.control_panel):
        #     if secondary := imsearch.search_img_in_rect(secondary_img, self.win.control_panel):
        # if primary := imsearch.search_img_in_rect(primary, self.win.control_panel):
        #     if secondary := imsearch.search_img_in_rect(secondary, self.win.control_panel):
        #         self.mouse.move_to(primary.random_point())
        #         self.mouse.click()
        #         self.mouse.move_to(secondary.random_point())
        #         self.mouse.click()
                self.mouse.move_to(primary.random_point())
                self.mouse.click()
                self.mouse.move_to(secondary.random_point())
                self.mouse.click()
            else:
                self.log_msg("Couldn't find secondary in inventory..")
                return self.main_loop()
        else:
            self.log_msg("Couldn't find primary in inventory..")
            return self.main_loop()
        time.sleep(1)
        pag.press('space')
        time.sleep(2) # Guarantees that if the last message  was amulet breaking, we don't start everything
        counter = 0
        while counter <= 13: # Usually 17 seconds but minus 1 for the above sleep(1)
            if self.chatbox_text_RED_dodgy_necklace(contains="crumbles"):
                self.log_msg("Amulet broken. Banking.")
                break
            counter += 1
            time.sleep(1)
            
    def check_broken_amulet_text(self):
        amulet_of_chemistry_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "amulet_of_chemistry_bank.png")
        amulet_of_chemistry_bank = self.wait_until_img(amulet_of_chemistry_bank_img, self.win.game_view)
        if self.chatbox_text_RED_dodgy_necklace(contains="crumbles"):
            self.mouse.move_to(amulet_of_chemistry_bank.random_point())
            self.mouse.right_click()
            if withdraw_text := ocr.find_text("1 Amulet", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.ORANGE]):
                self.mouse.move_to(withdraw_text[1].random_point(), knotsCount=0)
                self.mouse.click()
                time.sleep(1)
                # pag.press('esc')
                # time.sleep(1)
        amulet_of_chemistry_inv_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "amulet_of_chemistry.png")
        if amulet_of_chemistry_inv := imsearch.search_img_in_rect(amulet_of_chemistry_inv_img, self.win.control_panel):
            self.mouse.move_to(amulet_of_chemistry_inv.random_point())
            pag.keyDown('shift')
            self.mouse.click()
            pag.keyUp('shift')
            # self.click_color(clr.CYAN)
            time.sleep(1)
        
        
    def open_bank(self):
        self.click_color(clr.CYAN) # Click banker
        primary_bank = self.get_primary_bank_img() 
        secondary_bank = self.get_secondary_bank_img() 
        primary = self.wait_until_img(primary_bank, self.win.game_view)
        secondary = self.wait_until_img(secondary_bank, self.win.game_view)
        self.deposit_all()
        self.check_broken_amulet_text()
        self.mouse.move_to(primary.random_point())
        if self.mouseover_text(contains="Release"):
            self.log_msg("Ran out of primary. Stopping script.")
            self.stop()
        self.mouse.click()
        self.mouse.move_to(secondary.random_point())
        if self.mouseover_text(contains="Release"):
            self.log_msg("Ran out of secondary. Stopping script.")
            self.stop()
        self.mouse.click()      
        pag.press("escape")
        #time.sleep(0.6)


    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := self.wait_until_img(deposit_img, self.win.game_view):
        # if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click() 
                           
    def click_color(self, color: clr):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if found := self.get_nearest_tag(color):
                if count < 10:
                    self.mouse.move_to(found.random_point())
                    if self.mouse.click(check_red_click=True):
                        break
                    else:
                        count += 1
                        time.sleep(1) 
                else:
                    count += 1
                    time.sleep(1)
                    if count == 10:
                        self.log_msg("We misclicked 10 times. Stopping script.")
                        self.stop()
            else:
                self.log_msg("failed to find object to click")
                self.stop() 
        return

    def wait_until_color(self, color: clr, timeout: int = 10):
        """this will wait till nearest tag is not none"""
        time_start = time.time()
        while True:
            if time.time() - time_start > timeout:
                self.log_msg(f"We've been waiting for {timeout} seconds, something is wrong...stopping.")
                self.stop()
            if found := self.get_nearest_tag(color):
                break
            time.sleep(0.1)
        return
            
    def wait_until_img(self, img: Path, screen: Rectangle, timeout: int = 10):
        """this will wait till img shows up in screen"""
        time_start = time.time()
        while True:
            if found :=imsearch.search_img_in_rect(img, screen):
                break
            if time.time() - time_start > timeout:
                self.log_msg(f"We've been waiting for {timeout} seconds, something is wrong...stopping.")
                self.stop()
        return found