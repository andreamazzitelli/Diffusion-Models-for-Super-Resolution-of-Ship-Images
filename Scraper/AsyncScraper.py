import io
import os
import time
import tqdm

import asyncio
import aiohttp
import aiofiles
import random
import pandas as pd

from PIL import Image
from lxml import etree
from pathlib import Path
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class AsyncScraper():
    def __init__(self, n_tasks, destination_folder='./images/', urls_file='./urls.csv', missing_image_file='./missing_image.csv',error_file='./error.csv', headers=None):

        self.n_tasks = n_tasks
        self.pbar = None
        self.fake_user_agent = UserAgent()

        self.destination_folder = destination_folder
        Path(destination_folder).mkdir(parents=True, exist_ok=True)

        self.urls_file = urls_file
        self.missing_image_file = missing_image_file
        self.error_file = error_file

        if not os.path.exists(self.urls_file):
            raise Exception("Missing File with urls list")
        if not os.path.exists(self.error_file):
            pd.DataFrame(columns=['url', 'id']).to_csv(
                self.error_file, index=False, header=True)
        if not os.path.exists(self.missing_image_file):
            pd.DataFrame(columns=['url', 'id']).to_csv(
                self.missing_image_file, index=False, header=True)

        self.session = None

        self.headers = headers if headers is not None else {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Referer': 'http://www.google.com/'
        }

    def run(self):

        start_time = time.time()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
        loop.close()

        time_difference = time.time() - start_time
        print(f'Completed Execution in %.2f seconds.' % time_difference)

    async def main(self):

        done = False

        while not done:

            self.headers['User-Agent'] = self.fake_user_agent.random

            tasks = []
            self.session = aiohttp.ClientSession(headers=self.headers)

            csv_data = pd.read_csv(self.urls_file)
            tail_len = len(csv_data.index) - self.n_tasks

            head_data = csv_data.head(self.n_tasks)
            tail_data = csv_data.tail(tail_len).to_csv(
                './urls.csv', index=False, header=True)

            head_len = len(head_data.index)
            done = True if head_len < self.n_tasks else False

            for _, row in head_data.iterrows():
                task = asyncio.create_task(
                    self.scrape(row['url'], row['id']))
                tasks.append(task)

            self.pbar = tqdm.tqdm(total=head_len, desc='Scraped files')

            await asyncio.gather(*tasks)
            await self.session.close()

    def _cut_url_parameters(self, url) -> str:
        return url.split('?')[0]

    async def _write_problematic(self, file_path, url, id):
        async with aiofiles.open(file_path, 'a') as file:
            await file.write(f"{url},{id}\n")

    async def _save_metadata_csv(self, data_dict, destination_folder):
        metadata_path = f'{destination_folder}/metadata.csv'
        csv_headers = False if os.path.exists(metadata_path) else True

        async with aiofiles.open(metadata_path, 'a') as fp:

            if csv_headers:
                keys = [key for key in data_dict.keys()]
                headers = ','.join(keys) + '\n'
                await fp.write(headers)

            values = [str(data_dict[key]) for key in data_dict.keys()]
            line = ','.join(values) + '\n'
            await fp.write(line)

    async def _save_data(self, image_url, id, data_dict, destination_folder):

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(image_url) as response:
                body = await response.read()
                await asyncio.sleep(1)

                image = Image.open(io.BytesIO(body))
                width, height = image.size

                image.crop((0, 0, width, height - 20)
                           ).save(f"{destination_folder}/{id}.jpg")

        await self._save_metadata_csv(data_dict, destination_folder)

    async def scrape(self, url, id):

        try:

            async with self.session.get(url) as response:
                body = await response.text()
                await asyncio.sleep(1)
                bs = BeautifulSoup(body, 'html.parser')
                dom = etree.HTML(str(bs))

                if dom is None:

                    string_version = str(bs)

                    start_pos = string_version.find('<div id="root">')
                    end_token = "Privacy Policy</a></div></div></div></div></div></div></div>"
                    end_pos = string_version.find(end_token)
                    string_version = string_version[start_pos: end_pos + len(end_token)]

                    dom = etree.HTML(string_version)

                ship_category = dom.xpath(
                    '//span[contains(., "Photo Category")]/following-sibling::span/a')
                ship_category = ship_category[0].text if ship_category else "None"

                ship_image = dom.xpath(
                    "//img[contains(@alt, 'Ship') and contains(@title, 'Click to see Full Screen')]")
                ship_image = self._cut_url_parameters(
                    ship_image[0].attrib["src"]) if ship_image else None

                if ship_image is None:
                    await self._write_problematic(self.missing_image_file, url, id)
                    self.pbar.update(1)
                    return

                image_title = dom.xpath(
                    '//div[contains(@class, "summary-photo__title")]/h1/strong')
                image_title = image_title[0].text.replace(
                    ',', ' ') if image_title else "None"

                vessel_type = dom.xpath(
                    '//span[contains(., "Vessel Type")]/following-sibling::span')
                vessel_type = vessel_type[0].text.replace(
                    ',', ' ') if vessel_type else "None"

                current_name = dom.xpath(
                    '//span[contains(., "Current name")]/following-sibling::span/a')
                current_name = current_name[0].text.replace(
                    ',', '') if current_name else "None"

                previous_names = dom.xpath(
                    '//p[contains(., "Former name(s)")]/following-sibling::div/p/a')
                previous_names = [name.text.replace(
                    ',', ' ').replace("'", ' ') for name in previous_names]

                gross_tonnage = dom.xpath(
                    '//span[contains(., "Gross")]/following-sibling::span')
                gross_tonnage = gross_tonnage[0].text.replace(
                    ',', '') if gross_tonnage else "None"

                dwt = dom.xpath(
                    '//span[contains(., "DWT")]/following-sibling::span')
                dwt = dwt[0].text.replace(',', '') if dwt else "None"

                length = dom.xpath(
                    '//span[contains(., "Length")]/following-sibling::span')
                length = length[0].text.replace(',', '') if length else "None"

                beam = dom.xpath(
                    '//span[contains(., "Beam")]/following-sibling::span')
                beam = beam[0].text.replace(',', '') if beam else "None"

                draught = dom.xpath(
                    '//span[contains(., "Draught")]/following-sibling::span')
                draught = draught[0].text.replace(
                    ',', '') if draught else "None"

                ship_data = {
                    "image_id": id,
                    "image_title": image_title,
                    "vessel_type": vessel_type,
                    "ship_category": ship_category,
                    "current_name": current_name,
                    "previous_names": '"' + str(previous_names) + '"',
                    "gross_tonnage": gross_tonnage,
                    "dwt": dwt,
                    "length": length,
                    "beam": beam,
                    "draught": draught
                }

                destination_folder = f"{self.destination_folder}{ship_category.replace('/', ' - ')}"
                Path(destination_folder).mkdir(parents=True, exist_ok=True)

                await self._save_data(ship_image, id, ship_data, destination_folder)
                await asyncio.sleep(random.randint(3, 5))

                self.pbar.update(1)

        except:
            await self._write_problematic(self.error_file, url, id)
            self.pbar.update(1)


n_tasks = 400
scraper = AsyncScraper(n_tasks=n_tasks)
scraper.run()
