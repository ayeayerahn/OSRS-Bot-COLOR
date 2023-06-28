import time
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot


class OSRScanifisrooftops(OSRSBot):
    def __init__(self):
        bot_title = "Canifis Rooftops"
        description = "This bot will run rooftop agility at Canifis."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1000
        self.options_set = True

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
        #self.set_compass_west()
        #self.move_camera(0,80)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.log_msg("Checking for marks")
            self.check_for_marks() # Check if marks of grace are visible on screen

            #self.log_msg("Checking for agility icon")
            #self.return_to_start() # Check if Agility icon is visible

            self.log_msg("Checking for green obstacles")
            self.green_obstacle() # If neither of the above are true, find and click green obstacle


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
        achievement_icon_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "Achievement_Diaries_icon.png")
        if not obstacle_tiles:
            # If no obstacles can be seen, look for the agility icon
            if achievement_icon:= imsearch.search_img_in_rect(achievement_icon_img, self.win.minimap):
                time.sleep(1)
                self.mouse.move_to(achievement_icon.random_point())
                time.sleep(1)
                self.mouse.click()
                self.sleep(16,17)

    
    def green_obstacle(self):
        last_xp = self.get_total_xp()
        counter = 0 
        obstacle_tiles = self.get_nearest_tag(clr.GREEN) # Since we moved the camera, check again
        try: 
            self.mouse.move_to(obstacle_tiles.random_point(), mouseSpeed = 'fastest')
            if self.mouseover_text(color=[clr.OFF_WHITE, clr.CYAN]):
                if not self.mouse.click(check_red_click=True):
                    return self.green_obstacle()
        except: self.log_msg("Can't find a green obstacle")
        while counter < 17:
            new_xp = self.get_total_xp()
            if new_xp != last_xp:
                break
            counter += 1
            self.log_msg(f"Seconds elapsed: {counter}")
            time.sleep(1)
        time.sleep(0.5)
        counter = 0

    def check_for_marks(self):
        marks_of_grace = self.get_nearest_tag(clr.BLUE)
        while marks_of_grace:
            obstacle_tiles = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
            self.log_msg("Found mark of grace.")
            time.sleep(1)
            if obstacle_tiles: # For the one time the bot sees a mark of grace on another platform before seeing the green tile in front of it
                break
            self.mouse.move_to(marks_of_grace.random_point())
            if self.mouseover_text(contains="Mark of grace", color=clr.OFF_ORANGE):
                if self.mouse.click(check_red_click=True):
                    self.log_msg("Successful click!")
                    self.wait_until_color(color=clr.GREEN, timeout=10)
                    break      
            return self.check_for_marks()

    def wait_until_color(self, color: clr, timeout: int = 10):
        """this will wait till nearest tag is not none"""
        time_start = time.time()
        while True:
            if time.time() - time_start > timeout:
                self.log_msg(f"We've been waiting for {timeout} seconds, something is wrong...stopping.")
                self.stop()
            if found := self.get_nearest_tag(color):
                break
            time.sleep(1)
        return