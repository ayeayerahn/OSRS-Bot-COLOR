import time
import utilities.color as clr
import utilities.api.item_ids as ids
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSchop_and_firemake(OSRSBot):
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

            self.woodcut(api_m)
            self.firemake(api_m)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def woodcut(self, api_m: MorgHTTPSocket):
        if not api_m.get_is_inv_full():
            if tree := self.get_nearest_tag(clr.GREEN):
                self.mouse.move_to(tree.random_point())
                self.mouse.click()
                self.log_msg("Wooducutting until we have a full inventory.")
                time.sleep(3)
        while not api_m.get_is_player_idle():
            time.sleep(1)
        if api_m.get_is_inv_full():
            self.log_msg("Inventory is full. Time to firemake.")
            return self.firemaking_spot()
        else:
            return self.woodcut(api_m)       

    def firemake(self, api_m: MorgHTTPSocket):
        oak_logs = api_m.get_inv_item_indices(ids.logs)
        for i in oak_logs:
            oak_logs = api_m.get_inv_item_indices(ids.logs)
            self.mouse.move_to(self.win.inventory_slots[0].random_point())
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[oak_logs[0]].random_point())
            self.mouse.click()
            api_m.wait_til_gained_xp("Firemaking", 15)
        time.sleep(1)
        self.log_msg("Out of logs. Time to cut again.")

    def firemaking_spot(self):
        tile = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(tile.random_point())
        self.mouse.click()
        self.log_msg("Running to firemaking spot.")
        time.sleep(5)