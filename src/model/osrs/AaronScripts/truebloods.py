import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


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
        api_m = MorgHTTPSocket()
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
            time.sleep(4)
        # 1b. Retrieve supplies
            self.get_supplies(api_m)
            time.sleep(0.5)
    # 2. Go to fairy ring
            self.start_run()
    # 3. Click necessary obstacles to reach the blood altar
            self.run_to_altar()
            time.sleep(3.3)
            self.enter_altar()
    #4. Craft runes
            self.click_altar(api_m)
    #5. Teleport to house to replenish run energy and return to Castle Wars to bank
            self.return_to_bank()
            time.sleep(4)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Bank"):
            self.mouse.move_to(banker.random_point()) 
        self.mouse.click()


    def get_supplies(self, api_m:MorgHTTPSocket):
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
        self.mouse.move_to(pure_ess.random_point(), knotsCount=0)
        self.mouse.click()
        # Fill small and medium pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest', knotsCount=0) # small pouch
        self.mouse.click()
        # This sequence will fill inventory with pure ess if our inventory is not already full
        self.mouse.move_to(pure_ess.random_point(), knotsCount=0)
        self.mouse.click()
        while not api_m.get_is_inv_full():
            time.sleep(0.5)
        pag.press('esc')   
        self.repair_pouches(api_m)

    def click_fairy_ring(self):
        fairy_ring = self.get_nearest_tag(clr.YELLOW)
        if not self.mouseover_text(contains="Last"):
            self.mouse.move_to(fairy_ring.random_point()) 
        self.mouse.click()

    def run_to_altar(self):
        first_obstacle = self.get_nearest_tag(clr.GREEN)
        while not first_obstacle:
            first_obstacle = self.get_nearest_tag(clr.GREEN)
            time.sleep(1)
        self.mouse.move_to(first_obstacle.random_point()) 
        self.mouse.click()
        time.sleep(4.8)

        second_obstacle = self.get_nearest_tag(clr.BLUE)
        self.mouse.move_to(second_obstacle.random_point()) 
        self.mouse.click()      

        third_obstacle = self.get_nearest_tag(clr.RED)
        while not third_obstacle:
            third_obstacle = self.get_nearest_tag(clr.RED)
            time.sleep(0.5)
        self.mouse.move_to(third_obstacle.random_point()) 
        self.mouse.click()
        time.sleep(9.5)

        fourth_obstacle = self.get_nearest_tag(clr.ORANGE)
        self.mouse.move_to(fourth_obstacle.random_point()) 
        self.mouse.click()

    def enter_altar(self):
        altar = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Enter"):
            self.mouse.move_to(altar.random_point()) 
        self.mouse.click()

    def click_altar(self, api_m: MorgHTTPSocket):
        altar = self.get_nearest_tag(clr.RED)
        while not altar:
            time.sleep(1)
            altar = self.get_nearest_tag(clr.RED)           
        if altar:
            self.log_msg("Crafting first set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 10)
        self.empty_pouches()
        if altar := self.get_nearest_tag(clr.RED):
            self.log_msg("Crafting second set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 2)
        self.empty_pouches()
        if altar := self.get_nearest_tag(clr.RED):
            self.log_msg("Crafting third set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 1)

    def empty_pouches(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        pag.keyUp('shift')

    def return_to_bank(self):
        # Bank with craft cape
        self.mouse.move_to(self.win.inventory_slots[7].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()

    def start_run(self):
        self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        fairy_ring = self.get_nearest_tag(clr.YELLOW)
        while not fairy_ring:
            fairy_ring = self.get_nearest_tag(clr.YELLOW)
            time.sleep(0.5)

        run_energy = self.get_run_energy()
        if run_energy < 25:
            pool = self.get_nearest_tag(clr.PURPLE)
            self.mouse.move_to(pool.random_point(), mouseSpeed='fast')
            self.mouse.click()
            time.sleep(3)
        fairy_ring = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(fairy_ring.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()  

    def repair_pouches(self, api_m: MorgHTTPSocket):
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
            api_m.wait_til_gained_xp('Magic', 10)
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
            if withdraw_text := ocr.find_text("Withdraw-1", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.OFF_ORANGE]):
                self.mouse.move_to(withdraw_text[0].random_point(), knotsCount=0)
                self.mouse.click()
                time.sleep(0.5)
                pag.press('esc')
                self.mouse.move_to(self.win.inventory_slots[1].random_point())
                self.mouse.click()
                time.sleep(0.5)
                self.open_bank()
            time.sleep(1)