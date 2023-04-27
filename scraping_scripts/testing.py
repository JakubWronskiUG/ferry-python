import scraper
from objects.ferry_companies import FerryCompany, CompanyInfoGetter

# scraper.Scraper.scrape_jpg_tables('https://www.calmac.co.uk/image/8026/Table-11-Oban---Craignure-Winter-2022---2023-timetable---This-image-is-currently-not-accessible-to-screen-readers.-Please-phone-0800-066-5000-for-timetable-details/original.jpg?m=1668190374640')
ret = scraper.Scraper.scrape_jpg_tables(CompanyInfoGetter.get_company_timetable_urls(FerryCompany.CALMAC)[1])
print(ret.get_times())
# scraper.Scraper.scrape_html_tables('https://pentlandferries.co.uk/timetable-2/')
