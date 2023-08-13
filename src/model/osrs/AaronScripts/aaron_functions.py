import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path

class AaronFunctions(OSRSBot):
    def __init__(self, bot_title, description) -> None:
        super().__init__(bot_title, description)

    def activate_special(self):
        """Activates the special attack of the equipped weapon."""
        spec_energy = self.get_special_energy()
        if spec_energy >= 100:
            self.mouse.move_to(self.win.spec_orb.random_point())
            self.mouse.click()
            return True

    def click_color(self, color: clr):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if found := self.get_nearest_tag(color):
                if count < 10:
                    self.mouse.move_to(found.random_point())
                    if self.mouse.click(check_red_click=True):
                        break
                    else:
                        count += 1
                        time.sleep(1) 
                else:
                    count += 1
                    time.sleep(1)
                    if count == 10:
                        self.log_msg("We misclicked 10 times. Stopping script.")
                        self.stop()
            else:
                self.log_msg("failed to find object to click. Stopping script.")
                self.stop() 
        return
    
    def is_bank_open(self):
        """Checks if the bank is open, if not, opens it
        Returns:
            True if the bank is open, False if not
        Args:
            None"""
        # Define the image to search for in the bank interface
        deposit_all_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png")

        # Set a time limit for searching for the image
        end_time = time.time() + 2

        # Loop until the time limit is reached
        while (time.time() < end_time):
            # Check if the image is found in the game view
            if deposit_btn := imsearch.search_img_in_rect(deposit_all_img, self.win.game_view):
                return True

            # Sleep for a short time to avoid excessive CPU usage
            time.sleep(.2)

        # If the image was not found within the time limit, return False
        return False

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click() 
            return
        
    def open_bank_af(self):
        """
        This will bank all logs in the inventory.
        Returns: 
            void
        Args: 
            deposit_slots (int) - Inventory position of each different item to deposit.
        """
        # move mouse to bank and click while not red click
        bank = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(bank.random_point())
        while not self.mouse.click(check_red_click=True):
            bank = self.get_nearest_tag(clr.CYAN)
            self.mouse.move_to(bank.random_point())

        wait_time = time.time()
        while not self.is_bank_open():
            if time.time() - wait_time > 20:
                self.mouse.move_to(bank.random_point())
                while not self.mouse.click(check_red_click=True):
                    bank = self.get_nearest_tag(clr.CYAN)
                    self.mouse.move_to(bank.random_point())
            # if we waited for 17 seconds, break out of loop
            if time.time() - wait_time > 30:
                self.log_msg("We clicked on the bank but bank is not open after 12 seconds, bot is quiting...")
                self.stop()
        return

            
    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time) 

    def craft_cape_teleport(self):
        craft_cape_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "crafting_cape(t).png")
        if craft_cape := imsearch.search_img_in_rect(craft_cape_img, self.win.control_panel):
            self.mouse.move_to(craft_cape.random_point())
            self.mouse.click()
        time.sleep(3)
    
    def wait_until_img(self, img: Path, screen: Rectangle, timeout: int = 10):
        """this will wait till img shows up in screen"""
        time_start = time.time()
        while True:
            if found := imsearch.search_img_in_rect(img, screen):
                break
            if time.time() - time_start > timeout:
                self.log_msg(f"We've been waiting for {timeout} seconds, something is wrong...stopping.")
                self.stop()
        return found    
    
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