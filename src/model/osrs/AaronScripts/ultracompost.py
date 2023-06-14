import time
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSultracompost(OSRSBot):
    def __init__(self):
        bot_title = "Ultracompost maker"
        description = "This bot will make ultracompost."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 360
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
        # Setup APIs
        api_m = MorgHTTPSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            self.open_bank()
            self.deposit_all()
            self.withdraw_supplies(api_m)
            self.make_compost()
            time.sleep(35)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()   

    def make_compost(self):
        self.mouse.move_to(self.win.inventory_slots[0].random_point())
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[4].random_point())
        self.mouse.click()
        self.sleep(0.8, 2)
        pag.press('space')
    
    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Bank"):
            self.mouse.move_to(banker.random_point()) 
        self.mouse.click()
        self.sleep(1,2)

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)                                 
            
    def withdraw_supplies(self, api_m: MorgHTTPSocket):
        super_compost_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Supercompost_bank.png") # Specify which leather.png file to point to
        if super_compost := imsearch.search_img_in_rect(super_compost_bank_img, self.win.game_view):
            self.mouse.move_to(super_compost.random_point())
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