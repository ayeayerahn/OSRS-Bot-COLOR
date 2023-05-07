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

class OSRSgem_cutter(OSRSBot):
    def __init__(self):
        bot_title = "Gem Cutter"
        description = "This bot will cut your gems."
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
            self.sleep(15, 19) # Gives enough time to complete crafting

        self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(banker.random_point())  
        self.mouse.click()
        self.sleep(1,2)
    
    def withdraw_supplies(self, api_m: MorgHTTPSocket):
        uncut_sapphire_bank_img = imsearch.BOT_IMAGES.joinpath("scraper", "Uncut_sapphire_bank.png")
        while True:
            if uncut_gem := imsearch.search_img_in_rect(uncut_sapphire_bank_img, self.win.game_view):
                self.mouse.move_to(uncut_gem.random_point())
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

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)    

    def craft(self, api_m: MorgHTTPSocket):
        chisel_img = imsearch.BOT_IMAGES.joinpath("scraper", "Chisel.png") 
        slots = [1, 4]
        slot = random.choice(slots)
        if chisel := imsearch.search_img_in_rect(chisel_img, self.win.inventory_slots[0]):
            if gems := api_m.get_inv_item_indices(ids.gems):
                self.mouse.move_to(chisel.random_point())
                self.mouse.click()
                self.mouse.move_to(self.win.inventory_slots[gems[slot]].random_point())
                self.mouse.click()
                self.sleep(0.8, 2)
                pag.press('space')

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("items", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()   