import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRStruebloods(OSRSBot):
    def __init__(self):
        bot_title = "True Blood RC"
        description = "<Script description here>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 10

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
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
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
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
            while not api_m.get_is_player_idle():
                time.sleep(1)
        # 1b. Retrieve supplies
            self.get_supplies(api_m)
            time.sleep(0.5)
    # 2. Go to fairy ring
        # 2a. Teleport via ardy cape
            self.ardy_cape_teleport()
            while not api_m.get_is_player_idle():
                time.sleep(1)
            tile = self.get_nearest_tag(clr.ORANGE)
            self.mouse.move_to(tile.random_point())
            self.mouse.click()
            while not api_m.get_is_player_idle():
                time.sleep(0.5)    
            second_tile = self.get_nearest_tag(clr.CYAN)
            self.mouse.move_to(second_tile.random_point())
            self.mouse.click()
            while not api_m.get_is_player_idle():
                time.sleep(0.5)           
        # # 2b. Locate and click quest icon on minimap
            # self.locate_quest_icon()
            # while not api_m.get_is_player_idle():
            #     time.sleep(0.5) 
        # # 2c. Locate and click fairy ring
            self.click_fairy_ring()
            while not api_m.get_is_player_idle():
                time.sleep(1) 
    # 3. Click necessary obstacles to reach the blood altar
            self.run_to_altar()
            time.sleep(3.3)
            self.enter_altar()
    #4. Craft runes
            self.click_altar(api_m)
    #5. Teleport to house to replenish run energy and return to Castle Wars to bank
            self.return_to_bank()
            time.sleep(5)

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
    # add a check if the blood essence is in the inventory
        # Assumes pouches, active blood ess, bank tabs, and rune pouch are already in inventory
        # Assumes withdraw all is defaulted
        self.deposit_all()
        self.check_for_blood_ess()
        pure_ess_bank = imsearch.BOT_IMAGES.joinpath("Aarons_images", "pure_essence_bank.png")
        # This sequence will fill inventory with pure ess if our inventory is not already full
        if not api_m.get_is_inv_full():
            if pure_ess := imsearch.search_img_in_rect(pure_ess_bank, self.win.game_view):
                self.mouse.move_to(pure_ess.random_point())
                self.mouse.click()
        #time.sleep(1)
        # Fill small and giant pouch
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[4].random_point()) # medium pouch
        self.mouse.click()
        time.sleep(1)
        if self.chatbox_text_RED(contains='Your rune pouch has decayed'):
            self.repair_pouches(api_m)
            self.open_bank()
        time.sleep(0.5)
        # This sequence will fill inventory with pure ess if our inventory is not already full
        if not api_m.get_is_inv_full():
            if pure_ess := imsearch.search_img_in_rect(pure_ess_bank, self.win.game_view):
                self.mouse.move_to(pure_ess.random_point())
                self.mouse.click()
        # Fill small and medium pouch
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[5].random_point()) # medium pouch
        self.mouse.click()
        #time.sleep(0.5)
        # This sequence will fill inventory with pure ess if our inventory is not already full
        if not api_m.get_is_inv_full():
            if pure_ess := imsearch.search_img_in_rect(pure_ess_bank, self.win.game_view):
                self.mouse.move_to(pure_ess.random_point())
                self.mouse.click()
        time.sleep(0.5)
        pag.press('esc')

    def ardy_cape_teleport(self):
        ardy_cape_inv = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ardougne_cloak_1.png")
        self.mouse.move_to(self.win.cp_tabs[4].random_point())
        self.mouse.click()
        time.sleep(0.5)
        if ardy_cape := imsearch.search_img_in_rect(ardy_cape_inv, self.win.control_panel):
            self.mouse.move_to(ardy_cape.random_point())
            self.mouse.click()
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()        

    def locate_quest_icon(self):
        quest_icon_minimap = imsearch.BOT_IMAGES.joinpath("Aarons_images", "quest_start_icon.png")
        if quest_icon := imsearch.search_img_in_rect(quest_icon_minimap, self.win.minimap):
            self.mouse.move_to(quest_icon.random_point())
            self.mouse.click()

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
        self.empty_pouches_first()
        if altar := self.get_nearest_tag(clr.RED):
            self.log_msg("Crafting second set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        self.empty_pouches_second()
        if altar := self.get_nearest_tag(clr.RED):
            self.log_msg("Crafting third set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        time.sleep(1.5) # Gives enough time to let your character become idle

    def empty_pouches_first(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[4].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        pag.keyUp('shift')

    def empty_pouches_second(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[5].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        pag.keyUp('shift')

    def return_to_bank(self):
        self.mouse.move_to(self.win.inventory_slots[6].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        time.sleep(5)

        pool = self.get_nearest_tag(clr.PURPLE)
        self.mouse.move_to(pool.random_point(), mouseSpeed='fast')
        self.mouse.click()
        time.sleep(3)

        jewel_box = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(jewel_box.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()  

    def repair_pouches(self, api_m: MorgHTTPSocket):
        large_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "large_pouch.png")
        giant_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "giant_pouch.png")
        large_rune_pouch = imsearch.search_img_in_rect(large_rune_pouch_img, self.win.inventory_slots[2])
        giant_rune_pouch = imsearch.search_img_in_rect(giant_rune_pouch_img, self.win.inventory_slots[3])
        if not large_rune_pouch or not giant_rune_pouch:
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
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
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
                self.mouse.move_to(self.win.inventory_slots[2].random_point())
                self.mouse.click()
                time.sleep(0.5)
                self.open_bank()
            time.sleep(0.5)