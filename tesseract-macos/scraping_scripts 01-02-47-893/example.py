from scraper import TimeTableScraper, FerryCompany


scr = TimeTableScraper()

pentland_ferries_timetables = scr.get_timetables_for_company(
    FerryCompany.PENTLANDFERRIES)


for timetable in pentland_ferries_timetables:
    print(timetable, '\n')
