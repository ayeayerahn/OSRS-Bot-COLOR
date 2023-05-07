import time

import pyautogui as pag
import utilities.color as clr
import utilities.api.item_ids as ids
import utilities.random_util as rd
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSfiremaker(OSRSBot):
    def __init__(self):
        bot_title = "Firemaker"
        description = "This bot will light logs."
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


            self.open_bank()
            self.withdraw_supplies(api_m)
            self.first_spot()
            self.second_spot()
            self.firemake(api_m)
            self.third_spot()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def firemake(self, api_m: MorgHTTPSocket):
        logs_inventory_img = imsearch.BOT_IMAGES.joinpath("scraper", "Willow_logs.png")
        for logs in range(28):
            #if logs := imsearch.search_img_in_rect(logs_inventory_img, self.win.inventory_slots[logs]):
            if logs := api_m.get_inv_item_indices(ids.logs):
                self.mouse.move_to(self.win.inventory_slots[0].random_point())
                self.mouse.click()
                self.mouse.move_to(self.win.inventory_slots[logs[0]].random_point())
                self.mouse.click()
                api_m.wait_til_gained_xp("Firemaking", 5)

    def first_spot(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
        self.log_msg("Heading to the first tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(5)

    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(banker.random_point())  
        self.mouse.click()
        self.sleep(1,2)

    def second_spot(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.PURPLE)
        self.log_msg("Heading to the second tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(3)

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
# TO DO's
# Maybe rotate through 3-4 different squares to add variation to "start point"