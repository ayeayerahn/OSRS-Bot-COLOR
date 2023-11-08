import shutil
import time
from pathlib import Path

import utilities.api.item_ids as item_ids
import utilities.imagesearch as imsearch
import utilities.color as clr
import utilities.game_launcher as launcher
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSCombat(AaronFunctions):
    def __init__(self):
        bot_title = "Combat"
        description = "This."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: 200
        self.loot_items: str = self.lootables()
        self.hp_threshold: int = 35
        self.cannon = False
        self.loop_to_run = 0

    def create_options(self):
        # self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        # self.options_builder.add_text_edit_option("loot_items", "Loot items (requires re-launch):", "E.g., Coins, Dragon bones")
        # self.options_builder.add_slider_option("hp_threshold", "Low HP threshold (0-100)?", 0, 100)
        self.options_builder.add_dropdown_option("cannon", "Cannon?", ["Yes", "No"])

    def save_options(self, options: dict):
        self.running_time = 200
        if options["cannon"] == "Yes":
            self.loop_to_run = 1
        elif options["cannon"] == "No":
            self.loop_to_run = 0
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")

        # self.log_msg(f'Loot items: {self.loot_items or "None"}.')
        # self.log_msg(f"Bot will eat when HP is below: {self.hp_threshold}.")
        self.options_set = True

    def launch_game(self):
        """
        This is a somewhat impractical way of modifying a properties file prior to launching RuneLite.
        In this example, we make a copy of the default settings file, modify it according to the user's
        option selections, and then launch RuneLite with the modified settings file. Since RuneLite 1.9.11,
        it's likely more efficient to use the Profile Manager to modify settings on the fly.
        """
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return

        # Make a copy of the default settings and save locally
        src = launcher.RL_SETTINGS_FOLDER_PATH.joinpath("osrs_settings.properties")
        dst = Path(__file__).parent.joinpath("custom_settings.properties")
        shutil.copy(str(src), str(dst))

        # # Modify the highlight list
        loot_items = self.capitalize_loot_list(self.loot_items, to_list=False)
        with dst.open() as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("grounditems.highlightedItems="):
                lines[i] = f"grounditems.highlightedItems={loot_items}\n"
        with dst.open("w") as f:
            f.writelines(lines)

        # Launch the game
        launcher.launch_runelite(
            properties_path=dst,
            game_title=self.game_title,
            use_profile_manager=True,  # Important for games that use the new Profile Manager RL feature
            profile_name="OSBCCombat",  # Supply a profile name if you'd like to save it to the Profile Manager
            callback=self.log_msg,
        )

    def main_loop(self):
        # Setup API
        api_morg = MorgHTTPSocket()

        if self.loop_to_run == 1:
            self.log_msg("Running cannon loop")
        elif self.loop_to_run == 0:
            self.log_msg("Running loop without cannon")
        # failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            
            if self.loop_to_run == 1:
                self.cannon_loop(api_morg)
            else:
                self.non_cannon_loop(api_morg)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def loot_ground_items(self, api_morg):
        if self.loot_items:
            self.__loot(api_morg)
        return
            
    def return_to_cannon(self):     # Still need to test this
        self.log_msg("Returning to cannon spot.")
        cannon = self.get_nearest_tag(color=clr.GREEN)
        while True:
            try:
                self.mouse.move_to(cannon.center())
            except AttributeError:
                self.log_msg("Couldn't find the green box. Trying again.") 
                time.sleep(1) 
                continue      
            self.mouse.right_click()
            if fire_cannon := ocr.find_text("Fire", self.win.game_view, ocr.PLAIN_12, clr.OFF_WHITE):
                self.mouse.move_to(fire_cannon[0])
                self.mouse.click()
        
    def check_prayer(self):
        if self.get_prayer() <= 15:
            self.refill_cannon()
            self.prayer_pot()

    def refill_cannon(self):
        if self.chatbox_text_RED_first_line(contains="cannon") or self.chatbox_text_RED_first_line(contains="broken"):
            self.click_cannon()
        return
    
    def click_cannon(self):
        if self.mouseover_text(contains="Fire Dwarf", color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            self.log_msg("Mouse already on cannon. Just going to click.")
            self.mouse.click()
            return
        else:
            while True:
                cannon = self.get_nearest_tag(color=clr.GREEN)
                try:
                    self.mouse.move_to(cannon.center())
                except AttributeError:
                    self.log_msg("Couldn't find the green box. Trying again.")
                    time.sleep(0.5)
                    return self.click_cannon()
                self.mouse.click()
                break
            return

    def pickup_cannon(self):
        cannon = self.get_nearest_tag(color=clr.GREEN)
        while True:
            try:
                self.mouse.move_to(cannon.center())
            except AttributeError:
                self.log_msg("Couldn't find the green box. Trying again.")
                return self.pickup_cannon()
            self.mouse.right_click()
            if fire_cannon := ocr.find_text("Pick", self.win.game_view, ocr.BOLD_12, clr.WHITE):
                self.mouse.move_to(fire_cannon[0].get_center())
                self.mouse.click()
                break
        return
    
    def check_bracelet(self):
        expeditious_bracelet = imsearch.BOT_IMAGES.joinpath("Aarons_images", "expeditious_bracelet.png")
        slaughter_bracelet = imsearch.BOT_IMAGES.joinpath("Aarons_images", "bracelet_of_slaughter.png")
       
        if self.chatbox_text_RED_slayer_bracelet(contains="dust"):
            if expeditious := imsearch.search_img_in_rect(expeditious_bracelet, self.win.control_panel):
                self.mouse.move_to(expeditious.random_point())
                self.mouse.click()
            elif slaughter := imsearch.search_img_in_rect(slaughter_bracelet, self.win.control_panel):
                self.mouse.move_to(slaughter.random_point())
                self.mouse.click()
            if self.loop_to_run == 1:
                self.click_cannon()
        return
                
    def prayer_pot(self):
        super_rest_2_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(2).png")
        super_rest_3_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(3).png")
        super_rest_4_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(4).png")
        super_rest_1_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(1).png")
        self.log_msg("Prayer is low.")
        if super_rest_1 := imsearch.search_img_in_rect(super_rest_1_img, self.win.control_panel, confidence=0.04):
            self.log_msg("Found super restore (1)")
            self.mouse.move_to(super_rest_1.random_point())
            self.mouse.click()
        elif super_rest_2 := imsearch.search_img_in_rect(super_rest_2_img, self.win.control_panel, confidence=0.03):
            self.log_msg("Found super restore (2)")
            self.mouse.move_to(super_rest_2.random_point())
            self.mouse.click()
        elif super_rest_3 := imsearch.search_img_in_rect(super_rest_3_img, self.win.control_panel, confidence=0.04):
            self.log_msg("Found super restore (3)")
            self.mouse.move_to(super_rest_3.random_point())
            self.mouse.click()
        elif super_rest_4 := imsearch.search_img_in_rect(super_rest_4_img, self.win.control_panel, confidence=0.02):
            self.log_msg("Found super restore (4)")
            self.mouse.move_to(super_rest_4.random_point())
            self.mouse.click()
        time.sleep(3)
        return

    def __eat(self, api: MorgHTTPSocket):
        self.log_msg("HP is low.")
        food_slots = api.get_inv_item_indices(item_ids.all_food)
        if len(food_slots) == 0:
            self.log_msg("No food found. Pls tell me what to do...")
            self.set_status(BotStatus.STOPPED)
            return
        self.log_msg("Eating food...")
        self.mouse.move_to(self.win.inventory_slots[food_slots[0]].random_point())
        self.mouse.click()

    def __loot(self, api: MorgHTTPSocket):
        """Picks up loot while there is loot on the ground"""
        while self.pick_up_loot(self.loot_items):
            if self.search_slot_28():
                self.__logout("Inventory full. Cannot loot.")
                return
            curr_inv = len(api.get_inv())
            self.log_msg("Picking up loot...")
            for _ in range(5):  # give the bot 5 seconds to pick up the loot
                if len(api.get_inv()) != curr_inv:
                    self.log_msg("Loot picked up.")
                    time.sleep(1)
                    break
                time.sleep(1)

    def check_task_complete(self):
        if self.chatbox_text_RED(contains="Slayer"):
            self.log_msg("Task completed. Teleporting to house and stopping script.")
            self.con_cape_teleport()
            self.stop()
            
    def check_task_complete_cannon(self):
        if self.chatbox_text_RED(contains="Slayer"):
            self.log_msg("Task completed. Picking up cannon.")
            self.pickup_cannon()
            time.sleep(3)
            self.con_cape_teleport()
            self.stop()        
            
    def check_antifire(self):
        ext_super_antifire_1_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "extended_super_antifire(1).png")
        ext_super_antifire_2_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "extended_super_antifire(2).png")
        ext_super_antifire_3_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "extended_super_antifire(3).png")
        ext_super_antifire_4_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "extended_super_antifire(4).png")
        if self.chatbox_text_ANTIFIRE(contains="antifire"):
            self.log_msg("Antifire about to expire.")
            if self.chatbox_text_BLACK(contains="extended"):
                pass
            elif ext_super_antifire_1 := imsearch.search_img_in_rect(ext_super_antifire_1_img, self.win.control_panel, confidence=0.04):
                self.log_msg("Found ext super antifire (1)")
                self.mouse.move_to(ext_super_antifire_1.random_point())
                self.mouse.click()
            elif ext_super_antifire_2 := imsearch.search_img_in_rect(ext_super_antifire_2_img, self.win.control_panel, confidence=0.03):
                self.log_msg("Found ext super antifire (2)")
                self.mouse.move_to(ext_super_antifire_2.random_point())
                self.mouse.click()
            elif ext_super_antifire_3 := imsearch.search_img_in_rect(ext_super_antifire_3_img, self.win.control_panel, confidence=0.04):
                self.log_msg("Found ext super antifire (3)")
                self.mouse.move_to(ext_super_antifire_3.random_point())
                self.mouse.click()
            elif ext_super_antifire_4 := imsearch.search_img_in_rect(ext_super_antifire_4_img, self.win.control_panel, confidence=0.02):
                self.log_msg("Found ext super antifire (4)")
                self.mouse.move_to(ext_super_antifire_4.random_point())
                self.mouse.click()

    def cannon_loop(self, api_morg: MorgHTTPSocket):
        # While in combat
        while True:
            while api_morg.get_is_in_combat():
                # Check to eat food
                if self.get_hp() < self.hp_threshold:
                    self.__eat(api_morg)
                self.check_antifire()   # Not working
                self.check_prayer()
                self.refill_cannon()
                self.check_bracelet()
                self.loot_ground_items(api_morg)
                self.check_task_complete_cannon()
                time.sleep(1)

    def non_cannon_loop(self, api_morg: MorgHTTPSocket):
        failed_searches = 0
        # While not in combat
        while not api_morg.get_is_in_combat():
            self.check_task_complete()
            # Find a target
            target = self.get_nearest_tagged_NPC()
            if target is None:
                failed_searches += 1
                if failed_searches % 10 == 0:
                    self.log_msg("Searching for targets...")
                if failed_searches > 60:
                    # If we've been searching for a whole minute...
                    self.__logout("No tagged targets found. Logging out.")
                    return
                time.sleep(1)
                continue
            failed_searches = 0

            # Click target if mouse is actually hovering over it, else recalculate
            pag.moveTo(target.random_point())
            if not self.mouseover_text(contains="Attack", color=clr.OFF_WHITE):
                continue
            pag.click()
            time.sleep(1)

        # While in combat
        while api_morg.get_is_in_combat():
            # Check to eat food
            # if self.get_hp() < self.hp_threshold:
            if self.get_hp() < 40:
                self.__eat(api_morg)
                time.sleep(1)
            self.check_antifire()
            self.check_prayer()
            self.check_bracelet()
            time.sleep(1)
        # self.loot_ground_items(api_morg)

        # Loot all highlighted items on the ground
        if self.loot_items:
            self.__loot(api_morg)
            self.check_task_complete()
    
    def lootables(self) -> list:
        # issue items:
        # Snapdragon seed
        # Rune platelegs
        ITEMS = [
            "Rune med helm",
            "Mystic robe bottom (dark)", 
            "Lava Battlestaff",
            "Mystic robe top (dark)",
            "Brimstone key",
            "Rune bar",
            "Rune Battleaxe",
            "Runite bar",
            "Rune 2h sword",
            "Rune sq shield",
            "Rune kiteshield",
            "Dragon med helm",
            "Shield left half",
            "Dragon spear",
            "Ancient shard",
            "Dark totem base",
            "Dark totem middle",
            "Dark totem top",
            "Torstol seed",
            "Snape grass seed",
            "Snapdragon seed",
            "Rune chainbody",
            "Abyssal whip",
            "Abyssal dagger",
            "Grimy ranarr weed",
            "Loop half of key",
            "Tooth half of key",
            "Rune 2h sword",
            "Dragonstone",
            "Rune spear",
            "Abyssal head",
            "Ranarr seed",
            "Rune longsword",
            "Dragon javelin heads",
            "Dragon platelegs",
            "Dragon plateskirt",
            "Uncut dragonstone",
            "Rune hasta",
            "Rune platelegs",
            "Rune full helm",
            "Rune platebody",
            "Dragon longsword",
            "Dragon dagger",
            "Rune javelin",
            "Soul rune",
            "Death rune",
            "Law rune",
            "Rune arrow",
            "Dragon dart tip",
            "Runite ore",
            "Dragon arrowtips",
            "Dark bow",
            "Adamantite bar",
            "Adamantite ore",
            "Rune dagger",
            "Air battlestaff",
            "Earth battlestaff",
            "Mystic air staff",
            "Mystic earth staff",
            "Dragon chainbody",
            "Occult necklace",
            "Smoke rune",
            "Runite bolts",
            "Battlestaff"
            ]
        return ITEMS