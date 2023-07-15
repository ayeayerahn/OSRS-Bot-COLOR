import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Point, Rectangle, RuneLiteObject
from utilities.window import Window


class OSRSGOTR_iron(OSRSBot):
    def __init__(self):
        bot_title = "GOTR"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1

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
            self.first_sequence(api_m)
            self.normal_sequence(api_m)  

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
# Full sequences

    def first_sequence(self, api_m:MorgHTTPSocket):
        self.log_msg("                                    First sequence")
        self.guardian_remains(api_m)
        # self.activate_spec()
        while True:
            if self.chatbox_text_RED(contains="portal"):
                break
            time.sleep(0.5)
        self.click_color(color=clr.RED)
        time.sleep(6)
        self.return_to_start()
        time.sleep(2)
        self.portal_sequence(api_m)

    def normal_sequence(self, api_m:MorgHTTPSocket):
        self.log_msg("                                    Gather sequence")
        self.get_essence_workbench(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m)
        self.deposit_runes(api_m)
        return self.normal_sequence(api_m)   

    def portal_sequence(self, api_m:MorgHTTPSocket):
        self.log_msg("                                Portal sequence")
        self.blue_portal_sequence(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.power_up_guardian(api_m) 
        self.deposit_runes(api_m)
        self.log_msg("                          Returning to normal sequence")
        return self.normal_sequence(api_m)

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
            api_m.wait_til_gained_xp("Runecraft", 7)
            pag.press('space') # In case the game ends before we get to deposit the last batch
            self.is_portal_active(api_m)
            self.is_guardian_defeated()
        except:
            AttributeError

    def deposit_runes(self, api_m:MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Heading to deposit runes")
        self.find_deposit()
        counter = 0 
        while not self.chatbox_text_BLACK_first_line(contains="You deposit all of your runes into the pool"):
            if self.chatbox_text_BLACK(contains="You have no runes to deposit into the pool"):
                self.log_msg("You had no runes to deposit")
                break
            self.log_msg("Looking for successful deposit message")
            self.is_guardian_defeated()
            counter += 1
            time.sleep(1)
            if counter == 8:
                self.log_msg("Counter reached 15, returning to get_essence_workbench function")
                return self.normal_sequence(api_m)
        time.sleep(0.5)
        self.is_portal_active(api_m)

    def huge_guardian_remains(self, api_m:MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Running to huge guardian remains")
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.click_color(color=clr.RED)
        while not self.chatbox_text_QUEST(contains="inventory"):
            self.is_guardian_defeated()
            time.sleep(1)
        self.fill_pouches(api_m)
        self.click_color(color=clr.RED)
        while not self.chatbox_text_QUEST(contains="inventory"):
            self.is_guardian_defeated()
            time.sleep(1)
        # self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        # self.mouse.click()
        time.sleep(1)
        # self.repair_pouches(api_m)
        # self.click_color(color=clr.RED)
        # while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
        #     self.is_guardian_defeated()
        #     time.sleep(1)

    def click_altar(self, api_m: MorgHTTPSocket):
        self.wait_until_color(color=clr.GREEN) # Wait until altar is visible          
        self.log_msg("Crafting first set of essence..")
        self.click_color(color=clr.GREEN) # Click altar
        api_m.wait_til_gained_xp("Runecraft", 10)
        self.empty_pouches()
        self.click_color(color=clr.GREEN) # Click altar
        api_m.wait_til_gained_xp("Runecraft", 3)
        pag.keyDown('shift')
        # self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        # self.mouse.click()
        pag.keyUp('shift')
        # if altar := self.get_nearest_tag(clr.GREEN):
        #     self.log_msg("Crafting third set of essence..")
        #     self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
        #     self.mouse.click()
        # api_m.wait_til_gained_xp("Runecraft", 3)
        time.sleep(2) # Gives enough time to let your character become idle
        self.log_msg("Heading back to main area..")
        self.click_color(color=clr.ORANGE)
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
        self.log_msg("                                 Blue portal sequence")
        # Loop to locate blue portal
        self.is_guardian_defeated()
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        # Constantly check for blue portal to spawn
        counter = 0
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            # self.activate_spec()
            self.is_guardian_defeated()
            counter += 1
            time.sleep(1)
            if counter == 30:
                return self.normal_sequence(api_m)
        self.mouse.move_to(portal.random_point())
        # This sequence is for the blue portal that spawns on the east side
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!'):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()
        self.log_msg("Heading to huge guardian remains")
        # Counter sequence to break us out of this if we get stuck
        self.check_chatbox_blue_portal(api_m)
        self.click_color(color=clr.RED) # Mine huge guardian essence
        self.huge_guardian_remains_is_inv_full() # Check if inventory is full
        self.fill_pouches(api_m)
        self.click_color(color=clr.RED) # Mine huge guardian essence
        self.huge_guardian_remains_is_inv_full() # Check if inventory is full
        # self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # small pouch
        # self.mouse.click()
        time.sleep(1)
        # self.repair_pouches(api_m)
        self.huge_guardian_remains_is_inv_full() # Check if inventory is full
        # Return to the main area via blue portal
        self.log_msg("Returning to main area...")
        self.click_color(color=clr.CYAN) # Return to the main area via blue portal
        time.sleep(1)
        self.check_chatbox_blue_portal(api_m)

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

        if cosmic_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_RED)
            chosen_altar = 'Cosmic'
        elif nature_pillar:
            altar = self.get_nearest_tag(clr.DARK_GREEN)
            chosen_altar = 'Nature'
        elif law_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_PURPLE)
            chosen_altar = 'Law' 
        elif chaos_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_BROWN)
            chosen_altar = 'Chaos'
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
        elif body_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_CYAN)
            chosen_altar = 'Body'
            
        self.is_guardian_defeated()       
        self.log_msg(f"Going to {chosen_altar} altar")
        count = 0
        while True:
            if count < 10:
                if altar:
                    self.mouse.move_to(altar.random_point())
                    while not self.mouse.click(check_red_click=True):
                        self.log_msg("Misclicked")
                        self.mouse.move_to(altar.random_point())
                    break
                else:
                    count += 1
                    time.sleep(1)
            else:
                self.log_msg("failed to find cape")
                self.stop() 
        self.is_guardian_defeated()
          
        counter = 0
        while True:
            if self.chatbox_text_BLACK_first_line(contains=f"You step through the rift and find yourself at the {chosen_altar} Altar"):
                self.log_msg(f"Successfully entered the {chosen_altar} altar room!!")
                counter = 0
                break
            if self.chatbox_text_QUEST(contains="The Guardian is dormant. Its energy might return soon."):
                pag.press('space')
                self.log_msg("Altar was dormant. Trying again")
                counter = 0
                return self.choose_guardian(api_m)
            counter += 1
            time.sleep(1)
            if counter == 10:
                self.log_msg("We might have misclicked")
                pag.press('space')
                counter = 0
                return self.choose_guardian(api_m)
        
        # self.log_msg(f"Successfully entered the {chosen_altar} altar room!!")
 
# Mini-sequences
    def get_essence_workbench(self, api_m:MorgHTTPSocket):
        self.check_chatbox_guardian_fragment()
        self.is_guardian_defeated()
        self.log_msg("Waiting until inventory is full..")
        self.work_at_bench()
        api_m.wait_til_gained_xp("Crafting", 5)
        self.workbench_is_inv_full(api_m)
        pag.press('space')
        self.fill_pouches(api_m)
        self.log_msg("Waiting until inventory is full #2..")
        self.work_at_bench()
        self.workbench_is_inv_full(api_m)
        pag.press('space')
        # self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest') # fill giant pouch
        # self.mouse.click()
        time.sleep(1)
        # self.repair_pouches(api_m)
        # self.log_msg("Waiting until inventory is full #3..")
        # self.work_at_bench()
        # while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
        #     self.is_guardian_defeated()
        #     if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
        #         break
        #     time.sleep(1)
        # pag.press('space')

# Check functions
    def is_portal_active(self, api_m:MorgHTTPSocket):
        portal = self.get_nearest_tag(clr.CYAN)
        if portal:
            portal = self.get_nearest_tag(clr.CYAN)
            return self.portal_sequence(api_m)

    def workbench_is_inv_full(self, api_m:MorgHTTPSocket):
        while True:
            self.is_portal_active(api_m)
            self.is_guardian_defeated()
            if self.chatbox_text_QUEST(contains="inventory"):
                self.log_msg("Inventory full.")
                break
            if self.chatbox_text_BLACK_first_line(contains="fragments"):
                self.log_msg("Ran out of guardian fragments.")
                self.guardian_remains(api_m)
                return self.blue_portal_sequence(api_m)
            time.sleep(0.5)
                

    def huge_guardian_remains_is_inv_full(self):
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated()
            time.sleep(1)

    def is_guardian_active(self):
        while not self.chatbox_text_RED(contains="The rift becomes active!"):
            self.log_msg("Waiting for new game to start..")
            if orange_portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(orange_portal.random_point())
                self.mouse.click()
            time.sleep(1)

    def is_guardian_defeated(self):
        if self.chatbox_text_GREEN(contains="The Great Guardian successfully closed the rift") or self.chatbox_text_RED(contains="defeated"):
            self.log_msg("Game has ended.")
            time.sleep(10)
            orange_portal = self.get_nearest_tag(clr.ORANGE)
            blue_portal = self.get_nearest_tag(clr.CYAN)
            if return_to_start := self.get_nearest_tag(clr.DARKER_GREEN):
                self.return_to_start()
                time.sleep(10) 
                orange_portal = self.get_nearest_tag(clr.ORANGE)
                blue_portal = self.get_nearest_tag(clr.CYAN)
            elif orange_portal:
                self.orange_portal()
                time.sleep(5)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.return_to_start()
            elif blue_portal:
                self.blue_portal()
                time.sleep(5)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.return_to_start()
                    time.sleep(15)
            time.sleep(3)
            self.click_color(color=clr.RED)
            time.sleep(10)
            self.is_guardian_active()
            return self.main_loop()

    def check_chatbox_guardian_fragment(self):
        while self.chatbox_text_QUEST("You'll need at least one guardian fragment to craft guardian essence."):
            time.sleep(1)
            pag.press('space')

    def check_chatbox_blue_portal(self, api_m:MorgHTTPSocket):
        counter = 0
        self.log_msg("Checking chat for 'another part of the temple' after clicking blue portal")
        while not self.chatbox_text_BLACK_first_line('You step through the portal and find yourself in another part of the temple'):
            self.is_guardian_defeated()
            counter += 1
            time.sleep(1)
            if counter == 15:
                self.log_msg("Returning to normal sequence")
                return self.normal_sequence(api_m)

# Smaller functions
    def activate_spec(self):
        spec_energy = self.get_special_energy()
        if spec_energy >= 100:
            self.mouse.move_to(self.win.spec_orb.random_point())
            self.mouse.click()  

    def fill_pouches(self, api_m: MorgHTTPSocket):
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        # self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # medium pouch
        # self.mouse.click()
        # self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest') # large pouch
        # self.mouse.click()
        #time.sleep(1)
        #self.repair_pouches(api_m)

    def empty_pouches(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest') # small pouch
        self.mouse.click()
        # self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest') # medium pouch
        # self.mouse.click()
        # self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest') # large pouch
        # self.mouse.click()
        pag.keyUp('shift')

    def repair_pouches(self, api_m: MorgHTTPSocket):
        giant_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "giant_pouch.png")
        giant_rune_pouch = imsearch.search_img_in_rect(giant_rune_pouch_img, self.win.inventory_slots[4])
        if not giant_rune_pouch:
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

    def find_deposit(self):
        if deposit := self.get_nearest_tag(clr.DARK_BLUE): # DARK_BLUE = Color([20, 95, 94])
            self.mouse.move_to(deposit.random_point())
            self.mouse.click()

    def work_at_bench(self):
        self.log_msg("Converting fragments to essence..") # DARK_PURPLE = Color([106, 32, 110])
        self.click_color(color=clr.DARK_PURPLE)

    def guardian_remains(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated()
        self.log_msg("Mining guardian fragments")
        self.click_color(color=clr.YELLOW)
        api_m.wait_til_gained_xp('Mining', 10)
        self.is_guardian_defeated()

    def return_to_start(self):
        if return_to_start := self.get_nearest_tag(clr.DARKER_GREEN):
            self.mouse.move_to(return_to_start.random_point())
            self.mouse.click() 

    def orange_portal(self):
        if orange_portal := self.get_nearest_tag(clr.ORANGE):
            self.mouse.move_to(orange_portal.random_point())
            self.mouse.click()
            while not self.chatbox_text_BLACK(contains="You step through the portal and find yourself back in the temple"):
                time.sleep(1)

    def blue_portal(self):
        if blue_portal := self.get_nearest_tag(clr.CYAN):
            self.mouse.move_to(blue_portal.random_point())
            self.mouse.click()
            while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
                time.sleep(1)

    def click_color(self, color: clr):
        count = 0
        while True:
            # if count < 10:
            if found := self.get_nearest_tag(color):
                self.mouse.move_to(found.random_point())
                while not self.mouse.click(check_red_click=True):
                    self.log_msg("Misclicked")
                    if count < 10:
                        if found := self.get_nearest_tag(color):
                            self.mouse.move_to(found.random_point())
                        else:
                            count += 1
                            time.sleep(1)
                break
                # else:
                #     count += 1
                #     time.sleep(1)
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