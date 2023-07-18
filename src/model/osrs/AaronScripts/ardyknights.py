import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point


class OSRSardyknights(OSRSBot):
    def __init__(self):
        bot_title = "Ardy Knights"
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
            counter = 0
            knight = self.get_nearest_tag(color=clr.CYAN)
            if self.mouseover_text(contains="Pickpocket"):
                #self.log_msg("Mouse text found")
                self.mouse.click()
                time.sleep(0.5)
                while True:
                    if self.chatbox_text_BLACK_first_line(contains="continue"): # Full coin pouch
                        self.log_msg("Pouch is full.")
                        self.mouse.move_to(self.win.inventory_slots[0].random_point())
                        self.mouse.click()
                        break
                    elif self.chatbox_text_BLACK_first_line(contains="pick"):
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
                        
            else:
                #self.log_msg("Mouse text NOT found")
                self.mouse.move_to(knight.random_point())
                self.mouse.click()
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
                 
    def check_hp(self):
        # trout_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "trout.png")
        # trout = imsearch.search_img_in_rect(trout_img, self.win.control_panel)          
        shark_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "shark.png")
        shark = imsearch.search_img_in_rect(shark_img, self.win.control_panel)          
        current_hp = self.get_hp()
        if current_hp <= 40:
            if shark:
                self.mouse.move_to(shark.random_point())
                self.mouse.click()
            else:
                self.log_msg("Ran out of food. Stopping script.")
                self.stop()
            # if trout:
            #     self.mouse.move_to(trout.random_point())
            #     self.mouse.click()
                           
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