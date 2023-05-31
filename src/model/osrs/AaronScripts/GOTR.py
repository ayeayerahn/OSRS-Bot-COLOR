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
        bot_title = "GOTR"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 100

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
    #0. Start game
    #1. Begin game
            self.activate_spec()
            if api_m.get_inv_item_stack_amount(item_id=26878) < 43:
                self.log_msg("Not enough guardian fragments.. starting the special portal sequence")
                self.special_portal_sequence(api_m)
            self.normal_sequence(api_m)
            self.is_guardian_defeated()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def is_guardian_defeated(self):
        if self.chatbox_text_GREEN(contains="The Great Guardian successfully closed the rift"):
            while not self.chatbox_text_RED(contains="The rift becomes active!"):
                self.log_msg("Waiting for new game to start..")
                time.sleep(1)

    def gather_more_essence(self, api_m:MorgHTTPSocket):
        workbench = self.get_nearest_tag(clr.DARK_PURPLE) # DARK_PURPLE = Color([106, 32, 110])
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Converting fragments to essence..")
        if portal: # Check if portal has spawned
            portal = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        self.log_msg("Waiting until inventory is full..")
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            time.sleep(1)
        self.fill_pouches(api_m)
        while not portal: # Check if portal has spawned
            workbench = self.get_nearest_tag(clr.DARK_PURPLE) # Call this again to recreate the rectangle from the original
            self.mouse.move_to(workbench.random_point())
            self.mouse.click()
            while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
                time.sleep(1)
            break
        self.huge_guardian_remains(api_m)
        self.special_portal(api_m)
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            time.sleep(1)

    def deposit_runes(self, api_m:MorgHTTPSocket):
        self.log_msg("Heading to deposit runes")
        deposit = self.get_nearest_tag(clr.DARK_BLUE)
        try:
            deposit = self.get_nearest_tag(clr.DARK_BLUE) # DARK_BLUE = Color([20, 95, 94])
            self.mouse.move_to(deposit.random_point())
            self.mouse.click()
        except:
            AttributeError
        # while not api_m.get_is_player_idle():
        #     time.sleep(2)
        while not self.chatbox_text_BLACK(contains=f"You deposit all of your runes into the pool"):
            time.sleep(1)
        time.sleep(0.5)

    def power_up_guardian(self, api_m:MorgHTTPSocket):
        power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
        while not power_up:
            power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
            time.sleep(1)
        try:
            #power_up = self.get_nearest_tag(clr.DARKER_YELLOW) # DARKER_YELLOW = Color([112, 110, 17])
            self.log_msg("Powering up the guardian..")
            self.mouse.move_to(power_up.random_point())
            self.mouse.click()
            api_m.wait_til_gained_xp("Runecraft", 10)
            pag.press('space') # In case the game ends before we get to deposit the last batch
        except:
            AttributeError

    def huge_guardian_remains(self, api_m:MorgHTTPSocket):
        self.log_msg("Running to huge guardian remains")
        # while not api_m.get_is_player_idle():
        #     time.sleep(2)
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            time.sleep(1)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            time.sleep(1)
        # while not api_m.get_is_player_idle():
        #     time.sleep(2)
        self.fill_pouches(api_m)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        # while not api_m.get_is_player_idle():
        #     time.sleep(2)
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            time.sleep(1)

    def guardian_remains(self):
        self.log_msg("Mining guardian fragments")
        remains = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def click_altar(self, api_m: MorgHTTPSocket):
        altar = self.get_nearest_tag(clr.GREEN)
        while not altar:
            time.sleep(1)
            altar = self.get_nearest_tag(clr.GREEN)           
        if altar:
            self.log_msg("Crafting first set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 10)
        self.empty_pouches()
        if altar := self.get_nearest_tag(clr.GREEN):
            self.log_msg("Crafting second set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        time.sleep(1.5) # Gives enough time to let your character become idle
        if portal := self.get_nearest_tag(clr.ORANGE):
            self.log_msg("Heading back to main area..")
            self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
            self.mouse.click()
        # while not api_m.get_is_player_idle():
        #     time.sleep(2)
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself back in the temple"):
            time.sleep(1)

    def special_portal(self, api_m: MorgHTTPSocket):
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            time.sleep(1)
        self.mouse.move_to(portal.random_point())
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!'):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()

    def empty_pouches(self): #Need to add proper checks for when the pouches become damaged
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest') # large pouch
        self.mouse.click()
        pag.keyUp('shift')

    def fill_pouches(self, api_m: MorgHTTPSocket): #Need to add proper checks for when the pouches become damaged
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest') # large pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)

    def repair_pouches(self, api_m: MorgHTTPSocket):
        if self.chatbox_text_RED(contains='Your rune pouch has decayed'):
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
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            time.sleep(1)


    def choose_guardian(self, api_m: MorgHTTPSocket):

        # Need to figure out a solution to seeing the same altar message for back to back sequences

        self.log_msg("Picking a guardian..")

        chaos_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_chaos.png")
        cosmic_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_cosmic.png")
        earth_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_earth.png")
        fire_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_fire.png")
        nature_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_nature.png")
        water_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_water.png")
        air_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_air.png")
        law_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_law.png")


        chaos_pillar = imsearch.search_img_in_rect(chaos_img, self.win.game_view)
        cosmic_pillar = imsearch.search_img_in_rect(cosmic_img, self.win.game_view)
        earth_pillar = imsearch.search_img_in_rect(earth_img, self.win.game_view)
        fire_pillar = imsearch.search_img_in_rect(fire_img, self.win.game_view)
        nature_pillar = imsearch.search_img_in_rect(nature_img, self.win.game_view)
        water_pillar = imsearch.search_img_in_rect(water_img, self.win.game_view)
        air_pillar = imsearch.search_img_in_rect(air_img, self.win.game_view)
        law_pillar = imsearch.search_img_in_rect(law_img, self.win.game_view)

        if law_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_PURPLE)
            chosen_altar = 'Law'   
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)   
        elif chaos_pillar:
            altar = self.get_nearest_tag(clr.ORANGE)
            chosen_altar = 'Chaos'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)
        elif nature_pillar:
            altar = self.get_nearest_tag(clr.DARK_GREEN)
            chosen_altar = 'Nature'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m) 
        elif fire_pillar:
            altar = self.get_nearest_tag(clr.PINK)
            chosen_altar = 'Fire'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)
        elif cosmic_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_RED)
            chosen_altar = 'Cosmic'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m) 
        elif earth_pillar:
            altar = self.get_nearest_tag(clr.PURPLE)
            chosen_altar = 'Earth'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m) 
        elif water_pillar:
            altar = self.get_nearest_tag(clr.BLUE)
            chosen_altar = 'Water'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)
        elif air_pillar:
            altar = self.get_nearest_tag(clr.DARK_YELLOW) # DARK_YELLOW = Color([149, 146, 15])
            chosen_altar = 'Air'
            if self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)
        
        self.log_msg(f"Going to {chosen_altar} altar")
        try:
            self.mouse.move_to(altar.random_point(), mouseSpeed = 'fastest')
            self.mouse.click()
        except AttributeError:
            self.log_msg(f"Could not locate {chosen_altar} pillar")
            return self.choose_guardian(api_m)

        while not self.chatbox_text_BLACK(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
            time.sleep(1)
            if self.chatbox_text_QUEST(contains="The Guardian is dormant. Its energy might return soon."):
                pag.press('space')
                self.log_msg("Altar was dormant. Trying again")
                chosen_altar = None
                self.choose_guardian(api_m)
                break
        self.log_msg(f"Successfully entered the {chosen_altar} altar room!!")

    def special_portal_sequence(self, api_m:MorgHTTPSocket):
        self.guardian_remains()
        self.special_portal(api_m)
        self.huge_guardian_remains(api_m)
        self.special_portal(api_m)
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            time.sleep(1)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        self.deposit_runes(api_m)

    def normal_sequence(self, api_m:MorgHTTPSocket):
        self.gather_more_essence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        self.deposit_runes(api_m)   

    def activate_spec(self):
        spec_energy = self.get_special_energy()
        if spec_energy >= 100:
            self.mouse.move_to(self.win.spec_orb.random_point())
            self.mouse.click()  

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

        self.is_guardian_defeated(self)
            for i in range(2):
                self.guardian_remains()
    #2. Wait for and click special portal when it appears
                self.special_portal(api_m)
    #2a. Mine the rocks, when inventory is full, fill pouches
                self.huge_guardian_remains(api_m)
    #2c. mine rocks until inventory is full again then leave portal
                self.special_portal(api_m)
                #time.sleep(3.5)
    #3. Pick an altar to craft runes
                self.choose_guardian(api_m)
    #4. Craft runes
                self.click_altar(api_m)
    #5. Charge the guardian
                self.power_up_guardian(api_m)
    #6. Deposit runes
                self.deposit_runes(api_m)
    #7. Go to workbench to create more essence
            self.gather_more_essence(api_m)
            self.choose_guardian(api_m)
            self.click_altar(api_m)
            time.sleep(1)
            self.deposit_runes(api_m)  
            for i in range(2):
                self.gather_more_essence(api_m)
                self.power_up_guardian(api_m)
                self.choose_guardian(api_m)
                self.click_altar(api_m)
                self.deposit_runes(api_m)
            # Final sequence 
            self.gather_more_essence(api_m)
            self.power_up_guardian(api_m) 
            self.choose_guardian(api_m)
            self.click_altar(api_m)
            self.power_up_guardian(api_m)
            self.deposit_runes(api_m)
"""