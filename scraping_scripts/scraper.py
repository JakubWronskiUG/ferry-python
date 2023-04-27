import datetime
from bs4 import BeautifulSoup
import cv2
import pytesseract
import numpy as np
from PIL import Image
import requests
import pandas as pd
from objects.ferry_companies import FerryCompany, CompanyInfoGetter, ScrapingType, COMPANIES
from objects.ports import Port, PortInfoGetter
from objects.timetable import Timetable


class CompanyNotSupportedException(Exception):
    pass


class ScrapingMethodDidNotWorkOnAWebsite(Exception):
    pass


class Scraper:

    def scrape_html_tables(url):
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')

            table_sections = soup.find_all(class_='timetab')

            timetables = []

            for i, table_section in enumerate(table_sections):
                
                if i > 1:
                    continue

                table_title = table_section.h5.text
                headers_set = table_section.find_all('th')
                headers = [header.text for header in headers_set]
                data = pd.DataFrame(columns=headers)

                duration = CompanyInfoGetter.get_company_default_trip_duration(FerryCompany.PENTLANDFERRIES)
                ferry_id = CompanyInfoGetter.get_company_default_ferry_id(FerryCompany.PENTLANDFERRIES)
                departure_port = PortInfoGetter.get_port_from_text(table_title)
                arrival_port  = Port.GILLSBAY if departure_port == Port.STMARGARETSHOPE else Port.STMARGARETSHOPE

                timetable = Timetable(departure_port, arrival_port, ferry_id)
                
                rows = table_section.find_all('tr')[1:]

                for row in rows:
                    row_data = row.find_all('td')
                    row_text = [i.text for i in row_data]
                    length = len(data)
                    data.loc[length] = row_text

                for column in data.columns:
                    weekday = column.lower()
                    timetable.load_route(
                        departures = data[column],
                        arrivals = [str((datetime.datetime(100, 1, 1, int(time.split(':')[0]), int(time.split(':')[1]), 0) + datetime.timedelta(minutes=duration)).time())[:5]
                            for time in data[column]
                        ],
                        weekday = weekday
                    )
                    
                timetables.append(timetable)

            return timetables

        except Exception as e:
            print(e)
            raise ScrapingMethodDidNotWorkOnAWebsite

    def scrape_jpg_tables(url_touple):
        
        # print(url_touple)
        url = url_touple[0]
        dimensions = url_touple[1]
        departure_port = url_touple[2]
        arrival_port = url_touple[3]
        ferry_id = url_touple[4]
        ret = []

        filename = './scraping_scripts/assets/timetableimage.jpg'
        pytesseract.pytesseract.tesseract_cmd = r'./tesseract-macos/5.3.0_1/bin/tesseract'

        image = Image.open(requests.get(url, stream=True).raw)
        # image = image.crop((40, 315, 1200, 2605)) #TODO save image timetable sizes
        # image = image.crop((430, 315, 972, 2605)) #TODO save image timetable sizes
        image = image.crop(dimensions)
        image = image.save(filename)
        img = cv2.imread(cv2.samples.findFile(filename))
        cImage = np.copy(img)
        # cv2.imshow("image", img) #name the window as "image"
        # cv2.waitKey(0)
        # cv2.destroyWindow("image") #close the window

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (_, gray) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY) #remove grey pixels that mess up the IR
        canny = cv2.Canny(gray, 50, 150)
        # cv2.imshow("gray", gray)
        # cv2.waitKey(0)
        # cv2.destroyWindow("gray")
        # cv2.imshow("canny", canny)
        # cv2.waitKey(0)
        # cv2.destroyWindow("canny")


        # Using Hough Transform to find lines on the timetable image
        # cv.HoughLinesP(image, rho, theta, threshold[, lines[, minLineLength[, maxLineGap]]]) → lines
        rho = 1
        theta = np.pi/360
        threshold = 30
        minLineLength = 250
        maxLineGap = 25
        linesP = cv2.HoughLinesP(canny, rho , theta, threshold, None, minLineLength, maxLineGap)
        linesP = linesP if linesP is not None else []

        im1 = cv2.imread(filename, 0)
        im = cv2.imread(filename)

        def is_vertical(line):
            return line[0]==line[2]
        def is_horizontal(line):
            return line[1]==line[3]
        
        def overlapping_filter(lines, sorting_index, separation=5):
            filtered_lines = []
            lines = sorted(lines, key=lambda lines: lines[sorting_index])
            for i, line in enumerate(lines):    
                if i == 0:
                    filtered_lines.append(line)
                    continue
                prev_line = lines[i-1]
                if (line[sorting_index] - prev_line[sorting_index]) > separation:
                    filtered_lines.append(line)
            return filtered_lines

        horizontal_lines = []
        vertical_lines = []

        for l in [i[0] for i in linesP]:
            if is_vertical(l): 
                vertical_lines.append(l)   
            elif is_horizontal(l):
                horizontal_lines.append(l)

        horizontal_lines = overlapping_filter(horizontal_lines, 1)
        vertical_lines = overlapping_filter(vertical_lines, 0)

        # print(horizontal_lines)

        #draw the lines
        for i, line in enumerate(horizontal_lines):
            cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,255,0), 3, cv2.LINE_AA)
            cv2.putText(cImage, str(i) + "h", (line[0] + 5, line[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)                      
        for i, line in enumerate(vertical_lines):
            cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,0,255), 3, cv2.LINE_AA)
            cv2.putText(cImage, str(i) + "v", (line[0], line[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # cv2.imshow("with_line", cImage)
        # cv2.waitKey(0)
        # cv2.destroyWindow("with_line") #close the window
        # return
    
        first_line_index = 1
        last_line_index = 63

        def get_cropped_image(image, x, y, w, h):
            return image[ y:y+h , x:x+w ]
        
        def get_ROI(image, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index, offset=0):
            x1 = vertical[left_line_index][2] + offset
            y1 = horizontal[top_line_index][3] + offset
            x2 = vertical[right_line_index][2] - offset
            y2 = horizontal[bottom_line_index][3] - offset
            # print(horizontal[bottom_line_index])
            
            w = x2 - x1
            h = y2 - y1
            
            cropped_image = get_cropped_image(image, x1, y1, w, h)
            
            return cropped_image, (x1, y1, w, h)
        
        def detect(cropped_frame):
            return pytesseract.image_to_string(cropped_frame, config='--psm 10 -c tessedit_char_whitelist=0123456789')        

        print("Start detecting text...")

        timetable = Timetable(departure_port, arrival_port, "1")
        
        departures = []
        arrivals = []
        weekday_index = 0

        for i in range(1,len(horizontal_lines)-1):
            
            dep_cropped_image, _ = get_ROI(gray, horizontal_lines, vertical_lines, 0, 1, i, i+1)
            arr_cropped_image, _ = get_ROI(gray, horizontal_lines, vertical_lines, 1, 2, i, i+1)
            
            departure = detect(dep_cropped_image).strip()
            arrival = detect(arr_cropped_image).strip()
            if len(departure.strip()) < 2:
                # print('Lecimy z continue')
                if i == len(horizontal_lines) - 2:
                    timetable.load_route(departures, arrivals, timetable.weekdays[weekday_index])
                continue
            
            departure = departure[:2] + ':' + departure[2:4]
            arrival = arrival[:2] + ':' + arrival[2:4]
            
            departure = departure + "0" if len(departure) < 4 else departure
            arrival = arrival + "0" if len(arrival) < 4 else arrival


            if len(departures) > 0 and departures[len(departures)-1] > departure:
                timetable.load_route(departures, arrivals, timetable.weekdays[weekday_index])
                weekday_index += 1
                print('zmieniam index z', weekday_index - 1, 'na', weekday_index)
                departures = []
                arrivals = []
            
            arrivals.append(arrival)
            departures.append(departure)

            if i == len(horizontal_lines) - 2:
                timetable.load_route(departures, arrivals, timetable.weekdays[weekday_index])
        
        timetable.ferry_id = ferry_id
        ret.append(timetable)
        return ret

    website_scraping_method = {
        ScrapingType.HTMLTABLE: scrape_html_tables,
        ScrapingType.JPGTABLE: scrape_jpg_tables,
    }


class TimeTableScraper(Scraper):

    def get_timetables_for_company(self, company: FerryCompany) -> list:

        if company not in FerryCompany:
            raise CompanyNotSupportedException(
                f'Company {company} is not supported.')

        # select proper scraping tools
        scraping_type = CompanyInfoGetter.get_company_scraping_type(company)
        scraping_method = self.website_scraping_method[scraping_type]
        urls = CompanyInfoGetter.get_company_timetable_urls(company)
        print(urls,'\n\n----------')
        timetables = []

        # scrape
        for url in urls:
            try:
                for t in scraping_method(url):
                    timetables.append(t)
            except ScrapingMethodDidNotWorkOnAWebsite:
                print(
                    f'Scraping method {scraping_type} did not work for {url}. Check if website still supports this scraping method.')
                return None
            except Exception as e:
                print(e)
    
        return timetables
