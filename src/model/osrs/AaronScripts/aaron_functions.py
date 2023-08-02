import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.imagesearch import search_img_in_rect
from utilities.geometry import Rectangle, Point
from pathlib import Path

class AaronFunctions(OSRSBot):
    def __init__(self, bot_title, description) -> None:
        super().__init__(bot_title, description)

    def activate_special(self):
        """Activates the special attack of the equipped weapon."""
        spec_energy = self.get_special_energy()
        if spec_energy >= 100:
            self.mouse.move_to(self.win.spec_orb.random_point())
            self.mouse.click()

    def click_color(self, color: clr):
        """This will click when the nearest tag is not none."""
        count = 0
        while True:
            if found := self.get_nearest_tag(color):
                if count < 10:
                    self.mouse.move_to(found.random_point())
                    if self.mouse.click(check_red_click=True):
                        break
                    else:
                        count += 1
                        time.sleep(1) 
                else:
                    count += 1
                    time.sleep(1)
                    if count == 10:
                        self.log_msg("We misclicked 10 times. Stopping script.")
                        self.stop()
            else:
                self.log_msg("failed to find object to click. Stopping script.")
                self.stop() 
        return

    def deposit_all(self): 
        deposit_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "deposit.png") 
        if deposit := self.wait_until_img(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit.random_point())   
            self.mouse.click() 
            return
            
    def sleep(self, num1, num2):
        sleep_time = rd.fancy_normal_sample(num1, num2)   
        #self.log_msg(f"Sleeping for {sleep_time} seconds")     #Uncomment this out if you wish to see how many seconds the sleep is doing
        time.sleep(sleep_time) 
    
    def wait_until_img(self, img: Path, screen: Rectangle, timeout: int = 10):
        """this will wait till img shows up in screen"""
        time_start = time.time()
        while True:
            if found := imsearch.search_img_in_rect(img, screen):
                break
            if time.time() - time_start > timeout:
                self.log_msg(f"We've been waiting for {timeout} seconds, something is wrong...stopping.")
                self.stop()
        return found    
    
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