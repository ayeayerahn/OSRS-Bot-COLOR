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
            #self.is_guardian_active()
            #guardian_fragments = api_m.get_inv_item_stack_amount(ids.GUARDIAN_FRAGMENTS)
            #if guardian_fragments > 43:
            self.mining_sequence(api_m)
            for i in range(10):
                self.normal_sequence(api_m)
                self.first_sequence(api_m)
            # if guardian_fragments < 43:
            #     self.log_msg("Not enough guardian fragments.. starting the special portal sequence")
            #     #self.mining_sequence(api_m)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def is_guardian_defeated(self):
        if self.chatbox_text_GREEN(contains="The Great Guardian successfully closed the rift") or self.chatbox_text_RED(contains="defeated"):
            self.log_msg("Game has ended.")
            time.sleep(5)
            return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
            if return_to_start:
                self.mouse.move_to(return_to_start.random_point())
                self.mouse.click()
                time.sleep(15)
            elif orange_portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(orange_portal.random_point())
                self.mouse.click()
                while not self.chatbox_text_BLACK(contains="You step through the portal and find yourself back in the temple"):
                    time.sleep(1)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.mouse.move_to(return_to_start.random_point())
                    self.mouse.click()
                    time.sleep(15)
            elif blue_portal := self.get_nearest_tag(clr.CYAN):
                self.mouse.move_to(blue_portal.random_point())
                self.mouse.click()
                while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
                    time.sleep(1)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.mouse.move_to(return_to_start.random_point())
                    self.mouse.click()
                    time.sleep(15)
            time.sleep(3)
            top_rubble = self.get_nearest_tag(clr.RED)
            self.mouse.move_to(top_rubble.random_point())
            self.mouse.click()
            time.sleep(10)
            self.is_guardian_active()
            return self.main_loop()


    def is_guardian_active(self):
        while not self.chatbox_text_RED(contains="The rift becomes active!"):
            self.log_msg("Waiting for new game to start..")
            if orange_portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(orange_portal.random_point())
                self.mouse.click()
            time.sleep(1)

    def gather_more_essence(self, api_m:MorgHTTPSocket):
        if self.chatbox_text_QUEST("You'll need at least one guardian fragment to craft guardian essence."):
            time.sleep(1)
            pag.press('space')
        self.is_guardian_defeated()
        workbench = self.get_nearest_tag(clr.DARK_PURPLE) # DARK_PURPLE = Color([106, 32, 110])
        self.log_msg("Converting fragments to essence..")
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        self.log_msg("Waiting until inventory is full..")
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            self.is_guardian_defeated()
            if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
                break
            time.sleep(1)
        pag.press('space')
        self.fill_pouches(api_m)
        workbench = self.get_nearest_tag(clr.DARK_PURPLE) # Call this again to recreate the rectangle from the original
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            self.is_guardian_defeated()
            if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
                break
            time.sleep(1)
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)
        self.mouse.move_to(workbench.random_point())
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            self.is_guardian_defeated()
            if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
                break
            time.sleep(1)
        pag.press('space')

    def deposit_runes(self):
        self.is_guardian_defeated()
        self.log_msg("Heading to deposit runes")
        deposit = self.get_nearest_tag(clr.DARK_BLUE)
        try:
            deposit = self.get_nearest_tag(clr.DARK_BLUE) # DARK_BLUE = Color([20, 95, 94])
            self.mouse.move_to(deposit.random_point())
            self.mouse.click()
        except:
            AttributeError
        counter = 0 
        while not self.chatbox_text_BLACK_first_line(contains=f"You deposit all of your runes into the pool"):
            if self.chatbox_text_BLACK_first_line(contains="You have no runs to deposit into the pool"):
                break
            self.is_guardian_defeated()
            counter += 1
            time.sleep(1)
            if counter == 15:
                return self.deposit_runes()
        time.sleep(0.5)

    def power_up_guardian(self, api_m:MorgHTTPSocket):
        self.is_guardian_defeated()
        power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
        while not power_up:
            power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
            self.is_guardian_defeated()
            time.sleep(1)
        try:
            #power_up = self.get_nearest_tag(clr.DARKER_YELLOW) # DARKER_YELLOW = Color([112, 110, 17])
            self.log_msg("Powering up the guardian..")
            self.mouse.move_to(power_up.random_point())
            self.mouse.click()
            api_m.wait_til_gained_xp("Runecraft", 10)
            pag.press('space') # In case the game ends before we get to deposit the last batch
            self.is_guardian_defeated()
        except:
            AttributeError

    def huge_guardian_remains(self, api_m:MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Running to huge guardian remains")
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            self.is_guardian_defeated()
            time.sleep(1)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.fill_pouches(api_m)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)

    def guardian_remains(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Mining guardian fragments")
        remains = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        api_m.wait_til_gained_xp('Mining', 10)
        self.is_guardian_defeated()

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
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        pag.keyUp('shift')
        if altar := self.get_nearest_tag(clr.GREEN):
            self.log_msg("Crafting third set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        time.sleep(1.5) # Gives enough time to let your character become idle
        if portal := self.get_nearest_tag(clr.ORANGE):
            self.log_msg("Heading back to main area..")
            self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
            self.mouse.click()
        # while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself back in the temple"):
        #     self.is_guardian_defeated()
        #     time.sleep(1)

    def special_portal(self, api_m: MorgHTTPSocket):
        counter = 0
        self.is_guardian_defeated()
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.activate_spec()
            self.is_guardian_defeated()
            time.sleep(1)
        self.mouse.move_to(portal.random_point())
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!'):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()
        while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
            counter += 1
            time.sleep(1)
            if counter == 15:
                return self.normal_sequence(api_m)
    
    def blue_portal_sequence(self, api_m:MorgHTTPSocket):
        # Loop to locate blue portal
        counter = 0
        self.is_guardian_defeated()
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        # Constantly check for blue portal to spawn
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.activate_spec()
            self.is_guardian_defeated()
            time.sleep(1)
        self.mouse.move_to(portal.random_point())
        # This sequence is for the blue portal that spawns on the east side
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!'):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()
        self.log_msg("Heading to huge guardian remains")
        # Counter sequence in to break us out of this if we get stuck
        while not self.chatbox_text_BLACK_first_line('You step through the portal and find yourself in another part of the temple'):
            self.is_guardian_defeated()
            counter += 1
            time.sleep(1)
            if counter == 15:
                return self.normal_sequence(api_m)
        # Mine huge guardian essence
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.fill_pouches(api_m)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)
        # Return to the main area via blue portal
        counter = 0
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Returning to main area...")
        self.mouse.move_to(portal.random_point())
        self.mouse.click()
        while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
            self.is_guardian_defeated()
            time.sleep(1)

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
        large_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "large_pouch.png")
        giant_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "giant_pouch.png")
        large_rune_pouch = imsearch.search_img_in_rect(large_rune_pouch_img, self.win.inventory_slots[2])
        giant_rune_pouch = imsearch.search_img_in_rect(giant_rune_pouch_img, self.win.inventory_slots[3])
        if not large_rune_pouch or not giant_rune_pouch:
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


    def choose_guardian(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Picking a guardian..")

        chaos_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_chaos.png")
        cosmic_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_cosmic.png")
        earth_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_earth.png")
        fire_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_fire.png")
        nature_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_nature.png")
        water_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_water.png")
        air_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_air.png")
        law_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_law.png")
        body_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_body.png")
        mind_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "gotr_mind.png")

        chaos_pillar = imsearch.search_img_in_rect(chaos_img, self.win.game_view)
        cosmic_pillar = imsearch.search_img_in_rect(cosmic_img, self.win.game_view)
        earth_pillar = imsearch.search_img_in_rect(earth_img, self.win.game_view)
        fire_pillar = imsearch.search_img_in_rect(fire_img, self.win.game_view)
        nature_pillar = imsearch.search_img_in_rect(nature_img, self.win.game_view)
        water_pillar = imsearch.search_img_in_rect(water_img, self.win.game_view)
        air_pillar = imsearch.search_img_in_rect(air_img, self.win.game_view)
        law_pillar = imsearch.search_img_in_rect(law_img, self.win.game_view)
        body_pillar = imsearch.search_img_in_rect(body_img, self.win.game_view)
        mind_pillar = imsearch.search_img_in_rect(mind_img, self.win.game_view)

        chosen_altar = None
        altar = None

        if law_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_PURPLE)
            chosen_altar = 'Law'    
        elif chaos_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_BROWN)
            chosen_altar = 'Chaos'
        elif nature_pillar:
            altar = self.get_nearest_tag(clr.DARK_GREEN)
            chosen_altar = 'Nature'
        elif cosmic_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_RED)
            chosen_altar = 'Cosmic'
        elif body_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_CYAN)
            chosen_altar = 'Body'
        elif mind_pillar:
            altar = self.get_nearest_tag(clr.DARK_ORANGE)
            chosen_altar = 'Mind'
        elif earth_pillar:
            altar = self.get_nearest_tag(clr.PURPLE)
            chosen_altar = 'Earth'
        elif water_pillar:
            altar = self.get_nearest_tag(clr.BLUE)
            chosen_altar = 'Water'
        elif air_pillar:
            altar = self.get_nearest_tag(clr.DARK_YELLOW) # DARK_YELLOW = Color([149, 146, 15])
            chosen_altar = 'Air'
        elif fire_pillar:
            altar = self.get_nearest_tag(clr.PINK)
            chosen_altar = 'Fire'
            
        try:
            if self.chatbox_text_BLACK_first_line(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                chosen_altar = None
                return self.choose_guardian(api_m)   
        except UnboundLocalError:
            self.log_msg("Idk why this happens lol")
            
        self.is_guardian_defeated()       
        self.log_msg(f"Going to {chosen_altar} altar")
        try:
            self.mouse.move_to(altar.random_point(), mouseSpeed = 'fastest')
            self.mouse.click()
        except AttributeError:
            self.log_msg(f"Could not locate {chosen_altar} pillar")
            return self.choose_guardian(api_m)
        self.is_guardian_defeated()
        while not self.chatbox_text_BLACK_first_line(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
            self.is_guardian_defeated()
            time.sleep(1)
            if self.chatbox_text_QUEST(contains="The Guardian is dormant. Its energy might return soon."):
                pag.press('space')
                self.log_msg("Altar was dormant. Trying again")
                #chosen_altar = None
                self.choose_guardian(api_m)
                break
        self.log_msg(f"Successfully entered the {chosen_altar} altar room!!")

    def first_sequence(self, api_m:MorgHTTPSocket):
        self.log_msg("Special portal sequence")
        self.guardian_remains(api_m)
        self.blue_portal_sequence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        self.deposit_runes()

    def mining_sequence(self, api_m:MorgHTTPSocket):
        self.log_msg("Mining sequence")
        self.guardian_remains(api_m)
        self.activate_spec()
        time.sleep(90)
        top_rubble = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(top_rubble.random_point())
        self.mouse.click()
        time.sleep(5)
        self.gather_more_essence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        self.deposit_runes() 

    def portal_sequence(self, api_m:MorgHTTPSocket):
        self.blue_portal_sequence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m) 

    def normal_sequence(self, api_m:MorgHTTPSocket):
        self.gather_more_essence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        portal = self.get_nearest_tag(clr.CYAN)
        if portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.portal_sequence(api_m)
        self.deposit_runes()   

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
"""