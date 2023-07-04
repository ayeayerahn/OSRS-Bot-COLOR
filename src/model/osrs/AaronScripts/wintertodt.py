import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSwintertodt(OSRSBot):
    def __init__(self):
        bot_title = "Wintertodt"
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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

        #1. Wait for the game to start
            self.wait_till_game_start()
            self.cut_logs()
            self.fletch_logs()
            self.firemake()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def wait_till_game_start(self):
        self.wait_until_color(color=clr.GREEN, timeout=60)

    def check_is_game_ended(self):
        if self.chatbox_text_BLACK(contains="Wintertodt"):
            return self.main_loop()

    def cut_logs(self):
        if not self.search_slot_28():
            self.click_color(color=clr.CYAN) # Click on tree
        while not self.search_slot_28():
            time.sleep(1)
            
    def fletch_logs(self):
        knife_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "knife.png")
        knife = imsearch.search_img_in_rect(knife_img, self.win.control_panel)
        bruma_root_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bruma_root.png")
        bruma_root = imsearch.search_img_in_rect(bruma_root_img, self.win.control_panel)
        if bruma_root:
            if knife:
                self.mouse.move_to(knife.random_point())
                self.mouse.click()
                self.mouse.move_to(bruma_root.random_point())
                self.mouse.click()
        time.sleep(2)
        while bruma_root:
            bruma_root = imsearch.search_img_in_rect(bruma_root_img, self.win.control_panel)
            self.log_msg("Still roots in inv. Sleeping..")
            time.sleep(1)
            if self.chatbox_text_RED_first_line(contains="Fletching"):
                time.sleep(0.5)
                self.check_hp()
                return self.fletch_logs()
        self.log_msg("No roots left. Moving on.")
        
    def check_hp(self):
        whole_cake_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "cake.png")
        two_thirds_cake_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "2-3_cake.png")
        one_thirds_cake_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "slice_of_cake.png")
        whole_cake = imsearch.search_img_in_rect(whole_cake_img, self.win.control_panel)
        two_thirds_cake = imsearch.search_img_in_rect(two_thirds_cake_img, self.win.control_panel)
        one_thirds_cake = imsearch.search_img_in_rect(one_thirds_cake_img, self.win.control_panel)
        current_hp = self.get_hp()
        if current_hp < 8:
            if one_thirds_cake:
                self.mouse.move_to(one_thirds_cake.random_point())
                self.mouse.click()
            elif two_thirds_cake:
                self.mouse.move_to(two_thirds_cake.random_point())
                self.mouse.click()
            elif whole_cake:
                self.mouse.move_to(whole_cake.random_point())
                self.mouse.click()

    def firemake(self):
        bruma_kindling_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bruma_kindling.png")
        bruma_kindling = imsearch.search_img_in_rect(bruma_kindling_img, self.win.control_panel)
        self.wait_until_color(color=clr.GREEN)
        self.click_color(color=clr.GREEN)
        while bruma_kindling:
            bruma_kindling = imsearch.search_img_in_rect(bruma_kindling_img, self.win.control_panel)
            self.log_msg("Firemaking..")
            time.sleep(1)
            if self.chatbox_text_RED_first_line(contains="Cold"):
                self.log_msg("Took cold damage. Starting to firemake again.")
                return self.firemake()
            elif self.chatbox_text_RED_first_line(contains="Shattered"):
                self.log_msg("The brazier broke. Starting to firemake again.")
                return self.firemake()
            elif self.chatbox_text_RED_first_line(contains="went out"):
                return self.firemake()
        return
                

    def click_color(self, color: clr):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if count < 10:
                if found := self.get_nearest_tag(color):
                    self.mouse.move_to(found.random_point(), mouseSpeed='fastest')
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