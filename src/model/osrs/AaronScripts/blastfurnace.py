import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point, RuneLiteObject
from pathlib import Path


class OSRSblastfurnace(AaronFunctions):
    def __init__(self):
        bot_title = "Blast Furnace"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.bar_list = ['Gold']

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("bar_to_make", "Select bar to make", self.bar_list)
        
    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "bar_to_make":
                self.bar_to_make = options[option]
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
            # Open bank, withdraw supplies and close the bank
            self.gold_ore_open_bank()
                       
            # Make potions
            self.make_gold_ore()
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
    
    def get_ore_bank_img(self):
        if self.bar_to_make == 'Gold':
            ore_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gold_ore_bank.png")
            
        return ore_bank_img
    
    def get_secondary_bank_img(self):
        if self.bar_to_make == 'Prayer':
            secondary_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "snape_grass_bank.png")

        return secondary_bank_img 
    
    def make_gold_ore(self):
        ore_img = self.get_ore_bank_img()  
        if gold_ore := self.wait_until_img(ore_img, self.win.control_panel):
            self.log_msg("ore found in inventory")
            # self.click_color(clr.YELLOW) # Click conveyor belt
            self.deposit_Ores()
        else:
            self.log_msg("Couldn't find ore in inventory..Stopping script")
            self.stop()
        timer = 0
        while self.search_slot_28():
            time.sleep(0.5)
            timer += 1
            if timer == 40:
                self.log_msg("20 seconds have past and we've not seen the confirmed chat text. Clicking conveyor belt again.")
                return self.make_gold_ore()
        self.log_msg("Successfully deposited the gold ore.")
        first_tile = self.get_nearest_tag(clr.PINK)
        self.mouse.move_to(first_tile.random_point())
        self.mouse.click()
        ice_gloves_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ice_gloves.png")
        if ice_gloves := imsearch.search_img_in_rect(ice_gloves_img, self.win.inventory_slots[0]):
            self.mouse.move_to(ice_gloves.random_point())
        else:
            self.log_msg("Could not locate ice gloves. Stopping script.")
        self.wait_for_exp_drop() # Wait until we receive the exp drop that the ores made it to the dispenser
        self.mouse.click() # Click the gloves since we found them earlier
        time.sleep(1)
        self.retrieve_Ores() # Retrieve gold bars
        time.sleep(1.5)
        pag.press('space')
        goldsmith_gaunts_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "goldsmith_gauntlets.png")
        if goldsmith_gaunts := imsearch.search_img_in_rect(goldsmith_gaunts_img, self.win.inventory_slots[0]):
            self.mouse.move_to(goldsmith_gaunts.random_point())
            self.mouse.click()
        else:
            self.log_msg("Could not locate goldsmith gloves. Stopping script.")
        gold_bar_inv = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gold_bar.png")
        if gold_bar := imsearch.search_img_in_rect(gold_bar_inv, self.win.inventory_slots[1]): 
            self.log_msg("Gold bar found in inventory. We can bank.") 
        else:
            self.retrieve_Ores()  
            time.sleep(1.5)
            pag.press('space') 
        
    def gold_ore_open_bank(self):
        self.open_bank_af()
        ore_bank = self.get_ore_bank_img() 
        ore = self.wait_until_img(ore_bank, self.win.game_view)
        self.log_msg("Found ore in bank view")
        if self.search_slot_28():
            self.deposit_all()
        self.check_stamina()
        self.log_msg("Deposit button successfully clicked.")
        if ore:
            self.mouse.move_to(ore.random_point())
            self.log_msg("Withdrawing gold ore")
            # if self.mouseover_text(contains="Gold ore", color=clr.ORANGE):
            #     self.log_msg("Ran out of ore. Stopping script.")
            #     self.stop()
            if self.mouseover_text(contains="Release"):
                self.log_msg("Ran out of ore. Stopping script.")
                self.stop()
            self.mouse.click() 
        else:
            self.log_msg("Ore could not be found.")
            self.stop()
        while not self.search_slot_28():
            time.sleep(0.5)
        self.log_msg("Exiting bank.") 
        pag.press("escape")
        
    def check_stamina(self):
        stamina_1_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "stamina_potion_bank.png")
        current_energy = self.get_run_energy()
        if current_energy <= 60:
            if stamina_1_bank := imsearch.search_img_in_rect(stamina_1_bank_img, self.win.game_view):
                self.mouse.move_to(stamina_1_bank.random_point())
                pag.keyDown('shift')
                self.mouse.click()
                pag.keyUp('shift')
            else:
                self.log_msg("Run energy is below 60 and no staminas found. Stopping script.")
                self.stop()
            time.sleep(1)
            stamina_1_bank_inv = imsearch.BOT_IMAGES.joinpath("Aarons_images", "stamina_potion.png")
            if stamina_1_inv := imsearch.search_img_in_rect(stamina_1_bank_inv, self.win.control_panel):
                self.mouse.move_to(stamina_1_inv.random_point())
                pag.keyDown('shift')
                self.mouse.click()
                pag.keyUp('shift')
        
        return
    
    def wait_for_exp_drop(self):
        counter = 0
        last_xp = self.get_total_xp()
        while counter < 30:
            new_xp = self.get_total_xp()
            if new_xp != last_xp:
                break
            counter += 1
            self.log_msg(f"Seconds elapsed: {counter}")
            time.sleep(0.5)
            if counter == 30:
                self.log_msg("15 seconds have passed and we did not receie an exp drop.")
                return self.deposit_Ores()
    
    def deposit_Ores(self):
        if hopper := self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW):
            hopper = sorted(hopper, key=RuneLiteObject.distance_from_rect_center)
            while True:
                hopper = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
                hopper = sorted(hopper, key=RuneLiteObject.distance_from_rect_center)   
                if hopper:         
                    self.mouse.move_to(hopper[0].random_point())
                    time.sleep(0.1)
                    break  
            if self.mouse.click(check_red_click=True):
                self.log_msg("Successful clicked deposit!")
            else:
                return self.deposit_Ores()
            
    def retrieve_Ores(self):
        if dispenser := self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN):
            dispenser = sorted(dispenser, key=RuneLiteObject.distance_from_rect_center)
            while True:
                dispenser = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
                dispenser = sorted(dispenser, key=RuneLiteObject.distance_from_rect_center)   
                if dispenser:         
                    self.mouse.move_to(dispenser[0].random_point())
                    time.sleep(0.1)
                    break  
            if self.mouse.click(check_red_click=True):
                self.log_msg("Successful clicked deposit!")
            else:
                return self.retrieve_Ores()