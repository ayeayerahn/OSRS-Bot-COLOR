import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSGOTR(OSRSBot):
    def __init__(self):
        bot_title = "<Bot name here>"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 10

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
        # Setup APIs
        api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            #guardian_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_guardian.png")
            #while not guardian_img:
                #time.sleep(1)
                #self.log_msg("Waiting for next game to start..")
            #time.sleep(15)

        #0. Start game
            guardian_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_guardian.png")
            guardian = imsearch.search_img_in_rect(guardian_img, self.win.game_view)
            while not guardian:
                time.sleep(1)
                self.log_msg("Waiting for next game to start..")
                guardian = imsearch.search_img_in_rect(guardian_img, self.win.game_view)
            self.log_msg("Found guardian image. Starting the game..")
        #1. Mine guardian remains
            for i in range(2):
                self.guardian_remains()
        #2. Wait for and click special portal when it appears
                self.special_portal()
        #2a. Mine the rocks, when inventory is full, fill pouches
                self.huge_guardian_remains(api_m)
        #2c. mine rocks until inventory is full again then leave portal
                self.special_portal()
                time.sleep(3)
        #3. Pick an altar to craft runes
                self.choose_guardian(api_m)
        #4. Craft runes
                self.click_altar(api_m)
        #5. Charge the guardian
                self.power_up_guardian(api_m)
        #6. Deposit runes
                self.deposit_runes()
        #7. Go to workbench to create more essence
            for i in range(3):
                self.gather_more_essence(api_m)
                self.choose_guardian(api_m)
                self.click_altar(api_m)
                self.power_up_guardian(api_m)
                self.deposit_runes()
            guardian_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_guardian.png")
            while not guardian_img:
                time.sleep(1)
                self.log_msg("Waiting for next game to start..")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def check_for_portal(self, api_m:MorgHTTPSocket):
        portal = self.get_nearest_tag(clr.CYAN)
        if portal:
            self.special_portal()
            self.huge_guardian_remains(api_m)
            self.special_portal()
            time.sleep(3)

    def gather_more_essence(self, api_m:MorgHTTPSocket):
        workbench = self.get_nearest_tag(clr.DARK_PURPLE) # DARK_PURPLE = Color([106, 32, 110])
        self.log_msg("Converting fragments to essence..")
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        while not api_m.get_is_inv_full():
            self.log_msg("Waiting until inventory is full..")
            time.sleep(3)
        self.fill_pouches()
        workbench = self.get_nearest_tag(clr.DARK_PURPLE) # Call this again to recreate the rectangle from the original
        self.log_msg("Converting fragments to essence..")
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        while not api_m.get_is_inv_full():
            self.log_msg("Waiting until inventory is full..")
            time.sleep(3)

    def deposit_runes(self):
        try:
            deposit = self.get_nearest_tag(clr.DARK_BLUE) # DARK_BLUE = Color([20, 95, 94])
            self.log_msg("Depositing runes..")
            self.mouse.move_to(deposit.random_point())
            self.mouse.click()
            time.sleep(5)
        except:
            AttributeError
        #self.check_for_portal()

    def power_up_guardian(self, api_m:MorgHTTPSocket):
        while not api_m.get_is_player_idle():
            self.log_msg("Heading to power up the guardian")
            time.sleep(2)
        try:
            power_up = self.get_nearest_tag(clr.DARKER_YELLOW) # DARKER_YELLOW = Color([112, 110, 17])
            self.log_msg("Powering up the guardian..")
            self.mouse.move_to(power_up.random_point())
            self.mouse.click()
            api_m.wait_til_gained_xp("Runecraft", 10)
        except:
            AttributeError
        #self.check_for_portal()

    def huge_guardian_remains(self, api_m:MorgHTTPSocket):
        while not api_m.get_is_player_idle():
            self.log_msg("Running to huge guardian_remains")
            time.sleep(2)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not api_m.get_is_inv_full():
            time.sleep(2)
        self.fill_pouches()
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not api_m.get_is_inv_full():
            time.sleep(2)

    def guardian_remains(self):
        self.log_msg("Mining guardian fragments")
        remains = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def click_altar(self, api_m: MorgHTTPSocket):
        altar = self.get_nearest_tag(clr.GREEN)
        if altar:
            self.log_msg("Crafting first set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 15)
        self.empty_pouches()
        if altar := self.get_nearest_tag(clr.GREEN):
            self.log_msg("Crafting second set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 15)
        time.sleep(1.5)
        portal = self.get_nearest_tag(clr.ORANGE)
        self.log_msg("Heading back to main area..")
        self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def special_portal(self):
        portal = self.get_nearest_tag(clr.CYAN)
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.log_msg("Waiting for portal to appear.")
            time.sleep(1)
        self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def empty_pouches(self): #Need to add proper checks for when the pouches become damaged
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[4].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[8].random_point(), mouseSpeed='fastest') # large pouch
        self.mouse.click()
        pag.keyUp('shift')

    def fill_pouches(self): #Need to add proper checks for when the pouches become damaged
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[4].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[8].random_point(), mouseSpeed='fastest') # large pouch
        self.mouse.click()

    def choose_guardian(self, api_m: MorgHTTPSocket):
        self.log_msg("Picking a guardian..")

        chaos_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_chaos.png")
        cosmic_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_cosmic.png")
        earth_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_earth.png")
        fire_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_fire.png")
        nature_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_nature.png")
        water_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_water.png")
        air_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_air.png")

        chaos_altar = imsearch.search_img_in_rect(chaos_img, self.win.game_view)
        cosmic_altar = imsearch.search_img_in_rect(cosmic_img, self.win.game_view)
        earth_altar = imsearch.search_img_in_rect(earth_img, self.win.game_view)
        fire_altar = imsearch.search_img_in_rect(fire_img, self.win.game_view)
        nature_altar = imsearch.search_img_in_rect(nature_img, self.win.game_view)
        water_altar = imsearch.search_img_in_rect(water_img, self.win.game_view)
        air_altar = imsearch.search_img_in_rect(air_img, self.win.game_view)

        try:
            if chaos_altar:
                chaos = self.get_nearest_tag(clr.ORANGE)
                self.log_msg("Going to chaos altar")
                self.mouse.move_to(chaos.random_point())
                self.mouse.click()
            elif cosmic_altar:
                cosmic = self.get_nearest_tag(clr.LIGHT_RED)
                self.log_msg("Going to cosmic altar")
                self.mouse.move_to(cosmic.random_point())
                self.mouse.click()
            elif earth_altar:
                earth = self.get_nearest_tag(clr.PURPLE)
                self.log_msg("Going to earth altar")
                self.mouse.move_to(earth.random_point())
                self.mouse.click()
            elif fire_altar:
                fire = self.get_nearest_tag(clr.PINK)
                self.log_msg("Going to fire altar")
                self.mouse.move_to(fire.random_point())
                self.mouse.click()
            elif nature_altar:
                nature = self.get_nearest_tag(clr.LIGHT_PURPLE)
                self.log_msg("Going to nature altar")
                self.mouse.move_to(nature.random_point())
                self.mouse.click()
            elif water_altar:
                water = self.get_nearest_tag(clr.BLUE)
                self.log_msg("Going to water altar")
                self.mouse.move_to(water.random_point())
                self.mouse.click()
            elif air_altar:
                air = self.get_nearest_tag(clr.DARK_YELLOW) # DARK_YELLOW = Color([149, 146, 15])
                self.log_msg("Going to air altar")
                self.mouse.move_to(air.random_point())
                self.mouse.click()
        except:
            AttributeError
        while not api_m.get_is_player_idle():
            self.log_msg("Running to guardian altar..")
            time.sleep(1)
        time.sleep(2) 
        altar = self.get_nearest_tag(clr.GREEN)
        if not altar:
            self.log_msg("Altar was dormant. Finding a new guardian altar.")
            self.choose_guardian(api_m)          

"""
        if rd.random_chance(probability=0.5):
            first_tile = self.get_nearest_tag(clr.LIGHT_PURPLE)
            self.mouse.move_to(first_tile.random_point())
            self.mouse.click()
            time.sleep(3)
        else:
            second_tile = self.get_nearest_tag(clr.MID_GREEN)
            self.mouse.move_to(second_tile.random_point())
            self.mouse.click()
            time.sleep(5)
"""