import time
import pytweening

import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket

class OSRSherb_cleaner(OSRSBot):
    def __init__(self):
        bot_title = "Aaron's Herb Cleaner"
        description = "This bot will clean herbs."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        #self.what_to_fletch = None

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        #self.options_builder.add_dropdown_option("what_to_fletch", "Select bow to fletch", fletcher_recipes.Bow_recipes)

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
        #api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            # Logic for cleaning herbs
            # 1. Open bank
            self.open_bank()
            # 2. Deposit all
            self.deposit_all()
            # 3. Withdraw grimy herbs
            self.withdraw_herbs()
            # 4. Close bank
            self.close_bank()
            # 5. Click on all grimy herbs
            self.click_herbs(api_s)
            # 6. Sleep for a little bit
            self.sleep_time()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Found the banker")
        self.mouse.move_to(banker.random_point())  
        self.log_msg("Clicking the banker")
        self.mouse.click()
        time.sleep(1)
    
    def withdraw_herbs(self):
        # Locate herb of choice
        grimy_harralander_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Grimy_harralander_bank.png")
        # Click on herb in bank
        if grimy_herb := imsearch.search_img_in_rect(grimy_harralander_bank_img, self.win.game_view):
            self.mouse.move_to(grimy_herb.random_point())
            self.mouse.click()

    def sleep_time(self):
        sleep_time = rd.fancy_normal_sample(2, 5)   
        self.log_msg(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time) 

    def close_bank(self):
        time.sleep(0.5)
        pag.press('escape')
        time.sleep(0.5)

    def click(self, slots) -> None:
        self.log_msg("Dropping items...")
        for i, slot in enumerate(self.win.inventory_slots):
            if i not in slots:
                continue
            p = slot.random_point()
            self.mouse.move_to(
                (p[0], p[1]),
                mouseSpeed="fastest",
                knotsCount=1,
                offsetBoundaryY=40,
                offsetBoundaryX=40,
                tween=pytweening.easeInOutQuad,)
            pag.click()

    def click_herbs(self, api_s: StatusSocket):
        slots = api_s.get_inv_item_indices(205)
        self.click(slots)

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.log_msg("Found the deposit img") 
            self.mouse.move_to(deposit.random_point())   
            time.sleep(0.5)   
            self.mouse.click()   
            time.sleep(0.5)