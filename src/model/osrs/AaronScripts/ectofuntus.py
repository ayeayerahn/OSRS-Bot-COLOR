import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSectofuntus(OSRSBot):
    def __init__(self):
        bot_title = "Ectofuntus"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.bone_list = ['Dragon']

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("bones_to_use", "Select bones", self.bone_list)
        
    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "bones_to_use":
                self.bones_to_use = options[option]
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
            # # Teleport to ectofuntus
            # self.tele_to_ectofuntus()
            
            # # Fill buckets of slime
            # self.fill_buckets()
            
            # # Make bonemeal
            # self.make_bonemeal()
            
            # # Worship
            # self.worship()

            # # Teleport to bank
            # self.teleport_to_bank()
            
            # # Replenish inventory
            # self.open_bank()
            self.click_bones()
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def get_bones_img(self):
        if self.bones_to_use == 'Dragon':
            bones_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "dragon_bones.png")

        return bones_img
    
    def teleport_to_bank(self):
        self.log_msg("Moving to worn slot")
        self.mouse.move_to(self.win.cp_tabs[4].random_point()) # Move to worn items slot
        if self.mouseover_text(contains="Worn", color=clr.OFF_WHITE):
            self.mouse.click()
        else:
            return self.teleport_to_bank()
        time.sleep(0.5)
        craft_cape_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "crafting_cape(t).png")
        if craft_cape := imsearch.search_img_in_rect(craft_cape_img, self.win.control_panel):
            self.mouse.move_to(craft_cape.random_point())
            self.mouse.click()
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        
    
    def worship(self):
        ectofuntus = self.get_nearest_tag(clr.BLUE)
        self.mouse.move_to(ectofuntus.random_point())
        # for i in range(9):
        while True:
            if self.chatbox_text_QUEST(contains="ectoplasm"):
                break
            if self.chatbox_text_QUEST(contains="room"):
                self.claim_ectotokens()
            self.mouse.click()
            time.sleep(0.5)

            
    def claim_ectotokens(self):
        while True:
            count = 0
            if count < 10:
                if found := self.get_nearest_tag(clr.OFF_ORANGE):
                    self.mouse.move_to(found.random_point())
                    if self.mouseover_text(contains="Ghost", color=clr.OFF_YELLOW):
                        if self.mouse.click(check_red_click=True):
                            break
                        else:
                            return self.claim_ectotokens()
                else:
                    count +=1
                    time.sleep(1)
        time.sleep(5)
        pag.press('space')
        time.sleep(1)
        pag.press('space')
        return self.worship()
    
    def make_bonemeal(self):
        bones_img = self.get_bones_img()
        self.click_color(clr.YELLOW)
        self.wait_until_color(clr.GREEN) # Wait until we see the machine
        if bones := imsearch.search_img_in_rect(bones_img, self.win.control_panel):
                self.mouse.move_to(bones.random_point())
                self.mouse.click()
        self.click_color(clr.GREEN)
        time.sleep(103)
        self.tele_to_ectofuntus()
        
    def open_trapdoor(self):
        self.click_color(clr.RED) # Open first part of trapdoor
        self.log_msg("Opening first trapdoor")
        i = 0
        while True:
            if self.chatbox_text_BLACK_first_line(contains="climb"):
                self.log_msg("Trapdoor was already opened.")
                break
            elif self.chatbox_text_BLACK_first_line(contains="opens"):
                time.sleep(1)
                self.log_msg("Opening second trapdoor")
                count = 0
                if count < 10:
                    if found := self.get_nearest_tag(clr.RED):
                        self.mouse.move_to(found.random_point())
                        if self.mouse.click(check_red_click=True):
                            break
                        # else:
                        #     return self.fill_buckets()
                else:
                    count += 1
                    time.sleep(1)
            else:
                i += 1
                # self.log_msg(f"Time elapsed: {i}")
                if i == 40:
                    return self.open_trapdoor()
            time.sleep(0.1)
    
    def fill_buckets(self):
        bucket_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bucket.png")
        self.open_trapdoor()
        time.sleep(1)
        self.click_color(clr.GREEN) # Click first stairs
        time.sleep(2.6)
        self.click_color(clr.GREEN) # Click second stairs
        time.sleep(1)
        self.click_color(clr.GREEN) # Click third stairs
        self.wait_until_color(clr.YELLOW)
        self.log_msg("Waiting for the yellow marked pool")
        if bucket := imsearch.search_img_in_rect(bucket_img, self.win.control_panel):
            self.mouse.move_to(bucket.random_point())
            self.mouse.click()
        self.click_color(clr.YELLOW)
        time.sleep(19)
        self.tele_to_ectofuntus()
    
    def tele_to_ectofuntus(self):
        ectophial_inv_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ectophial.png")
        if ectophial := imsearch.search_img_in_rect(ectophial_inv_img, self.win.control_panel):
            self.mouse.move_to(ectophial.random_point())
            self.mouse.click()
        while True:
            if self.chatbox_text_BLACK_first_line(contains="refill"):
                break
            time.sleep(0.1)
    
    def click_bones(self):
        bones_bank_img = self.get_bones_img()
        
        while True:
            if bones := imsearch.search_img_in_rect(bones_bank_img, self.win.inventory_slots[27]):
                if altar := self.get_nearest_tag(clr.CYAN):
                    self.mouse.move_to(bones.random_point())
                    self.mouse.click()
                    self.mouse.move_to(altar.random_point())
                    self.mouse.click()
            
    def open_bank(self):
        # bones_bank_img = self.get_bones_img()
        ectotokens_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ecto-token_bank.png") 
        bones_img = self.get_bones_img()
        self.wait_until_color(clr.CYAN)
        self.click_color(clr.CYAN)
        # bones_bank = self.wait_until_img(bones_bank_img, self.win.game_view)
        # Wait until selected bones is seen in our bank
        bones = self.wait_until_img(bones_img, self.win.game_view)
        time.sleep(1)
        if ectotokens := imsearch.search_img_in_rect(ectotokens_bank_img, self.win.control_panel):
            self.mouse.move_to(ectotokens.random_point())
            self.mouse.click()
        self.mouse.move_to(bones.random_point())
        if self.mouseover_text(contains="Release"):
            self.log_msg("Ran out of bones. Stopping script.")
            self.stop()
        self.mouse.click()
        pag.press("escape")
        time.sleep(1)
        
    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click() 
                           
    def click_color(self, color: clr):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if count < 10:
                if found := self.get_nearest_tag(color):
                    self.mouse.move_to(found.random_point())
                    if self.mouse.click(check_red_click=True):
                        break
                    else:
                        count += 1
                        time.sleep(1) 
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg("failed to find cape")
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