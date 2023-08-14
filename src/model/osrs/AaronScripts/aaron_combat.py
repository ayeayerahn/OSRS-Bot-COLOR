import shutil
import time
from pathlib import Path

import utilities.api.item_ids as item_ids
import utilities.imagesearch as imsearch
import utilities.color as clr
import utilities.game_launcher as launcher
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSCombat(AaronFunctions):
    def __init__(self):
        bot_title = "Combat"
        description = "This bot kills NPCs. Position your character near some NPCs and highlight them.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = 1
        self.loot_items: str = self.lootables()
        self.hp_threshold: int = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        # self.options_builder.add_text_edit_option("loot_items", "Loot items (requires re-launch):", "E.g., Coins, Dragon bones")
        self.options_builder.add_slider_option("hp_threshold", "Low HP threshold (0-100)?", 0, 100)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            # elif option == "loot_items":
            #     self.loot_items = options[option]
            elif option == "hp_threshold":
                self.hp_threshold = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f'Loot items: {self.loot_items or "None"}.')
        self.log_msg(f"Bot will eat when HP is below: {self.hp_threshold}.")
        self.log_msg("Options set successfully. Please launch RuneLite with the button on the right to apply settings.")

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
        self.log_msg("WARNING: This script is for testing and may not be safe for personal use. Please modify it to suit your needs.")

        # Setup API
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()

        self.toggle_auto_retaliate(True)

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.check_task_complete()
            # If inventory is full...
            if self.search_slot_28():
                self.log_msg("Inventory is full. Idk what to do.")
                self.set_status(BotStatus.STOPPED)
                return

            # While not in combat
            while not api_morg.get_is_in_combat():
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
                self.mouse.move_to(target.random_point())
                if not self.mouseover_text(contains="Attack", color=clr.OFF_WHITE):
                    continue
                self.mouse.click()
                time.sleep(0.5)

            # While in combat
            while api_morg.get_is_in_combat():
                # Check to eat food
                if self.get_hp() < self.hp_threshold:
                    self.__eat(api_status)
                current_prayer = self.get_prayer()
                if current_prayer <= 40:
                    self.prayer_pot()
                time.sleep(1)

            # Loot all highlighted items on the ground
            if self.loot_items:
                self.__loot(api_morg)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def refill_cannon(self):
        if self.chatbox_text_RED_first_line(contains="cannon"):
            pass

    def prayer_pot(self):
        super_rest_1_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(1).png")
        super_rest_2_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(2).png")
        super_rest_3_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(3).png")
        super_rest_4_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "super_restore(4).png")
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
        elif super_rest_4 := imsearch.search_img_in_rect(super_rest_4_img, self.win.control_panel, confidence=0.03):
            self.log_msg("Found super restore (4)")
            self.mouse.move_to(super_rest_4.random_point())
            self.mouse.click()
        time.sleep(3)
        return


    def __eat(self, api: StatusSocket):
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

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def check_task_complete(self):
        if self.chatbox_text_RED(contains="Slayer"):
            self.log_msg("Task completed. Teleporting to the crafting guild and stopping script.")
            self.craft_cape_teleport()
            self.stop()

    def lootables(self) -> list:
        ITEMS = [
            "Rune med helm",
            "Rune bar",
            "Blood rune",
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
            ""
            ]
        return ITEMS