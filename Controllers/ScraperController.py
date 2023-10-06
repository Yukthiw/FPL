from Scrapers import fpl_api_scraper, fpl_fbref_scraper, fpl_fbref_team_scraper


class ScraperController():
    def get_player_data(self, url, target):
        scraper = fpl_fbref_scraper.FPLFbrefScraper(url, target)
        scraper.scrape()

    def get_api_data(self, url, target):
        scraper = fpl_api_scraper.FPLScraper(url, target)
        scraper.scrape()

    def get_team_data(self, url, target):
        scraper = fpl_fbref_team_scraper.TeamScraper(url, target)
        scraper.scrape()
