import time
import utilities.color as clr
import utilities.api.item_ids as ids
from utilities.api.morg_http_client import MorgHTTPSocket
from model.osrs.AaronScripts.aaron_functions import AaronFunctions


class OSRSchop_and_firemake(AaronFunctions):
    def __init__(self):
        bot_title = "Chop and Firemake"
        description = "This bot will light logs."
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

        # Setup APIs
        api_m = MorgHTTPSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            self.woodcut_normal_trees()
            self.firemake()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def woodcut_normal_trees(self):
        # self.activate_special()
        if not self.search_slot_28():
            if tree := self.get_nearest_tag(clr.GREEN):
                self.mouse.move_to(tree.random_point())
                self.mouse.click()
                self.log_msg("Wooducutting until we have a full inventory.")
                time.sleep(2)
        # while not api_m.get_is_player_idle(): # In case we don't want to use the API
        #     time.sleep(0.5)
            self.run_to_tree()
            self.check_woodcutting_status()
        if self.search_slot_28():
            self.log_msg("Inventory is full. Time to firemake.")
            # self.drop_all(skip_rows=0, skip_slots=[0, 1])
            return self.firemaking_spot()
        else:
            return self.woodcut_normal_trees()       
        
    def run_to_tree(self):
        self.log_msg("Running to next tree..")
        counter = 0
        while counter < 10:
            if self.chatbox_text_BLACK_first_line(contains="swing"):
                self.log_msg("Swing text found..")
                break
            else:
                time.sleep(1)
                counter += 1
        # return self.woodcut()
    
    def check_woodcutting_status(self):
        counter = 0
        while counter < 60:
            if self.chatbox_text_RED_first_line(contains="idle"):
                self.log_msg("Idle.")
                break
            else:
                time.sleep(1)
                counter += 1
        # return self.main_loop()

    def firemake(self):
        for i in range(27):
            self.mouse.move_to(self.win.inventory_slots[0].random_point())
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[i+1].random_point())
            self.mouse.click()
            self.wait_for_fire()

        # oak_logs = api_m.get_inv_item_indices(ids.logs)
        # for i in oak_logs:
        #     oak_logs = api_m.get_inv_item_indices(ids.logs)
        #     self.mouse.move_to(self.win.inventory_slots[0].random_point())
        #     self.mouse.click()
        #     self.mouse.move_to(self.win.inventory_slots[oak_logs[0]].random_point())
        #     self.mouse.click()
        #     api_m.wait_til_gained_xp("Firemaking", 15)

        time.sleep(1)
        self.log_msg("Out of logs. Time to cut again.")

    def wait_for_fire(self):
        last_xp = self.get_total_xp()
        counter = 0
        while counter < 50:
            new_xp = self.get_total_xp()
            if new_xp != last_xp:
                break
            else:
                counter += 1
                self.log_msg(f"Seconds elapsed: {counter}")
                time.sleep(1)
    

    def firemaking_spot(self):
        tile = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(tile.random_point())
        self.mouse.click()
        self.log_msg("Running to firemaking spot.")
        time.sleep(10)