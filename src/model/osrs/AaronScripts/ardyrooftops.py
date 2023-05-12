import time


import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSardyrooftops(OSRSBot):
    def __init__(self):
        bot_title = "Ardy Rooftops"
        description = "This bot will run rooftop agility at Ardy."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 10

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
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
        #api_s = StatusSocket()

        pag.press('b')
        self.move_camera(0,80)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        #pag.press('b')
        #time.sleep(2)

        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.log_msg("Checking for marks")
            self.check_for_marks() # Check if marks of grace are visible on screen

            self.log_msg("Checking for agility icon")
            self.return_to_start() # Check if Agility icon is visible

            self.log_msg("Checking for green obstacles")
            self.green_obstacle(api_m) # If neither of the above are true, find and click green obstacle


            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)    

    def return_to_start(self):
        obstacle_tiles = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        agility_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "ardy_agility.png")
        if not obstacle_tiles:
            # If no obstacles can be seen, look for the agility icon
            if agility:= imsearch.search_img_in_rect(agility_img, self.win.minimap):
                time.sleep(1)
                self.mouse.move_to(agility.random_point())
                time.sleep(1)
                self.mouse.click()
                self.sleep(11,12)

    
    def green_obstacle(self, api_m: MorgHTTPSocket):
        obstacle_tiles = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN) # Since we moved the camera, check again
        try: 
            self.mouse.move_to(obstacle_tiles[0].random_point())
            self.mouse.click()
        except: self.log_msg("Can't find a green obstacle")
        #self.mouse.click()
        api_m.wait_til_gained_xp("Agility", 11)
        self.sleep(0,1)

    def check_for_marks(self):
        obstacle_tiles = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        marks_of_grace = self.get_all_tagged_in_rect(self.win.game_view, clr.BLUE)
        while marks_of_grace:
            self.log_msg("Found mark of grace.")
            time.sleep(1)
            if obstacle_tiles: # For the one time the bot sees a mark of grace on another platform before seeing the green tile in front of it
                break
            self.mouse.move_to(marks_of_grace[0].random_point())
            if self.mouse.click(check_red_click=True):
                self.log_msg("Successful click!")
                time.sleep(1)
                break        