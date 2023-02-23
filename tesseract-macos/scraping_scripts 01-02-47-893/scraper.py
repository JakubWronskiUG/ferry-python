from bs4 import BeautifulSoup
import cv2
import pytesseract
import numpy as np
from enum import Enum, auto
# import matplotlib as plt
from PIL import Image
import requests
from collections import namedtuple
import pandas as pd
from objects.ferry_companies import FerryCompany, CompanyInfoGetter, ScrapingType
from objects.ports import Port, PortInfoGetter


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

            TimetableTouple = namedtuple(
                "TimetabelsTouple", "timetable heading")

            return_touples = []

            for table_section in table_sections:

                table_title = table_section.h5.text
                headers = []
                headers_set = table_section.find_all('th')
                for header in headers_set:
                    headers.append(header.text)
                data = pd.DataFrame(columns=headers)

                rows = table_section.find_all('tr')[1:]

                for j in rows:
                    row_data = j.find_all('td')
                    row = [i.text for i in row_data]
                    length = len(data)
                    data.loc[length] = row

                t = TimetableTouple(data, table_title)

                return_touples.append(t)

            return return_touples

        except Exception as e:
            print(e)
            raise ScrapingMethodDidNotWorkOnAWebsite

    def scrape_jpg_tables(url):
        
        filename = 'assets/timetableimage.jpg'

        image = Image.open(requests.get(url, stream=True).raw)
        image = image.save(filename)
        img = cv2.imread(cv2.samples.findFile(filename))
        cImage = np.copy(img)
        # cv2.imshow("image", img) #name the window as "image"
        # cv2.waitKey(0)
        # cv2.destroyWindow("image") #close the window

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, 50, 150)
        # cv2.imshow("gray", gray)
        # cv2.waitKey(0)
        # cv2.destroyWindow("gray")
        # cv2.imshow("canny", canny)
        # cv2.waitKey(0)
        # cv2.destroyWindow("canny")

        # cv.HoughLinesP(image, rho, theta, threshold[, lines[, minLineLength[, maxLineGap]]]) → lines
        rho = 1
        theta = np.pi/180
        threshold = 50
        minLinLength = 500
        maxLineGap = 25
        linesP = cv2.HoughLinesP(canny, rho , theta, threshold, None, minLinLength, maxLineGap)
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

        for i, line in enumerate(horizontal_lines):
            cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,255,0), 3, cv2.LINE_AA)
            cv2.putText(cImage, str(i) + "h", (line[0] + 5, line[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)                      
        for i, line in enumerate(vertical_lines):
            cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,0,255), 3, cv2.LINE_AA)
            cv2.putText(cImage, str(i) + "v", (line[0], line[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow("with_line", cImage)
        cv2.waitKey(0)
        cv2.destroyWindow("with_line") #close the window

        keywords = ['Day',
                    'Glasgow Queen St - Oban Departure',
                    'Glasgow Queen St - Oban Arrival',
                    'Oban - Craignure Departure',
                    'Oban - Craignure Arrival',
                    'Craignure - Oban Departure',
                    'Craignure - Oban Arrival',
                    'Oban - Glasgow Queen St Arrival',
                    'Oban - Glasgow Queen St Departure']
        dict_columns = {k : [] for k in keywords}

        counter = 0

        first_line_index = 1
        last_line_index = 63

        def get_cropped_image(image, x, y, w, h):
            return image[ y:y+h , x:x+w ]
        
        def get_ROI(image, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index, offset=4):
            x1 = vertical[left_line_index][2] + offset
            y1 = horizontal[top_line_index][3] + offset
            x2 = vertical[right_line_index][2] - offset
            y2 = horizontal[bottom_line_index][3] - offset
            # print(horizontal[bottom_line_index])
            
            w = x2 - x1
            h = y2 - y1
            
            cropped_image = get_cropped_image(image, x1, y1, w, h)
            
            return cropped_image, (x1, y1, w, h)
        
        pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.3.0_1/bin/tesseract'

        def draw_text(src, x, y, w, h, text):
            cFrame = np.copy(src)
            cv2.rectangle(cFrame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(cFrame, "text: " + text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5, cv2.LINE_AA)
            return cFrame

        def detect(cropped_frame, is_number = False):
            if (is_number):
                text = pytesseract.image_to_string(cropped_frame,
                                                config ='-c tessedit_char_whitelist=0123456789 --psm 10 --oem 2')
            else:
                text = pytesseract.image_to_string(cropped_frame, config='--psm 10')        
                
            return text

        print("Start detecting text...")
        (thresh, bw) = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        for i in range(first_line_index, last_line_index):
            for j, keyword in enumerate(keywords):
                counter += 1
                    
                left_line_index = j
                right_line_index = j+1
                top_line_index = i
                bottom_line_index = i+1
                    
                cropped_image, (x,y,w,h) = get_ROI(bw, horizontal_lines, vertical_lines, left_line_index, right_line_index, top_line_index, bottom_line_index)
                    
                if (keywords[j]=='day'):
                    text = detect(cropped_image)
                    dict_day[keyword].append(text)
                
                else:
                    # text = detect(cropped_image, is_number=True)
                    text = detect(cropped_image)
                    dict_day[keyword].append(text)
                image_with_text = draw_text(img, x, y, w, h, text)
        
        for k in keywords:
            print(dict_day[k][0],dict_day[k][1], dict_day[k][61], len(dict_day[k]), '\n---------')


        # ret,thresh_value = cv2.threshold(im1,180,255,cv2.THRESH_BINARY_INV)
        # kernel = np.ones((5,5),np.uint8)
        # dilated_value = cv2.dilate(thresh_value,kernel,iterations = 1)

        # contours, hierarchy = cv2.findContours(dilated_value,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # cordinates = []
        # for cnt in contours:
        #     x,y,w,h = cv2.boundingRect(cnt)
        #     cordinates.append((x,y,w,h))
        #     #bounding the images
        #     if y< 50:
        #         cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),1)

        
        # # plt.show()
        # cv2.namedWindow('detecttable', cv2.WINDOW_NORMAL)
        # cv2.imwrite('detecttable.jpg',im)
        

    website_scraping_method = {
        ScrapingType.HTMLTABLE: scrape_html_tables,
        ScrapingType.JPGTABLE: scrape_jpg_tables,
    }


class TimeTableScraper(Scraper):

    def get_port_from_text(self, text: str) -> Port:
        for port in Port:
            # print(text)
            if text.lower().find(PortInfoGetter.get_port_name(port).lower()) != -1:
                # print("Found you!!!!", port)
                return port
        return None

    def get_timetables_for_company(self, company: FerryCompany) -> list:

        if company not in FerryCompany:
            raise CompanyNotSupportedException(
                f'Company {company} is not supported.')

        # return type
        TimetableInfoBlock = namedtuple(
            "TimetableInfoBlock", "timetable ferry_id port_from port_to")

        # select proper scraping tools
        scraping_type = CompanyInfoGetter.get_company_scraping_type(company)
        scraping_method = self.website_scraping_method[scraping_type]
        url = CompanyInfoGetter.get_company_timetable_url(company)
        timetables = []
        ferry_id = None

        # scrape
        try:
            timetables = scraping_method(url)
        except ScrapingMethodDidNotWorkOnAWebsite:
            print(
                f'Scraping method {scraping_type} did not work for {url}. Check if website still supports this scraping method.')
            return None
        except Exception as e:
            print(e)

        # assign metadata
        if company == FerryCompany.PENTLANDFERRIES:
            ferry_id = "1"

        return [TimetableInfoBlock(
            t.timetable,
            ferry_id,
            self.get_port_from_text(t.heading),
            Port.GILLSBAY if self.get_port_from_text(
                t.heading) == Port.STMARGARETSHOPE else Port.STMARGARETSHOPE
        ) for t in timetables]
