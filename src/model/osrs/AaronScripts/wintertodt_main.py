import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point


class OSRSwintertodt_main(OSRSBot):
    def __init__(self):
        bot_title = "Wintertodt"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1000
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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

        #1. Wait for the game to start
            self.cut_logs()
            self.fletch_logs()
            self.firemake()
            self.return_to_bank()
            self.bank_items()
            self.return_to_start()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def return_to_start(self):
        self.click_color(color=clr.PINK)
        time.sleep(8)
        self.click_color(color=clr.GREEN)
        self.log_msg("Waiting for next game to begin..")
        while True:
            time.sleep(1)
            if self.chatbox_text_RED_first_line(contains="Wintertodt"):
                time.sleep(2)
                break
            if self.chatbox_text_BLACK(contains="Kourend"):
                time.sleep(2)
                break
            
    def bank_items(self):
        supply_crate_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "supply_crate.png")
        supply_crate = imsearch.search_img_in_rect(supply_crate_img, self.win.control_panel)          
        shark_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "shark.png")
        shark_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "shark_bank.png")
        shark = imsearch.search_img_in_rect(shark_img, self.win.control_panel)          
        shark_bank = imsearch.search_img_in_rect(shark_img, self.win.game_view)          
        if supply_crate:
            self.mouse.move_to(supply_crate.random_point())
            self.mouse.click()
        else:
            self.log_msg("No supply crate found in your inventory.")
        time.sleep(0.5)          
        while True:
            if shark := imsearch.search_img_in_rect(shark_img, self.win.inventory_slots[2]):
                if shark := imsearch.search_img_in_rect(shark_img, self.win.inventory_slots[1]):
                    self.log_msg("We have at least three shark.. Exiting bank.")
                    break
                else:
                    self.mouse.move_to(shark_bank.random_point())
                    self.mouse.click()
                    time.sleep(0.5)
                    self.mouse.click() 
                    break
            # shark = imsearch.search_img_in_rect(shark, self.win.control_panel)                  
            if not shark:
                self.log_msg("No shark in your inventory.")
                if shark_bank := imsearch.search_img_in_rect(shark_bank_img, self.win.game_view):
                    self.log_msg("Withdrawing two shark.")
                    self.mouse.move_to(shark_bank.random_point())
                    self.mouse.click()
                    time.sleep(0.5)
                    self.mouse.click() 
                    time.sleep(0.5)
                    self.mouse.click() 
                    break                   
            else:
                self.log_msg("No more food. Stopping the script..")
                self.stop()
        time.sleep(1)
        pag.press('esc')
        time.sleep(1)

    def return_to_bank(self):
        self.log_msg("Returning to bank")
        self.click_color(color=clr.PINK)
        while True:
            if self.chatbox_text_BLACK(contains="subdued"):
                break
            if self.chatbox_text_BLACK(contains="Kourend"):
                break
            time.sleep(1)
        self.poh_tele()
        self.click_color(color=clr.CYAN)
        time.sleep(8)

    def wait_till_game_start(self):
        self.wait_until_color(color=clr.YELLOW, timeout=60)

    def check_is_game_ended(self):
        if self.chatbox_text_BLACK(contains="Wintertodt"):
            return self.main_loop()

    def cut_logs(self):
        idle_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "IDLE.png")
        idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
        woodcutting_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "woodcutting.png")
        woodcutting = imsearch.search_img_in_rect(woodcutting_img, self.win.game_view)        
        if not self.search_slot_28():
            self.click_color(color=clr.CYAN) # Click on tree
        counter = 0
        while True:
            self.log_msg("Running to cut logs")
            time.sleep(1)
            woodcutting = imsearch.search_img_in_rect(woodcutting_img, self.win.game_view) 
            if woodcutting:
                break    
            counter += 1
            if counter == 10:
                self.log_msg("We probably misclicked the tree. Trying again.")
                return self.cut_logs()
        counter = 0               
        self.log_msg("Woodcutting")
        while True:
            time.sleep(0.5)
            self.check_hp()
            idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
            if self.chatbox_text_RED(contains="Inventory"):
                break
            if self.chatbox_text_BLACK_first_line(contains="seeps"):
                self.check_hp()
                time.sleep(2)
                if idle:
                    return self.cut_logs()
        self.check_hp()
            
    def fletch_logs(self):
        knife_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "knife.png")
        knife = imsearch.search_img_in_rect(knife_img, self.win.control_panel)
        bruma_root_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bruma_root.png")
        bruma_root = imsearch.search_img_in_rect(bruma_root_img, self.win.control_panel)
        idle_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "IDLE.png")
        idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
        if bruma_root:
            if knife:
                self.mouse.move_to(knife.random_point())
                self.mouse.click()
                self.mouse.move_to(bruma_root.random_point())
                self.mouse.click()
        time.sleep(2)
        self.log_msg("Fletching..")
        while bruma_root:
            bruma_root = imsearch.search_img_in_rect(bruma_root_img, self.win.control_panel)
            time.sleep(1)
            idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
            if idle:
                time.sleep(0.5)
                self.check_hp()
                return self.fletch_logs()
        self.log_msg("No roots left. Moving on.")
        
    def check_hp(self):         
        shark_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "shark.png")
        shark = imsearch.search_img_in_rect(shark_img, self.win.control_panel)          
        current_hp = self.get_hp()
        if current_hp <= 25:
            if shark:
                self.mouse.move_to(shark.random_point())
                self.mouse.click()

    def firemake(self):
        bruma_kindling_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bruma_kindling.png")
        bruma_kindling = imsearch.search_img_in_rect(bruma_kindling_img, self.win.control_panel)
        idle_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "IDLE.png")
        idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
        if bruma_kindling:
            self.click_color(color=clr.YELLOW)
        time.sleep(3)
        self.log_msg("Firemaking..")
        while bruma_kindling:
            bruma_kindling = imsearch.search_img_in_rect(bruma_kindling_img, self.win.control_panel)
            time.sleep(0.5)
            idle = imsearch.search_img_in_rect(idle_img, self.win.game_view)
            if idle:
                self.log_msg("Took damage.. checking health and firemaking until inv is empty.")
                time.sleep(0.5)
                self.check_hp()
                return self.firemake()
        return
                
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
            
    def poh_tele(self):
        count = 0
        # Bank with craft cape
        while True:
            if count < 10:
                self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # Place con cape in 4th slot
                time.sleep(0.2)
                if self.mouseover_text(contains="Tele", color=clr.OFF_WHITE):
                    self.mouse.click()
                    break
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg("failed to find cape")
                self.logout()
                self.stop()
        self.wait_until_color(color=clr.PURPLE)
        self.click_color(color=clr.PURPLE)
        time.sleep(3)
        self.click_color(color=clr.RED)
        time.sleep(5)