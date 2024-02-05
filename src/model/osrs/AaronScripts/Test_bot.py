import time
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from typing import List, Union
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, Rectangle, RuneLiteObject
# import utilities.ScreenToClient  as stc #comment out if not using remote input
# import utilities.RIOmouse as Mouse #comment out if not using rmeote input
# import utilities.BackGroundScreenCap as bcp #comment out if not using remote input
import utilities.imagesearch as imsearch
from PIL import Image
import cv2
import os
import threading
import utilities.ocr as ocr
import pyautogui as pag





class OSRSTest_Bot(OSRSBot):
    def __init__(self):
        bot_title = "Test Bot"
        description = "This is a test Bot to check functions inside of your osbc/runelite enviorment"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 300
        self.Client_Info = None
        self.win_name = None
        self.pid_number = None
        self.Input = "failed to set mouse input"
        self.is_idle = False   
    
        

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_process_selector("Client_Info")
        self.options_builder.add_checkbox_option("Input","Choose Input Method",["Remote","PAG"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "Client_Info":
                self.Client_Info = options[option]
                client_info = str(self.Client_Info)
                win_name, pid_number = client_info.split(" : ")
                self.win_name = win_name
                self.pid_number = int(pid_number)
                self.win.window_title = self.win_name
                # self.win.window_pid = self.pid_number
                # stc.window_title = self.win_name
                # Mouse.Mouse.clientpidSet = self.pid_number
                # bcp.window_title = self.win_name
                # bcp
            # elif option == "Input":
            #     self.Input = options[option]
            #     if self.Input == ['Remote']:
            #         Mouse.Mouse.RemoteInputEnabledSet = True
            #     elif self.Input == ['PAG']:
            #         Mouse.Mouse.RemoteInputEnabledSet = False
            #     else:
            #         self.log_msg(f"Failed to set mouse")  
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.log_msg(f"{self.win_name}")
        self.log_msg(f"{self.pid_number}")
        self.log_msg(f"{self.Input}")
        self.options_set = True
        
    
            
    def main_loop(self):

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # uncomment functions you want to run
           #self.ocr_extract_text_check(self.win.mouseover,ocr.BOLD_12,clr.OFF_WHITE)
           #self.mouse_over_text_check("Walk",clr.OFF_WHITE)
           #self.show_window(self.win.game_view)
           #self.save_window(self.win.game_view,"game_view")
           #self.contour_check(self.win.game_view,clr.BLACK)
        #    self._pick_up_loot(self.lootables())
            # yellow_marker_img = imsearch.BOT_IMAGES.joinpath("Aarons_images", "yellow_arrow_map_marker.png")
            # if yellow_marker := imsearch.search_img_in_rect(yellow_marker_img, self.win.game_view):
            #     print(yellow_marker)
            #     self.log_msg("Found yellow marker")
            # else:
            #     self.log_msg("Did not find yellow marker.")
            # time.sleep(0.1)
            altar = self.get_nearest_tag(clr.GREEN)
            self.mouse.move_to(self.win.inventory_slots[0].random_point())
            self.mouse.click()
            time.sleep(0.2)
            self.mouse.move_to(altar.random_point())
            self.mouse.click()
            time.sleep(0.2)
           
    def ocr_extract_text_check(self,window,font,color):
        #prints ocr to log box
         text = ocr.extract_text(window, font, color)
         self.log_msg(f"{text}")
        
    def mouse_over_text_check(self,text,color):
        #prints detected mouse over text to log box
        if self.mouseover_text(contains=text, color=color):
            self.log_msg(f"{text} found")
        else: 
            self.log_msg(f"{text} not found")
            
    def show_window(self,window):
        #opens a pop up of the given window
        cv2.imshow("x",window.screenshot())
        self.log_msg(f"press key to continue")
        cv2.waitKey(0)
        
    def save_window(self,window,filename):
        #saves a png of the selected window
        cv2.imwrite(f"{filename}.png",window.screenshot())
        self.log_msg(f"press key to continue")
        cv2.waitKey(0)
        
    def contour_check(self,window,color):
        if self.get_all_tagged_in_rect(window,color):
            self.log_msg(f" contour was found")
        else:
            self.log_msg(f"contour was NOT found")
                     
    def _pick_up_loot(self, items: Union[str, List[str]], supress_warning=True) -> bool:
        """
        Attempts to pick up a single purple loot item off the ground. It is your responsibility to ensure you have
        enough inventory space to pick up the item. The item closest to the game view center is picked up first.
        Args:
            item: The name(s) of the item(s) to pick up (E.g. -> "Coins", or "coins, bones", or ["Coins", "Dragon bones"]).
        Returns:
            True if the item was clicked, False otherwise.
        """
        # Capitalize each item name
        if isinstance(items, list):
            for i, item in enumerate(items):
                item = item.capitalize()
                items[i] = item
        else:
            items = self.capitalize_loot_list(items, to_list=True)
        # Locate Ground Items text
        try:
            if item_text := ocr.find_text(items, self.win.game_view, ocr.PLAIN_12, clr.PURPLE):
                for item in item_text:
                    item.set_rectangle_reference(self.win.game_view)
                sorted_by_closest = sorted(item_text, key=Rectangle.distance_from_center)
                pag.moveTo(sorted_by_closest[0].get_center())
                for _ in range(5):
                    if self.mouseover_text(contains=["Take"] + items, color=[clr.OFF_WHITE, clr.OFF_ORANGE]):
                        pag.keyDown('shift')
                        pag.click()
                        pag.keyUp('shift')
                        break
                    # self.mouse.move_rel(0, 3, 1, mouseSpeed="fastest")
                # search the right-click menu
                # if take_text := ocr.find_text(
                #     items,
                #     self.win.game_view,
                #     ocr.BOLD_12,
                #     [clr.WHITE, clr.PURPLE, clr.ORANGE],
                # ):
                #     self.mouse.move_to(take_text[0].random_point(), mouseSpeed="medium")
                #     self.mouse.click()
                #     return True
                # else:
                #     self.log_msg(f"Could not find 'Take {item_text[0]}' in right-click menu.")
                #     return False
            elif not supress_warning:
                self.log_msg(f"Could not find {item_text[0]} on the ground.")
                return False
        except IndexError:
            self.log_msg("Could not find item on the ground.")

    def capitalize_loot_list(self, loot: str, to_list: bool):
        """
        Takes a comma-separated string of loot items and capitalizes each item.
        Args:
            loot_list: A comma-separated string of loot items.
            to_list: Whether to return a list of capitalized loot items (or keep it as a string).
        Returns:
            A list of capitalized loot items.
        """
        if not loot:
            return ""
        phrases = loot.split(",")
        capitalized_phrases = []
        for phrase in phrases:
            stripped_phrase = phrase.strip()
            capitalized_phrase = stripped_phrase.capitalize()
            capitalized_phrases.append(capitalized_phrase)
        return capitalized_phrases if to_list else ", ".join(capitalized_phrases)
    
    def lootables(self) -> list:
        ITEMS = [
            "Rune med helm",
            "Mystic robe top (dark)",
            "Brimstone key",
            "Rune bar",
            "Rune Battleaxe",
            "Runite bar",
            "Rune 2h sword",
            "Rune sq shield",
            "Rune kiteshield",
            "Dragon med helm",
            "Shield left half",
            "Dragon spear",
            "Ancient shard",
            "Dark totem base",
            "Dark totem middle",
            "Dark totem top",
            "Torstol seed",
            "Snape grass seed",
            "snapdragon seed",
            "Rune chainbody",
            "Abyssal whip",
            "Abyssal dagger",
            "Grimy ranarr weed",
            "Loop half of key",
            "Tooth half of key",
            "Rune 2h sword",
            "Dragonstone",
            "Rune spear",
            "Abyssal head",
            "Ranarr seed",
            "Rune longsword",
            "Dragon javelin heads",
            "Dragon platelegs",
            "Dragon plateskirt",
            "Uncut dragonstone",
            "Rune hasta",
            "Rune platelegs",
            "Rune full helm",
            "Rune platebody",
            "Dragon longsword",
            "Dragon dagger",
            "Rune javelin",
            "Soul rune",
            "Death rune",
            "Law rune",
            "Rune arrow",
            "Dragon dart tip",
            "Runite ore",
            "Dragon arrowtips",
            "Dark bow",
            "Adamantite bar",
            "Adamantite ore",
            "Rune dagger",
            "Air battlestaff",
            "Earth battlestaff",
            "Mystic air staff",
            "Mystic earth staff",
            "Dragon chainbody",
            "Occult necklace",
            "Smoke rune",
            "Runite bolts",
            "Battlestaff"
            ]
        return ITEMS
  