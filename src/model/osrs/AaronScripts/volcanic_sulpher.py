import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import pyautogui as pag
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


class OSRSvolcanicsulpher(AaronFunctions):
    def __init__(self):
        bot_title = "Volcanic Sulpher"
        description = ""
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 500
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
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            volcanic_sulpher = self.get_nearest_tag(clr.GREEN)
            if self.search_slot_28():
                self.drop_all()
            if volcanic_sulpher:
                self.mouse.move_to(volcanic_sulpher.random_point())
                self.mouse.click()
                while volcanic_sulpher:
                    volcanic_sulpher = self.get_nearest_tag(clr.GREEN)
                    if self.search_slot_28():
                        self.drop_all()
                        break
                    time.sleep(1)
            time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def get_supplies(self):
        # Assumes pouches, active blood ess, bank tabs, and rune pouch are already in inventory
        # Assumes withdraw all is defaulted
        # self.deposit_all()
        self.check_for_blood_ess()
        pure_ess_bank = imsearch.BOT_IMAGES.joinpath("Aarons_images", "pure_essence_bank.png")
        # This sequence will fill inventory with pure ess if our inventory is not already full
        if pure_ess := imsearch.search_img_in_rect(pure_ess_bank, self.win.game_view):
            self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
            self.mouse.click()
            time.sleep(0.5)
        # Fill colossal pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest', knotsCount=0) # small pouch
        self.mouse.click()
        time.sleep(0.5)
        # This sequence will fill inventory with pure ess if our inventory is not already full
        self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
        self.mouse.click()
        time.sleep(0.5)
        # Fill small and medium pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest', knotsCount=0) # small pouch
        self.mouse.click()
        time.sleep(0.5)
        # This sequence will fill inventory with pure ess if our inventory is not already full
        self.mouse.move_to(pure_ess.random_point(), mouseSpeed='fastest', knotsCount=0)
        self.mouse.click()
        time.sleep(0.3)
        pag.press('esc')   
        time.sleep(0.5)
        # self.repair_pouches()

    def run_to_altar(self):
        self.wait_until_color(color=clr.OFF_GREEN, timeout=10)
        time.sleep(0.75) # Added because you cannot instantly click after coming from a fairy ring
        # self.click_color(color=clr.OFF_GREEN, contains="Enter") # First obstacle
        self.click_color_af(color=clr.OFF_GREEN) # First obstacle
        time.sleep(5)
        # self.click_color(color=clr.BLUE, contains="Enter") # Second obstacle
        self.click_color_af(color=clr.BLUE) # Second obstacle
        self.wait_until_color(color=clr.RED, timeout=10)
        # self.click_color(color=clr.RED, contains="Enter") # Third obstacle
        self.click_color_af(color=clr.RED) # Third obstacle
        self.wait_until_color(color=clr.OFF_ORANGE, timeout=10)
        # self.click_color(color=clr.OFF_ORANGE, contains="Enter") # Fourth obstacle
        time.sleep(0.2)
        self.click_color_af(color=clr.ORANGE) # Fourth obstacle

    def enter_altar(self):
        # self.click_color(color=clr.CYAN, contains="Enter")
        self.click_color_af(color=clr.CYAN)

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
        self.craft_cape_teleport()

    def start_run(self):
        self.con_cape_teleport()
        self.wait_until_color(color=clr.PURPLE, timeout=10)

        if self.get_run_energy() < 25:
            self.click_color_af(color=clr.PURPLE) # Click ornate pool
            time.sleep(3)
        self.click_color_af(color=clr.YELLOW) # Click fairy ring

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
                self.open_bank_af()
            time.sleep(1)
    
    def click_color(self, color: clr, contains: str = None):
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