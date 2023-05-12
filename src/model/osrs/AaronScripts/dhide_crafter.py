import time
import random

import utilities.color as clr
import utilities.api.item_ids as ids
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSdhide_crafter(OSRSBot):
    def __init__(self):
        bot_title = "Dhide Crafter"
        description = "This bot will craft dragonhide bodies."
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
        # Setup APIs
        api_m = MorgHTTPSocket()
        #api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            self.open_bank()
            self.deposit_all()
            self.withdraw_supplies(api_m)
            self.craft(api_m)
            self.hover_banker(api_m)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()   

    def craft(self, api_m: MorgHTTPSocket):
        needle_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Needle.png")
        slots = [2, 3] # This selection will click the 2nd and 3rd leather from the top. Adjust to your liking
        slot = random.choice(slots)
        if not api_m.get_is_inv_full(): # Fail-safe for when there's only a few leather left, logout and kill the script
            self.logout()
            self.stop()
        if needle := imsearch.search_img_in_rect(needle_img, self.win.inventory_slots[0]):
            if leather := api_m.get_inv_item_indices(ids.leathers):
                self.mouse.move_to(needle.random_point())
                self.mouse.click()
                self.mouse.move_to(self.win.inventory_slots[leather[slot]].random_point())
                self.mouse.click()
                self.sleep(0.8, 2)
                pag.press('space')

    def hover_banker(self, api_m: MorgHTTPSocket):
        banker = self.get_nearest_tag(clr.CYAN)
        self.sleep(3,7)
        self.mouse.move_to(banker.random_point(), mouseSpeed = "medium", knotsCount=2)
        while True:
            try:
                if api_m.get_is_player_idle(poll_seconds=2):
                    break
            except:
                time.sleep(5)
    
    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Bank"):
            self.mouse.move_to(banker.random_point()) 
        self.mouse.click()
        self.sleep(1,2)
                    #if not api_m.get_is_player_idle():
                #self.sleep(1,7)
                #self.mouse.move_to(banker.random_point(), mouseSpeed = "slow", knotsCount=2)
                #self.sleep(10,15)

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)                                 
            
    def withdraw_supplies(self, api_m: MorgHTTPSocket):
        leather_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Blue_dragon_leather_bank.png") # Specify which leather.png file to point to
        while True:
            if leather := imsearch.search_img_in_rect(leather_bank_img, self.win.game_view):
                self.mouse.move_to(leather.random_point())
                self.mouse.click()
                self.sleep(1,2)
            if not api_m.get_is_inv_full(): # Log out if no supplies are found
                self.log_msg("No more supplies. Logging out.")
                pag.press('escape')
                self.logout()
                self.stop()
            else:
                pag.press('escape')
                self.sleep(0.5, 1)
                break

    def craftv2(self):
        self.mouse.move_to(self.win.inventory_slots[0].random_point()) 
        self.mouse.click()
        

# BUGS
# 

# FUTURE UPDATES
# Figure out a way to make a list of all leathers so the user does not have to specify