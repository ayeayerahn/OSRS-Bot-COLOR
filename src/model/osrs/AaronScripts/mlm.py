import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSmlm(OSRSBot):
    def __init__(self):
        bot_title = "MLM"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1000

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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Mine sequence
            while not self.search_slot_28():
                self.mine_ore()
                counter = 0
                while counter < 60:
                    if self.chatbox_text_RED_first_line(contains="idle"):
                        self.log_msg("Idle.")
                        return self.main_loop()
                    if self.chatbox_text_QUEST(contains="inventory"):
                        self.log_msg("Inventory full.")
                        break
                    counter += 1
                    time.sleep(1)
            # Run to deposit pay-dirt
            self.deposit_paydirt()
            # Collect ores
            self.collect_ore()     
            # Bank ores
            self.bank_ores()
            
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()   
        
    def bank_ores(self):    
        self.click_color(clr.CYAN)
        time.sleep(5)
        self.deposit_all()
        time.sleep(1)
        pag.press("escape")
        time.sleep(1)
        return self.main_loop()
        
    def mine_ore(self):
        self.click_color(clr.YELLOW)
        counter = 0
        while not self.chatbox_text_BLACK_first_line("swing"):
            time.sleep(1)
            counter += 1
            if self.chatbox_text_QUEST(contains="inventory"):
                self.log_msg("Inventory full.")
                break
            if counter == 10:
                return self.mine_ore()
        
    def deposit_paydirt(self):
        self.click_color(clr.GREEN)
        counter = 0
        while True:
            if self.chatbox_text_BLACK(contains="ore is ready to be collected"):
                break
            if self.chatbox_text_QUEST(contains="The"): # Wheels are broken
                time.sleep(1)
                return self.repair_wheel()
            if self.chatbox_text_QUEST(contains="put in the hopper"):
                return self.bank_ores()
            counter += 1    
            time.sleep(1)
            if counter == 20:
                return self.deposit_paydirt()
        
    def collect_ore(self):
        self.click_color(clr.RED)
        counter = 0
        while True:
            if self.chatbox_text_QUEST("You"):
                break   
            counter += 1
            time.sleep(1)
            if counter == 10:
                self.log_msg("Maybe we misclicked the collect sack.")
                return self.collect_ore()   
        time.sleep(1)

    def repair_wheel(self):
        wheel = self.get_nearest_tag(clr.PINK)
        self.mouse.move_to(wheel.random_point())
        self.mouse.click()
        time.sleep(15)
       
    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click() 
        else:
            return self.bank_ores()
                           
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