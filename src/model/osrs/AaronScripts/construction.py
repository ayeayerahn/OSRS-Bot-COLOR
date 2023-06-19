import time
import utilities.color as clr
import pyautogui as pag
import utilities.ocr as ocr
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path


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
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

        # 1. Get planks from dude in the shop
            if not self.search_slot_28():
                self.get_planks()
                time.sleep(4)
                pag.press('3')
                time.sleep(0.5)
                self.enter_house()
        #2. Right click on portal and enter build mode
            else:
                self.enter_house()
        #3. Right click on larder and select build
            self.right_click_build_larder()
            time.sleep(3.5)
            pag.press('2')
            self.remove_larder()
            # time.sleep(1)
            for i in range(2):
                self.right_click_build_larder()
                time.sleep(1)
                pag.press('2')
        #5. Destroy larder
                self.remove_larder()
            time.sleep(0.5)
        #6. Left click to exit portal
            self.exit_portal()
            self.wait_until_color(color=clr.RED)

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
        if store_guy := self.get_nearest_tag(clr.CYAN):
            try:
                self.mouse.move_to(store_guy.random_point())
            except AttributeError:
                self.log_msg("Couldn't find the store guy. Trying again.")
        #if self.mouseover_text(contains="Phials", color=clr.OFF_YELLOW):
        self.mouse.click()

    #2. Right click on portal and enter build mode
    def enter_house(self):
        if portal := self.get_nearest_tag(clr.RED):
            try:
                self.mouse.move_to(portal.random_point(), mouseSpeed='fastest')
            except AttributeError:
                self.log_msg("Couldn't find the entry portal. Trying again.")
        self.mouse.click()

    #3. Right click on larder and select build
    def right_click_build_larder(self):
        self.wait_until_color(color=clr.GREEN)
        larder = self.get_nearest_tag(clr.GREEN)
        try:
            self.mouse.move_to(larder.random_point(), mouseSpeed='fastest')
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.right_click()
        if build_text := ocr.find_text("Build", self.win.game_view, ocr.BOLD_12, clr.WHITE):
            self.mouse.move_to(build_text[0].get_center(), knotsCount=0, mouseSpeed='fastest')
            self.mouse.click()

        #5. Destroy larder
    def remove_larder(self):
        self.wait_until_color(color=clr.YELLOW)         
        larder = self.get_nearest_tag(clr.YELLOW)
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
        portal = self.get_nearest_tag(clr.ORANGE)
        try:
            self.mouse.move_to(portal.random_point())
        except AttributeError:
            self.log_msg(AttributeError)
        self.mouse.click()

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
    
#This function specifically searches the 28th slot of the inventory. It returns False if the slot is empty and True if it contains any item.
    def search_slot_28(self):
        #define inventory_slots
        self.__locate_inv_slots(self.win.control_panel)
        # Create a rectangle for the 28th inventory slot
        slot_28 = self.inventory_slots[27]

        # Search for each item in the 28th inventory slot
        item_path = imsearch.BOT_IMAGES.joinpath("Aarons_images", "emptyslot.PNG")
        if search_img_in_rect(item_path, slot_28):
            self.log_msg(f"Slot 28: Empty")
            return False
        self.log_msg(f"Slot 28: Full")
        return True
    
#Make sure that this function is either imported from another file or defined in the same file before calling it.
    def __locate_inv_slots(self, cp: Rectangle) -> None:
        """
        Creates Rectangles for each inventory slot relative to the control panel, storing it in the class property.
        """
        self.inventory_slots = []
        slot_w, slot_h = 36, 32  # dimensions of a slot
        gap_x, gap_y = 6, 4  # pixel gap between slots
        y = 44 + cp.top  # start y relative to cp template
        for _ in range(7):
            x = 40 + cp.left  # start x relative to cp template
            for _ in range(4):
                self.inventory_slots.append(Rectangle(left=x, top=y, width=slot_w, height=slot_h))
                x += slot_w + gap_x
            y += slot_h + gap_y