import time
import random

import utilities.color as clr
import utilities.api.item_ids as ids
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket

class OSRSbow_fletcher(OSRSBot):
    def __init__(self):
        bot_title = "Bow Fletcher"
        description = "This bot will fletch longbows"
        super().__init__(bot_title=bot_title, description=description)
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
        api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            self.open_bank()
            self.deposit_all()
            self.withdraw_supplies(api_m)
            self.fletch_bow(api_m)
            self.sleep(15, 19) # Gives enough time to complete fletching

        self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("items", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()   

    def fletch_bow(self, api_m: MorgHTTPSocket):
        bow_string_img = imsearch.BOT_IMAGES.joinpath("scraper", "Bow_string.png")
        slots = [14, 17] # This selection will click the 2nd and 3rd leather from the top. Adjust to your liking
        slot = random.choice(slots)
        if not api_m.get_is_inv_full(): # Fail-safe for when there's only a few leather left, logout and kill the script
            self.logout()
            self.stop() 
        if bow_string := imsearch.search_img_in_rect(bow_string_img, self.win.inventory_slots[13]):
            if longbow_u := api_m.get_inv_item_indices(ids.longbows_u):
                self.mouse.move_to(bow_string.random_point())
                self.mouse.click()
                self.mouse.move_to(self.win.inventory_slots[longbow_u[slot]].random_point())
                self.mouse.click()
                self.sleep(0.8, 2)
                pag.press('space')
    
    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(banker.random_point())  
        self.mouse.click()
        self.sleep(1,2)

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)                                 
            
    def withdraw_supplies(self, api_m: MorgHTTPSocket):
        Bow_string_bank_img = imsearch.BOT_IMAGES.joinpath("scraper", "Bow_string_bank.png")
        Magic_longbow_u_img = imsearch.BOT_IMAGES.joinpath("scraper", "Magic_longbow_(u)_bank.png")
        while True:
            if bow_string := imsearch.search_img_in_rect(Bow_string_bank_img, self.win.game_view):
                if Magic_longbow_u := imsearch.search_img_in_rect(Magic_longbow_u_img, self.win.game_view):
                    self.mouse.move_to(bow_string.random_point())
                    self.mouse.click()
                    self.mouse.move_to(Magic_longbow_u.random_point())
                    self.mouse.click()
                    self.sleep(1,2)
                if not api_m.get_is_inv_full(): # Log out if no supplies are found
                    self.log_msg("No more supplies. Logging out.")
                    pag.press('escape')
                    self.logout()
                    self.stop()
                else:
                    pag.press('escape')
                    self.sleep(1,2)
                    break

# BUGS
# Sometimes does not withdraw the longbow (u)

# FUTURE UPDATES
# Update UI to accept more than just yew longbow (u)