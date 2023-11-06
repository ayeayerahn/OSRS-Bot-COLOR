import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
import utilities.api.item_ids as item_ids
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
# from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import RuneLiteObject
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSaerialfishing(AaronFunctions):
    def __init__(self):
        bot_title = "Aerial Fishing"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = True

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
        api_morg = MorgHTTPSocket()
        starting_exp = api_morg.get_skill_xp(skill="Fishing")
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.fish()
            api_morg.wait_til_gained_xp("Fishing", timeout=2)           
            if self.search_slot_28():
                knife_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "knife.png")
                fish = api_morg.get_inv_item_indices(item_id=item_ids.aerial_fish)
                knife = imsearch.search_img_in_rect(knife_img, self.win.control_panel)
                while fish:
                    fish = api_morg.get_inv_item_indices(item_id=item_ids.aerial_fish)
                    self.mouse.move_to(knife.random_point(), mouseSpeed = 'fastest')
                    self.mouse.click()
                    self.mouse.move_to(self.win.inventory_slots[27].random_point(), mouseSpeed = 'fastest')
                    self.mouse.click()

            self.update_progress((time.time() - start_time) / end_time)

        ending_exp = api_morg.get_skill_xp(skill="Fishing")
        total_exp_gained = ending_exp - starting_exp
        self.log_msg(f"Gained {total_exp_gained} experience in Fishing")
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def fish(self):
        counter = 0
        while counter != 1:
            if fishing_spot := self.get_all_tagged_in_rect(self.win.game_view, color=clr.CYAN):
                fishing_spot = sorted(fishing_spot, key=RuneLiteObject.distance_from_rect_center)
                pag.moveTo(fishing_spot[0].random_point())
                if not self.mouseover_text(contains="Catch", color=clr.OFF_WHITE):
                    continue
                else:
                    pag.click()
                    break
            time.sleep(1)
            counter += 1
            
    def is_fishing(self):
        if ocr.find_text("Fishing", self.win.game_view, ocr.PLAIN_12, clr.GREEN):
            return True
        else:
            self.log_msg("Could not find fishing text")