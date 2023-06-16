import time
import utilities.color as clr
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSConstruction(OSRSBot):
    def __init__(self):
        bot_title = "Construction"
        description = "<Script description here>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1000
        self.options_set = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

        # 1. Get planks from dude in the shop
            if not api_m.get_is_inv_full():
                self.get_planks()
                time.sleep(4)
                pag.press('3')

        #2. Right click on portal and enter build mode
            self.enter_house()
            
            #time.sleep(6)
        #3. Right click on larder and select build
            self.right_click_larder()
            self.build_larder()
            larder = self.get_nearest_tag(clr.YELLOW)
            if larder:
                self.remove_larder()
                time.sleep(4)
            time.sleep(2.5)
            pag.press('2')
            #time.sleep(1.5)
            self.remove_larder()
            time.sleep(1)
            for i in range(2):
                self.right_click_larder()
        #4. Build larder
                self.build_larder()
                #time.sleep(2)
        #5. Destroy larder
                self.remove_larder()
                #time.sleep(1)
        #6. Left click to exit portal
            self.exit_portal()
            time.sleep(3)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # 1. Get planks from dude in the shop
    def get_planks(self):
    # Left click the noted planks in inventory
        planks = self.win.inventory_slots[1]
        self.mouse.move_to(planks.random_point())
        self.mouse.click()
    # Left click on the dude in shop
        store_guy = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(store_guy.random_point())
        self.mouse.click()


    #2. Right click on portal and enter build mode
    def enter_house(self):
        portal = self.get_nearest_tag(clr.RED)
        try:
            self.mouse.move_to(portal.random_point(), mouseSpeed='fastest')
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.right_click()

        if build_mode_text := ocr.find_text("Build", self.win.game_view, ocr.BOLD_12, [clr.OFF_WHITE, clr.CYAN]):
            self.mouse.move_to(build_mode_text[0].get_center(), knotsCount=0)
            self.mouse.click()


    #loop twice
    #3. Right click on larder and select build
    def right_click_larder(self):
        larder = self.get_nearest_tag(clr.GREEN)
        while not larder:
            larder = self.get_nearest_tag(clr.GREEN)
            time.sleep(0.1)
        try:
            self.mouse.move_to(larder.random_point(), mouseSpeed='fastest')
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.right_click()

        #4. Build larder
    def build_larder(self):
            # Right click and Press 2
        if build_text := ocr.find_text("Build", self.win.game_view, ocr.BOLD_12, clr.WHITE):
            self.mouse.move_to(build_text[0].get_center(), knotsCount=0, mouseSpeed='fastest')
            self.mouse.click()
        time.sleep(1)
        pag.press('2')

        #5. Destroy larder
    def remove_larder(self):
        larder = self.get_nearest_tag(clr.YELLOW)
        while not larder:
            larder = self.get_nearest_tag(clr.YELLOW)
            time.sleep(0.2)            
        try:
            self.mouse.move_to(larder.random_point(), mouseSpeed='fastest')
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.right_click()

        if build_text := ocr.find_text("Remove", self.win.game_view, ocr.BOLD_12, clr.WHITE):
            self.mouse.move_to(build_text[0].get_center(), knotsCount=0, mouseSpeed='fastest')
            self.mouse.click()
        time.sleep(1)
        pag.press('1')

        #6. Left click to exit portal
    def exit_portal(self):
        portal = self.get_nearest_tag(clr.CYAN)
        try:
            self.mouse.move_to(portal.random_point())
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.click()