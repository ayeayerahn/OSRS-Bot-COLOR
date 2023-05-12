import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import utilities.debug as debug
import pyautogui as pag
import cv2
from model.osrs.osrs_bot import OSRSBot
from typing import NamedTuple
from utilities.geometry import Rectangle
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSbirdhouses(OSRSBot):
    def __init__(self):
        bot_title = "Birdhouse Run"
        description = "This bot will do birdhouse runs."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 10

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

        # 1. Teleport to crafting guild
            pag.press('a')
            self.set_compass_south()
            self.crafting_cape_teleport()
            time.sleep(4)
        # 2 Locate bank
        # 3. Open bank and deposit all
            self.open_bank()
            time.sleep(3)
            self.deposit_all()
            time.sleep(1)
        # 4. Withdraw supplies
            self.withdraw_supplies()
        # 5. Click on inventory tab and locate digsite pendant in inventory, right click and teleport to digsite
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            time.sleep(1)
            self.mouse.move_to(self.win.inventory_slots[7].random_point()) 
            self.mouse.click()
            time.sleep(1)
            pag.press('2')
            time.sleep(3)
        # 6. Locate the mushroom to teleport to the first spot
            self.set_compass_north()
            time.sleep(1)
            mushroom = self.get_nearest_tag(clr.GREEN)
            if not self.mouseover_text(contains="Use"):
                self.mouse.move_to(mushroom.random_point()) 
            self.mouse.click()
            time.sleep(7)
            pag.press('2')
            time.sleep(5)
        # 7. Conduct first birdhouse and second birdhouse
            self.birdhouse(api_m)
            time.sleep(1)
            self.second_birdhouse(api_m)
            time.sleep(1)
        # 8. Return to mushroom
            self.set_compass_west()
            mushroom = self.get_nearest_tag(clr.GREEN)
            if not self.mouseover_text(contains="Use"):
                self.mouse.move_to(mushroom.random_point()) 
            self.mouse.click()
            time.sleep(8)
            pag.press('4')
            time.sleep(5)
        #9. Third birdhouse
            self.set_compass_north()
            self.move_camera(0, 50)
            time.sleep(3)
            self.birdhouse(api_m)
            time.sleep(1)
        #10. Path to final birdhouse
            self.pathing_to_last_birdhouse()
        #11. Fourth birdhouse
            self.birdhouse(api_m)
        #12. Return to crafting guild
            self.crafting_cape_teleport()
            self.stop()




            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def new_rectangle(self):
        Point = NamedTuple("Point", x=int, y=int)
        top_left = Point(640, 458)
        bottom_right = Point(662, 469)
        equipment_rect = Rectangle.from_points(top_left, bottom_right)
        #sct = equipment_rect.screenshot()
        #debug.save_image('minimap screenshot', sct)
        return equipment_rect
    
    def open_bank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Bank"):
            self.mouse.move_to(banker.random_point()) 
        self.mouse.click()
        self.sleep(1,2)

    def crafting_cape_teleport(self):
        self.mouse.move_to(self.win.cp_tabs[4].random_point())
        self.mouse.click()
        crafting_cape = imsearch.BOT_IMAGES.joinpath("scraper", "crafting_cape.png") 
        if cape := imsearch.search_img_in_rect(crafting_cape, self.win.control_panel):
            self.mouse.move_to(cape.random_point())
            self.mouse.click()

    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time)   

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("scraper", "deposit.png") 
        if deposit := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click()   
    
    def withdraw_x(self):
        if withdraw_text := ocr.find_text('Withdraw-X', self.win.game_view, ocr.BOLD_12, clr.WHITE):
            item = withdraw_text[0]
            self.mouse.move_to(item.random_point(), knotsCount=0, mouseSpeed='fastest')
            self.mouse.click()    
    
    def withdraw_logs(self):
        yew_logs_bank = imsearch.BOT_IMAGES.joinpath("scraper", "yew_logs_bank.png")
        if yew_logs := imsearch.search_img_in_rect(yew_logs_bank, self.win.game_view):
            self.mouse.move_to(yew_logs.random_point(), mouseSpeed = 'fastest')
            self.mouse.right_click()
            self.withdraw_x()
            time.sleep(1.5)
            pag.press('4')
            time.sleep(0.5)
            pag.press('enter')
    
    def withdraw_hammer(self):
        hammer_bank = imsearch.BOT_IMAGES.joinpath("scraper", "hammer_bank.png")
        if hammer := imsearch.search_img_in_rect(hammer_bank, self.win.game_view):
            self.mouse.move_to(hammer.random_point(), mouseSpeed = 'fastest')
            self.mouse.click()
            time.sleep(0.5)

    def withdraw_chisel(self):
        chisel_bank = imsearch.BOT_IMAGES.joinpath("scraper", "chisel_bank.png")
        if chisel := imsearch.search_img_in_rect(chisel_bank, self.win.game_view):
            self.mouse.move_to(chisel.random_point(), mouseSpeed = 'fastest')
            self.mouse.click()
            time.sleep(0.5)

    def withdraw_seeds(self):
        seeds_bank = imsearch.BOT_IMAGES.joinpath("scraper", "Onion_seed_bank.png")
        if seeds := imsearch.search_img_in_rect(seeds_bank, self.win.game_view):
            self.mouse.move_to(seeds.random_point(), mouseSpeed = 'fastest')
            self.mouse.right_click()
            self.withdraw_x()
            time.sleep(1.5)
            pag.press('4')
            pag.press('0')
            time.sleep(0.5)
            pag.press('enter') 

    def withdraw_birdhouse(self):
        yew_birdhouse_bank = imsearch.BOT_IMAGES.joinpath("scraper", "yew_bird_house_bank.png")
        if birdhouse := imsearch.search_img_in_rect(yew_birdhouse_bank, self.win.game_view):
            self.mouse.move_to(birdhouse.random_point(), mouseSpeed='fastest')
            self.mouse.click() 
            time.sleep(0.5)
    
    def withdraw_necklace(self):
        digsite_neck_bank = imsearch.BOT_IMAGES.joinpath("scraper", "digsite_pendant_bank.png")
        if digsite_neck := imsearch.search_img_in_rect(digsite_neck_bank, self.win.game_view):
            self.mouse.move_to(digsite_neck.random_point(), mouseSpeed='fastest')
            self.mouse.click() 
            time.sleep(0.5)        

    def withdraw_supplies(self):
        self.withdraw_logs()
        self.withdraw_chisel()
        self.withdraw_hammer()
        self.withdraw_birdhouse()
        self.withdraw_necklace()
        self.withdraw_seeds()
        time.sleep(0.5)
        pag.press('escape')

    def birdhouse(self, api_m: MorgHTTPSocket):
        # Loot first birdhouse
        loot_spot = self.get_nearest_tag(clr.RED)
        if not self.mouseover_text(contains="Empty"):
            self.mouse.move_to(loot_spot.random_point()) 
        self.mouse.click()
        api_m.wait_til_gained_xp("Hunter", 10)
        time.sleep(1)
        # Replace birdhouse with already made birdhouse from inventory that we started with
        build_spot = self.get_nearest_tag(clr.RED)
        if not self.mouseover_text(contains="Build"):
            self.mouse.move_to(build_spot.random_point()) 
        self.mouse.click()
        time.sleep(1)
        # Add news seeds to empty birdhouse
        self.mouse.move_to(self.win.inventory_slots[8].random_point()) 
        self.mouse.click()
        refill_seeds = self.get_nearest_tag(clr.RED)
        if not self.mouseover_text(contains="Seeds"):
            self.mouse.move_to(refill_seeds.random_point()) 
        self.mouse.click()
        time.sleep(1)
        self.birdhouse_assembly(api_m)

    def second_birdhouse(self, api_m: MorgHTTPSocket):
        # Loot second birdhouse
        loot_spot = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Empty"):
            self.mouse.move_to(loot_spot.random_point()) 
        self.mouse.click()
        api_m.wait_til_gained_xp("Hunter", 10)
        time.sleep(1)
        # Replace birdhouse with already made birdhouse from inventory that we started with
        build_spot = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Build"):
            self.mouse.move_to(build_spot.random_point()) 
        self.mouse.click()
        time.sleep(1)
        # Add news seeds to empty birdhouse
        self.mouse.move_to(self.win.inventory_slots[8].random_point()) 
        self.mouse.click()
        refill_seeds = self.get_nearest_tag(clr.CYAN)
        if not self.mouseover_text(contains="Seeds"):
            self.mouse.move_to(refill_seeds.random_point()) 
        self.mouse.click()
        time.sleep(1)
        self.birdhouse_assembly(api_m)

    def pathing_to_last_birdhouse(self):
        top_minimap = self.new_rectangle()
        self.set_compass_south()
        time.sleep(2)
        for i in range(4):
            self.mouse.move_to(top_minimap.random_point())
            self.mouse.click()
            time.sleep(5)
        self.set_compass_north() 
        time.sleep(2)

    def birdhouse_assembly(self, api_m:MorgHTTPSocket):
        self.mouse.move_to(self.win.inventory_slots[5].random_point())
        self.mouse.click()
        logs = api_m.get_inv_item_indices(ids.YEW_LOGS)
        self.mouse.move_to(self.win.inventory_slots[logs[0]].random_point())
        self.mouse.click()
        time.sleep(0.5)

'''

'''