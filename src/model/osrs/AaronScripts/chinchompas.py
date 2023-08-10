import time
import utilities.color as clr
import utilities.random_util as rd
import utilities.game_launcher as launcher
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from model.osrs.AaronScripts.aaron_functions import AaronFunctions

 
class OSRSHunter(AaronFunctions):
    
    def __init__(self):
        bot_title = "Red chin bot"
        description = "This bot hunts red chins."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False


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
        start_time = time.time()
        end_time = self.running_time * 60
        
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:  
            self.update_progress((time.time() - start_time) / end_time)
            self.bot_loop_main()
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        
               
    def bot_loop_main(self):
        self.hunt()
    
    def hunt(self):
        yellow_traps = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        
        if not yellow_traps:                   
            if caught_trap := self.get_all_tagged_in_rect(self.win.game_view, clr.PINK):
                last_exp = self.get_total_xp()
                counter = 0
                self.mouse.move_to(caught_trap[0].center(), mouseSpeed="fastest")
                self.log_msg("Caught the chin $$$")
                if self.mouseover_text(contains= "Reset", color=clr.OFF_WHITE):
                    self.mouse.click()
                    while counter < 100:
                        new_xp = self.get_total_xp()
                        if new_xp != last_exp:
                            break
                        counter += 1
                        time.sleep(0.1)
                    time.sleep(3.51)
        # if not yellow_traps:                   
        #     if caught_trap := self.get_all_tagged_in_rect(self.win.game_view, clr.PINK):
        #         self.mouse.move_to(caught_trap[0].center(), mouseSpeed="fastest")
        #         self.log_msg("Caught the chin $$$")
        #         if self.mouseover_text(contains= "Reset", color=clr.OFF_WHITE):
        #             self.mouse.click()
        #             time.sleep(8.4)
        
        if not self.get_nearest_tag(clr.PINK):
            if failed_trap := self.get_all_tagged_in_rect(self.win.game_view, clr.RED):
                timer = 0
                self.log_msg("Slippery chinchompa got away :(")
                self.mouse.move_to(failed_trap[0].center(), mouseSpeed='fastest')
                if self.mouseover_text(contains= "Reset", color=clr.OFF_WHITE):
                    self.mouse.click()
                    while timer < 100:
                        if self.chatbox_text_BLACK_first_line(contains="dismantle"):
                            break
                        timer += 1
                        time.sleep(0.1)
                    time.sleep(3.52)      
        
        if reset_trap := self.get_nearest_tag(clr.OFF_YELLOW):
            self.log_msg("Resetting trap, must of had a funny smell..")
            self.mouse.move_to(reset_trap.random_point(), mouseSpeed='fastest')
            if self.mouseover_text(contains= "Lay", color=clr.OFF_WHITE):
                self.mouse.click()
                time.sleep(5.5)