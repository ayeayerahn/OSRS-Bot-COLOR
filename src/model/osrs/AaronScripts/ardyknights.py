import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSardyknights(OSRSBot):
    def __init__(self):
        bot_title = "Ardy Knights"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.food_list = ['Trout', 'Tuna', 'Salmon', 'Shark']

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("food_to_use", "Select food", self.food_list)
        
    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "food_to_use":
                self.food_to_use = options[option]
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
            counter = 0
            self.click_knight()
            while True:
                if self.chatbox_text_BLACK_first_line(contains="continue"): # Full coin pouch
                    self.log_msg("Pouch is full.")
                    self.mouse.move_to(self.win.inventory_slots[0].random_point())
                    self.mouse.click()
                    break
                elif self.chatbox_text_BLACK_first_line(contains="pick") or self.chatbox_text_BLACK_first_line(contains="rogue"):
                    #self.log_msg("Success")
                    break
                elif self.chatbox_text_BLACK_first_line(contains="stunned") or self.chatbox_text_BLACK_first_line(contains="fail") or self.chatbox_text_BLACK_first_line(contains="left"): # failure messages
                    #self.log_msg("Fail")
                    self.check_hp()
                    time.sleep(3)
                    break
                counter += 1
                time.sleep(1)
                if counter == 5:
                    self.log_msg("Maybe we misclicked off the knight.")
                    break
            if self.chatbox_text_RED_dodgy_necklace(contains="crumbles"):
                dodgy_necklace_inv_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "dodgy_necklace.png")
                if dodgy_necklace := imsearch.search_img_in_rect(dodgy_necklace_inv_img, self.win.control_panel):
                    self.log_msg("Equiping another dodgy necklace.")
                    self.mouse.move_to(dodgy_necklace.random_point())
                    self.mouse.click()
                else:
                    self.log_msg("We're out of dodgy necklaces.")
                    return self.main_loop()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def get_food_img(self):
        if self.food_to_use == 'Trout':
            food_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "trout.png")
        elif self.food_to_use == 'Shark':
            food_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "shark.png")
        elif self.food_to_use == 'Salmon':
            food_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "salmon.png")
        elif self.food_to_use == 'Tuna':
            food_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "tuna.png")

        return food_img

    def click_knight(self):
        count = 0
        while True:
            if count < 10:
                knight = self.get_nearest_tag(clr.CYAN)
                if self.mouseover_text(contains="Pickpocket"):
                    self.mouse.click()
                    time.sleep(0.4)
                    break
                else:
                    self.mouse.move_to(knight.random_point())
                    # continue
            else:
                count += 1
                time.sleep(1)
                if count == 10:
                    self.log_msg("failed to find knight")
                    self.stop()  
                 
    def check_hp(self):           
        food_img = self.get_food_img()       
        current_hp = self.get_hp()
        if current_hp <= 30:
            if food := imsearch.search_img_in_rect(food_img, self.win.control_panel):
                self.mouse.move_to(food.random_point())
                self.mouse.click()
            else:
                self.log_msg("Out of food. Banking for more.")
                time.sleep(5)
                self.open_bank()
                return self.main_loop()
            
    def open_bank(self):
        # food_bank_img = self.get_food_img()
        food_img = self.get_food_img()
        dodgy_necklace_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "dodgy_necklace.png")
        # Right click to open bank
        count = 0
        while True:
            if count < 10:
                if found := self.get_nearest_tag(clr.YELLOW):
                    self.mouse.move_to(found.random_point())
                    break
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg("failed to find bank")
                self.stop() 
        self.mouse.right_click()
        if bank_text := ocr.find_text("Bank Bank", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
            self.mouse.move_to(bank_text[0].random_point(), knotsCount=0)
            self.mouse.click()
        # food_bank = self.wait_until_img(food_bank_img, self.win.game_view)
        # Wait until selected food is seen in our bank
        food = self.wait_until_img(food_img, self.win.game_view)
        dodgy_necklace = self.wait_until_img(dodgy_necklace_img, self.win.game_view)
        time.sleep(1)
        if self.search_slot_28():
            self.deposit_all()
        if dodgy_necklace:
            self.mouse.move_to(dodgy_necklace.random_point())
            self.mouse.right_click()
            if withdraw_text := ocr.find_text("6 Dodgy", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.ORANGE]):
                self.mouse.move_to(withdraw_text[0].random_point(), knotsCount=0)
                self.mouse.click()
        self.mouse.move_to(food.random_point())
        if self.mouseover_text(contains="Release"):
            self.log_msg("Ran out of food. Stopping script.")
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
                    self.mouse.click()
                    break
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
    
#This function specifically searches the 28th slot of the inventory. It returns False if the slot is empty and True if it contains any item.
    def search_slot_28(self):
        #define inventory_slots
        self.__locate_inv_slots(self.win.control_panel)
        # Create a rectangle for the 28th inventory slot
        slot_28 = self.inventory_slots[27]

        # Search for each item in the 28th inventory slot
        item_path = imsearch.BOT_IMAGES.joinpath("Aarons_images", "emptyslot.PNG")
        if search_img_in_rect(item_path, slot_28):
            self.log_msg(f"Slot 28: Empty")
            return False
        self.log_msg(f"Slot 28: Full")
        return True
    
#Make sure that this function is either imported from another file or defined in the same file before calling it.
    def __locate_inv_slots(self, cp: Rectangle) -> None:
        """
        Creates Rectangles for each inventory slot relative to the control panel, storing it in the class property.
        """
        self.inventory_slots = []
        slot_w, slot_h = 36, 32  # dimensions of a slot
        gap_x, gap_y = 6, 4  # pixel gap between slots
        y = 44 + cp.top  # start y relative to cp template
        for _ in range(7):
            x = 40 + cp.left  # start x relative to cp template
            for _ in range(4):
                self.inventory_slots.append(Rectangle(left=x, top=y, width=slot_w, height=slot_h))
                x += slot_w + gap_x
            y += slot_h + gap_y
            
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