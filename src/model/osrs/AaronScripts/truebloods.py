import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRStruebloods(OSRSBot):
    def __init__(self):
        bot_title = "True Blood RC"
        description = "<Script description here>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 360
        self.options_set = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup APIs
        # api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
    # 1. Open bank, retrieve supplies, and close bank
        # 1a. Open bank
            self.open_bank()
            time.sleep(3.5)
        # 1b. Retrieve supplies
            self.get_supplies()
            #time.sleep(0.5)
    # 2. Go to fairy ring
            self.start_run()
    # 3. Click necessary obstacles to reach the blood altar
            self.run_to_altar()
            time.sleep(3.3)
            self.enter_altar()
    #4. Craft runes
            self.click_altar()
    #5. Teleport to house to replenish run energy and return to Castle Wars to bank
            self.return_to_bank()
            self.wait_until_color(color=clr.CYAN, timeout=10)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def open_bank(self):
        self.click_color(color=clr.CYAN, contains="Use")

    def get_supplies(self):
        # Assumes pouches, active blood ess, bank tabs, and rune pouch are already in inventory
        # Assumes withdraw all is defaulted
        self.deposit_all()
        self.check_for_blood_ess()
        pure_ess_bank = imsearch.BOT_IMAGES.joinpath("Aarons_images", "pure_essence_bank.png")
        # This sequence will fill inventory with pure ess if our inventory is not already full
        if pure_ess := imsearch.search_img_in_rect(pure_ess_bank, self.win.game_view):
            self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
            self.mouse.click()
        # Fill colossal pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest', knotsCount=0) # small pouch
        self.mouse.click()
        # This sequence will fill inventory with pure ess if our inventory is not already full
        self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
        self.mouse.click()
        # Fill small and medium pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest', knotsCount=0) # small pouch
        self.mouse.click()
        # This sequence will fill inventory with pure ess if our inventory is not already full
        self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
        self.mouse.click()
        time.sleep(0.5)
        pag.press('esc')   
        time.sleep(0.5)
        self.repair_pouches()

    def run_to_altar(self):
        self.wait_until_color(color=clr.OFF_GREEN, timeout=10)
        time.sleep(0.75) # Added because you cannot instantly click after coming from a fairy ring
        self.click_color(color=clr.OFF_GREEN, contains="Enter") # First obstacle
        time.sleep(5)
        self.click_color(color=clr.BLUE, contains="Enter") # Second obstacle
        self.wait_until_color(color=clr.RED, timeout=10)
        self.click_color(color=clr.RED, contains="Enter") # Third obstacle
        self.wait_until_color(color=clr.OFF_ORANGE, timeout=10)
        self.click_color(color=clr.OFF_ORANGE, contains="Enter") # Fourth obstacle

    def enter_altar(self):
        self.click_color(color=clr.CYAN, contains="Enter")
        # altar = self.get_nearest_tag(clr.CYAN)
        # self.mouse.move_to(altar.random_point(), mouseSpeed='fastest', knotsCount=0) 
        # if self.mouseover_text(contains="Enter"):
        #     self.mouse.click()

    def click_altar(self):
        self.wait_until_color(color=clr.RED, timeout=10)
        self.click_color(color=clr.RED, contains="Craft")
        time.sleep(2.5)
        self.empty_pouches()
        self.click_color(color=clr.RED, contains="Craft")
        time.sleep(0.5)   
        self.empty_pouches()
        self.click_color(color=clr.RED, contains="Craft")
        time.sleep(0.5)     

    def empty_pouches(self):
        pag.keyDown('shift')
        while not self.mouseover_text(contains="Empty", color=clr.OFF_WHITE):
            self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        pag.keyUp('shift')

    def return_to_bank(self):
        count = 0
        # Bank with craft cape
        while True:
            if count < 10:
                self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # Place craft cape in 4th slot
                time.sleep(0.2)
                if self.mouseover_text(contains="Teleport", color=clr.OFF_WHITE):
                    self.mouse.click()
                    break
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg("failed to find cape")
                self.logout()
                self.stop() 

    def start_run(self):
        while not self.mouseover_text(contains="Tele to POH", color=clr.OFF_WHITE):
            self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        self.wait_until_color(color=clr.PURPLE, timeout=10)

        run_energy = self.get_run_energy()
        if run_energy < 25:
            self.click_color(color=clr.PURPLE, contains="Drink") # Click ornate pool
            time.sleep(3)
        self.click_color(color=clr.YELLOW, contains="Last") # Click fairy ring

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()  

    def repair_pouches(self):
        colossal_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "colossal_pouch.png")
        colossal_rune_pouch = imsearch.search_img_in_rect(colossal_rune_pouch_img, self.win.control_panel)
        if not colossal_rune_pouch:
            pag.press('esc')
            time.sleep(0.5)
            spellbook_tab = self.win.cp_tabs[6]
            self.mouse.move_to(spellbook_tab.random_point())
            self.mouse.click()
            npc_contact_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "npc_contact_on.png")
            npc_contact = imsearch.search_img_in_rect(npc_contact_img, self.win.control_panel)
            self.mouse.move_to(npc_contact.random_point())
            self.mouse.click()
            time.sleep(1)
            dark_mage_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "npc_contact_darkmage.png")
            dark_mage = imsearch.search_img_in_rect(dark_mage_img, self.win.game_view)
            self.mouse.move_to(dark_mage.random_point())
            self.mouse.click()
            time.sleep(5)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            time.sleep(1)

    def check_for_blood_ess(self):
        blood_ess_inv_active_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Blood_essence_active_inv.png")
        blood_ess_active_inv = imsearch.search_img_in_rect(blood_ess_inv_active_img, self.win.control_panel)
        if not blood_ess_active_inv:
            blood_ess_bank_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Blood_essence_bank.png")
            blood_ess_bank = imsearch.search_img_in_rect(blood_ess_bank_img, self.win.game_view)
            self.mouse.move_to(blood_ess_bank.random_point())
            self.mouse.right_click()
            if withdraw_text := ocr.find_text("Withdraw-1", self.win.game_view, ocr.BOLD_12, [clr.OFF_WHITE, clr.OFF_ORANGE]):
                self.mouse.move_to(withdraw_text[0].random_point(), knotsCount=0)
                self.mouse.click()
                time.sleep(0.5)
                pag.press('esc')
                self.mouse.move_to(self.win.inventory_slots[1].random_point())
                self.mouse.click()
                time.sleep(0.5)
                self.open_bank()
            time.sleep(1)
            
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
    
    def click_color(self, color: clr, contains: str):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if count < 10:
                self.log_msg(f"Moving to {color}...")
                if found := self.get_nearest_tag(color):
                    self.mouse.move_to(found.random_point(), mouseSpeed='fastest')
                    time.sleep(0.2)
                    if self.mouseover_text(contains, color=clr.OFF_WHITE):
                        self.mouse.click()
                        break
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg(f"failed to find {color} :(")
                self.stop() 
        return