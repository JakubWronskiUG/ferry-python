from bs4 import BeautifulSoup
import cv2
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
        
        image = Image.open(requests.get(url, stream=True).raw)
        image = image.save('savedimage.jpg')
        im1 = cv2.imread('savedimage.jpg', 0)
        im = cv2.imread('savedimage.jpg')
        ret,thresh_value = cv2.threshold(im1,180,255,cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5),np.uint8)
        dilated_value = cv2.dilate(thresh_value,kernel,iterations = 1)

        contours, hierarchy = cv2.findContours(dilated_value,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        cordinates = []
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            cordinates.append((x,y,w,h))
            #bounding the images
            if y< 50:
                cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),1)

        
        # plt.show()
        cv2.namedWindow('detecttable', cv2.WINDOW_NORMAL)
        cv2.imwrite('detecttable.jpg',im)
        

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
