import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSgildedaltar(OSRSBot):
    def __init__(self):
        bot_title = "Gilded Altar"
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
            # Teleport to Rimmington
            self.teleport_to_rimmington()
            
            # Enter home
            self.enter_home()
            
            # Offer bones
            self.click_bones()
            
            # Teleport to bank
            self.teleport_to_bank()
            
            # Open bank
            self.open_bank()
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def enter_home(self):
        altar = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(altar.random_point())
        self.mouse.click()
        time.sleep(3)
        pag.press('enter')
        self.wait_until_color(clr.CYAN)
        
    def teleport_to_rimmington(self):
        self.mouse.move_to(self.win.cp_tabs[4].random_point()) # Move to worn items slot
        if self.mouseover_text(contains="Worn", color=clr.OFF_WHITE):
            self.mouse.click()
        else:
            return self.teleport_to_rimmington()
        time.sleep(0.5)
        con_cape_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "construct._cape(t).png")
        if con_cape := imsearch.search_img_in_rect(con_cape_img, self.win.control_panel):
            self.mouse.move_to(con_cape.random_point())
            self.mouse.click()
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        time.sleep(0.8)
        pag.press('2')
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        time.sleep(3)
        
    def get_bones_img(self):
        if self.bones_to_use == 'Dragon':
            bones_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "dragon_bones.png")

        return bones_img
    
    def teleport_to_bank(self):
        craft_cape_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "crafting_cape(t).png")
        if craft_cape := imsearch.search_img_in_rect(craft_cape_img, self.win.control_panel):
            self.mouse.move_to(craft_cape.random_point())
            self.mouse.click()
        time.sleep(3)
    
    def click_bones(self):
        bones_bank_img = self.get_bones_img()
        if bones := imsearch.search_img_in_rect(bones_bank_img, self.win.inventory_slots[27]):
            if altar := self.get_nearest_tag(clr.CYAN):
                self.mouse.move_to(bones.random_point())
                self.mouse.click()
                self.mouse.move_to(altar.random_point())
                self.mouse.click()
        time.sleep(4)
        while True:
            if bones := imsearch.search_img_in_rect(bones_bank_img, self.win.inventory_slots[27]):
                if altar := self.get_nearest_tag(clr.CYAN):
                    self.mouse.move_to(bones.random_point())
                    self.mouse.click()
                    self.mouse.move_to(altar.random_point())
                    self.mouse.click()
                    time.sleep(0.3)
            else:
                break
            
    def open_bank(self):
        bones_img = self.get_bones_img()
        self.click_color(clr.CYAN)
        bones = self.wait_until_img(bones_img, self.win.game_view)
        time.sleep(1)
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