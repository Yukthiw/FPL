from ScraperController import ScraperController


def print_option_list():
    print("Welcome to FPL Scraper Tool")
    print("Please choose an option: \n")
    print("1. Scrape Player Data \n 2. Scape FPL Data \n 3. Scrape Team Data \n 4. Scrape All \n q Quit \n")


class CLIController:
    def __init__(self):
        pass

    if __name__ == "__main__":
        is_running = True
        while is_running:
            print_option_list()
            scraper_controller = ScraperController()
            user_input = input("Enter desired option number: \n")
            if user_input == "1":
                scraper_controller.get_player_data('https://fbref.com/en/comps/9/Premier-League-Stats', '/Data/')
            elif user_input == "2":
                scraper_controller.get_api_data(None, 'Data')
            elif user_input == "3":
                scraper_controller.get_team_data('https://fbref.com/en/comps/9/Premier-League-Stats', '/Data/')
            elif user_input == 'q' or user_input == 'Q':
                exit()
            else:
                print("Invalid Input")
