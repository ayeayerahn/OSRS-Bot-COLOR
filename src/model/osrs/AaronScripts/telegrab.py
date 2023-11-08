import time

import utilities.imagesearch as imsearch
import utilities.color as clr
import pyautogui as pag
from model.osrs.AaronScripts.aaron_functions import AaronFunctions
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSTelegrab(AaronFunctions):
    def __init__(self):
        bot_title = "MTA - Telegrab"
        description = "Character must face North."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 200
        
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

    def save_options(self):
        self.running_time = 200
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        api_morg = MorgHTTPSocket()
        self.found = False
        self.green_tile = False
        self.telegrab_counter = 0
        self.steps = 0
        self.black_tile = False
        self.yellow_tile = False

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.check_room()
            self.check_green_tile(api_morg)
            self.move_to_yellow_marker(api_morg)       
            self.telegrab_guardian(api_morg)
            self.check_completed()
            time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
    def check_room(self):
        if not self.found:
            if tile := self.get_nearest_tag(clr.BLUE):
                self.steps = 8
                self.log_msg("Blue room found.")
            elif tile := self.get_nearest_tag(clr.YELLOW):
                self.steps = 7
                self.log_msg("Yellow room found.")
            elif tile := self.get_nearest_tag(clr.PURPLE):
                self.steps = 10
                self.log_msg("Purple room found.")
            elif tile := self.get_nearest_tag(clr.ORANGE):
                self.steps = 7
                self.log_msg("Orange room found.")
            elif tile := self.get_nearest_tag(clr.PINK):
                self.steps = 8
                self.log_msg("Pink room found.")
            elif tile := self.get_nearest_tag(clr.LIGHT_CYAN):
                self.steps = 9
                self.log_msg("Light cyan room found.")
            elif tile := self.get_nearest_tag(clr.WHITE):
                self.steps = 10
                self.log_msg("White room found.")
            elif tile := self.get_nearest_tag(clr.DARK_BLUE):
                self.steps = 9
                self.log_msg("Dark blue room found.")
            elif tile := self.get_nearest_tag(clr.DARK_PURPLE):
                self.steps = 7
                self.log_msg("Dark purple room found.")
            elif tile := self.get_nearest_tag(clr.RED):
                self.steps = 8
                self.log_msg("Red room found.")
            self.found = True
            self.log_msg(f"Steps needed: {self.steps}")
            time.sleep(1)
        
    def move_to_yellow_marker(self, api: MorgHTTPSocket):
        yellow_marker_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "yellow_arrow_map_marker.png")
        if yellow_marker := imsearch.search_img_in_rect(yellow_marker_img, self.win.game_view):
            center_x = yellow_marker.get_center()[0]
            center_y = yellow_marker.get_center()[1]
            # self.log_msg("Found yellow marker")
            self.mouse.move_to((center_x, center_y+20))
            self.mouse.click()
            while not api.get_is_player_idle():
                # self.log_msg("Running to tile.")
                time.sleep(1)
        else:
            # self.log_msg("Did not find yellow marker.")
            return self.move_to_yellow_marker(api)
        time.sleep(1)
            
        
    def telegrab_guardian(self, api: MorgHTTPSocket):
        if guardian := self.get_nearest_tag(clr.CYAN):
            self.mouse.move_to(self.win.spellbook_normal[19].get_center())
            self.mouse.click()
            self.mouse.move_to(guardian.random_point())
            if self.mouse.click(check_red_click=True):
                self.telegrab_counter += 1     
                self.log_msg(f"Steps: {self.telegrab_counter}")  
            else:
                self.log_msg("Misclicked during telegrab_guardian function.")
                return self.telegrab_guardian(api)      
        else:
            self.log_msg("Could not find guardian. Trying again.")
            return self.telegrab_guardian(api)
        api.wait_til_gained_xp('Magic', 10)
        
    def check_completed(self):
        if self.telegrab_counter == self.steps:
            self.log_msg("Maze completed.")
            self.green_tile = False
            self.found = False
            self.telegrab_counter = 0
            self.steps = 0
            while not self.chatbox_text_QUEST(contains='Pizazz'):
                time.sleep(1)
            if guardian := self.get_nearest_tag(clr.CYAN):
                self.mouse.move_to(guardian.random_point())
                if not self.mouse.click(check_red_click=True):
                    self.log_msg("Misclicked during check_completed function.")
                    return self.check_completed()
                time.sleep(2)
                pag.press('space')
                time.sleep(2)
                pag.press('1')
                time.sleep(2)
                pag.press('space')
                
    def check_green_tile(self, api: MorgHTTPSocket):
        if not self.green_tile:
            if tile := self.get_nearest_tag(clr.GREEN):
                self.mouse.move_to(tile.random_point())
                self.mouse.click()
                while not api.get_is_player_idle():
                    time.sleep(1)
                self.green_tile = True
        pass