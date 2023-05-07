import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSRSmyWoodcutter(OSRSBot):
    def __init__(self):
        bot_title = "Aaron's Woodcutter"
        description = "This bot power-chops wood. Position your character near some trees, tag them, and press the play button."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        self.logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:
            # 5% chance to take a break between tree searches
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=30, fancy=True)

            # If inventory is full
            if api_s.get_is_inv_full():
                self.move_to_bank() 
                self.deposit_all()
                self.return_to_tree()          
                

            # If our mouse isn't hovering over a tree, and we can't find another tree...
            if not self.mouseover_text(contains="Chop", color=clr.OFF_WHITE) and not self.__move_mouse_to_nearest_tree():
                failed_searches += 1
                if failed_searches % 10 == 0:
                    self.log_msg("Searching for trees...")
                if failed_searches > 60:
                    # If we've been searching for a whole minute...
                    self.__logout("No tagged trees found. Logging out.")
                time.sleep(1)
                continue
            failed_searches = 0  # If code got here, a tree was found

            # Click if the mouseover text assures us we're clicking a tree
            if not self.mouseover_text(contains="Yew"):
                continue
            self.mouse.click()
            time.sleep(0.5)

            # While the player is chopping (or moving), wait
            probability = 0.10
            while not api_m.get_is_player_idle():
                # Every second there is a chance to move the mouse to the next tree, lessen the chance as time goes on
                if rd.random_chance(probability):
                    self.__move_mouse_to_nearest_tree(next_nearest=True)
                    probability /= 2
                time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def move_to_bank(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        self.log_msg("Heading to the first tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(10)
        self.log_msg("Finding the bank")
        banker = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Found the banker")
        self.mouse.move_to(banker.random_point())  
        self.log_msg("Clicking the banker")
        self.mouse.click()
        time.sleep(5)    

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("items", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.log_msg("Found the deposit img") 
            self.mouse.move_to(deposit.random_point())      
            self.mouse.click()   
            time.sleep(1)
            pag.press('escape') 
            time.sleep(0.5)    

    def return_to_tree(self):
        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        self.log_msg("Heading to the first tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(5)

        tile = self.get_all_tagged_in_rect(self.win.game_view, clr.ORANGE)
        self.log_msg("Heading to the second tile")
        self.mouse.move_to(tile[0].random_point())
        self.mouse.click()
        time.sleep(10) 

    def __move_mouse_to_nearest_tree(self, next_nearest=False):
        trees = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
        tree = None
        if not trees:
            return False
        # If we are looking for the next nearest tree, we need to make sure trees has at least 2 elements
        if next_nearest and len(trees) < 2:
            return False
        trees = sorted(trees, key=RuneLiteObject.distance_from_rect_center)
        tree = trees[1] if next_nearest else trees[0]
        if next_nearest:
            self.mouse.move_to(tree.random_point(), mouseSpeed="slow", knotsCount=2)
        else:
            self.mouse.move_to(tree.random_point())
        return True
    
    def choose_bank(self):
        """
        Has a small chance to choose the second closest bank to the player.
            Returns: bank rectangle or none if no banks are found
            Args: None
        """
        if banks := self.get_all_tagged_in_rect(self.win.game_view, clr.PURPLE):
            banks = sorted(banks, key=RuneLiteObject.distance_from_rect_center)

            if len(banks) == 1:
                return banks[0]
            if (len(banks) > 1):
                return banks[0] if rd.random_chance(.74) else banks[1]
        else:
            self.log_msg("No banks found, trying to adjust camera...")
            self.adjust_camera(clr.PURPLE)
            return (self.choose_bank())
    
    def open_bank(self):
         banker = self.get_all_tagged_in_rect(self.win.game_view, clr.PURPLE)  
         self.mouse.move_to(banker.random_point())  
         self.mouse.click()

    def find_bank(self, deposit_slots):
        search_tries = 1

            # Time to bank
        self.log_msg("Banking...")
        # move mouse one of the closes 2 banks

        bank = self.choose_bank()

        # move mouse to bank and click
        self.mouse.move_to(bank.random_point())
        time.sleep(self.random_sleep_length(.8, 1.2))

        # search up to 5 times for mouseover text "bank"
        while not self.mouseover_text(contains="Bank"):
            self.log_msg(f"Bank not found, trying again. Try #{search_tries}.")
            self.mouse.move_to(bank.random_point())
            time.sleep(self.random_sleep_length())

            if search_tries > 5:
                self.log_msg(f"Did not see 'Bank' in mouseover text after {search_tries} searches, quitting bot so you can fix it...")
                self.stop()
            search_tries += 1

        self.mouse.click()
        time.sleep(self.random_sleep_length())

        wait_time = time.time()
        while not self.api_m.get_is_player_idle():
            # if we waited for 10 seconds, break out of loop
            if time.time() - wait_time > 15:
                self.log_msg("We clicked on the bank but player is not idle after 10 seconds, something is wrong, quitting bot.")
                self.stop()
            time.sleep(self.random_sleep_length(.8, 1.3))
            
        # if bank is open, deposit all 
        self.bank_each_item(deposit_slots)

        return