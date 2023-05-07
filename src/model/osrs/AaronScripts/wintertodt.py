import time
import random

import pyautogui as pag
import utilities.color as clr
import utilities.api.item_ids as ids
import utilities.random_util as rd
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSwintertodt(OSRSBot):
    def __init__(self):
        bot_title = "Wintertodt"
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

        # Setup APIs
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            # 1. Open bank
            #self.open_bank()
            # 2. Withdraw supplies
            #self.withdraw_supplies(api_m)
            # 3. Walk to first spot
            #self.first_spot()
            # 4. Click on big door
            #self.big_door()
            # 5. Walk to second spot
            #self.second_spot()
            # 6. Begin wintertodt
            self.wintertodt(api_m)
            # 7. Open bank (#1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


    def first_spot(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        self.log_msg("Heading to the first tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(5)

    def big_door(self):
        door = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(door.random_point())  
        self.mouse.click()
        self.sleep(5,7)        

    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(banker.random_point())  
        self.mouse.click()
        self.sleep(1,2)

    def second_spot(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.ORANGE)
        self.log_msg("Heading to the second tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        self.sleep(4,6)

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)    

    def third_spot(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        self.log_msg("Heading to the third tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(5)

    def withdraw_supplies(self, api_m: MorgHTTPSocket):
        logs_bank_img = imsearch.BOT_IMAGES.joinpath("scraper", "Willow_logs_bank.png")
        while True:
            if logs := imsearch.search_img_in_rect(logs_bank_img, self.win.game_view):
                self.mouse.move_to(logs.random_point())
                self.mouse.click()
                time.sleep(1)
            if api_m.get_is_inv_full():
                pag.press('escape')
                time.sleep(0.5)
                break
    
    def wintertodt(self, api_m: MorgHTTPSocket):
        tree = self.get_nearest_tag(clr.CYAN)
        fire = self.get_nearest_tag(clr.GREEN)
        brazier = self.get_nearest_tag(clr.YELLOW)
        while True:
            # If inventory is not full and player is idle
            while not api_m.get_is_inv_full() and api_m.get_is_player_idle():
                self.mouse.move_to(tree.random_point())  
                self.mouse.click()
                self.sleep(1,2)
            if api_m.get_is_inv_full():
                self.mouse.move_to(fire.random_point())  
                self.mouse.click()
                self.sleep(5,7)

# TO DO's