import time

import pyautogui as pag
import utilities.api.item_ids as ids
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import utilities.color as clr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSalcher(OSRSBot):
    def __init__(self):
        bot_title = "Alcher"
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
        #api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            self.alch_time(api_m)
            self.sleep(1, 2)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
    
    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time) 

    def alch_time(self, api_m: MorgHTTPSocket):
        ALCHABLE_IDS = [
            ids.BLUE_DHIDE_BODY + 1,
            ids.GREEN_DHIDE_BODY + 1
        ]
        self.mouse.move_to(self.win.spellbook_normal[34].random_point())      
        self.mouse.click()  
        self.sleep(0.3, 0.5)
        if alchables := api_m.get_inv_item_indices(ALCHABLE_IDS):
            self.mouse.move_to(self.win.inventory_slots[alchables[0]].random_point())
            self.mouse.click()
            self.sleep(0.3, 0.5)
            pag.press("f6")
        else:
            self.log_msg("Ran out of alchables. Logging out.")
            self.mouse.click()
            self.logout()
            self.stop()

"""
 TO DO
 Implement mouseover text check to ensure there's an item to click - DONE
"""