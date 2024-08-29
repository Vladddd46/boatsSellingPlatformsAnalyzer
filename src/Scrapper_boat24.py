import requests
import aiohttp
import asyncio
import json
import os
from bs4 import BeautifulSoup
from src.Scrapper import Scrapper
from src.utils.adapters import boat24_json_to_ad, json_to_ad
from src.utils.utils import save_json_data, is_file_exist, read_json_file


class Scrapper_boat24(Scrapper):

    def __init__(self, url="https://www.boat24.com/en/secondhandboats/"):
        self.m_url = url
        self.m_cache_details_links_filepath = (
            "data/tmp_boat24_cache_retrieved_links.json"
        )
        self.m_cache_ads = "data/tmp_boat24_cache_ads.json"
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()  # Synchronization primitive to prevent data race

    async def get_page_async(self, url, session):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to retrieve {url}")
                    return None
        except Exception as e:
            print(f"Exception occurred while getting page: {e}")
            return None

    async def get_max_page_number_async(self):
        async with aiohttp.ClientSession() as session:
            response = await self.get_page_async(self.m_url, session)
            if response:
                soup = BeautifulSoup(response, "html.parser")
                pagination = soup.find("ul", class_="pagination__pages")
                max_page = int(pagination.find_all("li")[-1].text.strip())
                return max_page
        return 1

    def extract_ad_links(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")
        ad_links = set()
        for link in soup.select('a[href*="/detail/"]'):
            ad_links.add(link.get("href"))
        return [{"url": i, "is_visited": False} for i in ad_links]

    async def get_links_to_ad_details_async(self, num_of_pages=None):
        async with aiohttp.ClientSession() as session:
            max_page = await self.get_max_page_number_async()
            if num_of_pages:
                max_page = min(max_page, num_of_pages)

            tasks = []
            for page_number in range(1, max_page + 1):
                requested_page = (page_number * 20) - 20
                url = f"{self.m_url}?page={requested_page}"
                task = asyncio.create_task(
                    self.fetch_page_and_extract_links(
                        url, session, page_number, max_page
                    )
                )
                tasks.append(task)

            all_ad_links = await asyncio.gather(*tasks)
            return [link for sublist in all_ad_links for link in sublist]

    async def fetch_page_and_extract_links(self, url, session, page_number, max_page):
        page_content = await self.get_page_async(url, session)
        if page_content:
            ad_links = self.extract_ad_links(page_content)
            print(f"Scraped page {page_number}/{max_page}")
            return ad_links
        else:
            print(f"Failed to scrape page {page_number}/{max_page}")
            return []

    async def get_ad_details_async(self, ad_details_page_url, session, i, max_ads_num):
        try:
            async with session.get(ad_details_page_url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                boat_info = {}

                # Extract ads_name (Boat Name)
                titles = soup.find_all(
                    ["h1", "h2", "h3", "h4", "h5", "h6"],
                    class_="heading__title heading__title--icon-right",
                )
                boat_info["ads_name"] = (
                    titles[0].get_text(strip=True) if len(titles) > 0 else None
                )
                # Extract price and currency
                boat_info["price"] = None
                boat_info["currency"] = None
                price = soup.find("span", class_="list__value list__value--large")
                if price:
                    tmp = price.get_text(strip=True).split()
                    boat_info["currency"] = tmp[0]
                    if boat_info["currency"] == "£":
                        boat_info["currency"] = "GBP"
                    try:
                        boat_info["price"] = float(
                            tmp[1].split(",")[0].replace(".", "")
                        )
                    except:
                        boat_info["price"] = None

                # Extract favorites_count
                boat_info["favorites_count"] = None
                favorites_tag_tags = soup.find_all("span")
                for tag in favorites_tag_tags:
                    boat_info["favorites_count"] = 0
                    if "In the favorites of " in tag.text:
                        boat_info["favorites_count"] = tag.text.split("In the favorites of")[1].strip().split()[0]
                        if boat_info["favorites_count"] == "one":
                            boat_info["favorites_count"] = 1
                        boat_info["favorites_count"] = int(boat_info["favorites_count"])
                        break

                # Extract year_built
                year_built = soup.find("span", string="Year Built")
                try:
                    boat_info["year_built"] = (
                        int(year_built.find_previous("span").get_text(strip=True))
                        if year_built
                        else None
                    )
                except:
                    boat_info["year_built"] = None

                # Extract ad_date
                boat_info["ad_date"] = ""
                ad_date_tags = soup.find_all("li")
                for ad_date_tag in ad_date_tags:
                    if "Ad Date" in ad_date_tag.text:
                        boat_info["ad_date"] = ad_date_tag.text.split("Ad Date: ")[
                            1
                        ].strip()

                # Extract views
                boat_info["views"] = None
                views_tags = soup.find_all("li", class_="text text--light text--small")
                for tag in views_tags:
                    if "Views" in tag.text:
                        boat_info["views"] = tag.find("strong").text.strip().split()[0]
                        if "'" in boat_info["views"]:
                            boat_info["views"] = boat_info["views"].replace("'", "")
                        try:
                            boat_info["views"] = int(boat_info["views"]) - 1
                        except:
                            boat_info["views"] = None
                boat_info["id"] = ad_details_page_url.split("/")[-2]
                # Include 'other' field
                boat_info["other"] = None

                if i % 100 == 0:
                    print(f"Retrieved ad details {i + 1}/{max_ads_num}")
                return boat_info

        except Exception as e:
            print(
                f"Exception occurred while retrieving ad details {i + 1}/{max_ads_num}: {e}"
            )
            return None

    async def get_ads_async(self, num_of_pages=None):
        container = []

        # Load ads links if cached, otherwise fetch them
        if is_file_exist(self.m_cache_details_links_filepath):
            async with self.lock:  # Ensure single access to file
                ads = read_json_file(self.m_cache_details_links_filepath)
        else:
            ads = await self.get_links_to_ad_details_async(num_of_pages)
            async with self.lock:  # Ensure single access to file
                save_json_data(self.m_cache_details_links_filepath, ads)

        max_ads_num = sum(1 for item in ads)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, ad in enumerate(ads):
                if not ad["is_visited"]:
                    task = asyncio.create_task(
                        self.get_ad_details_async(ad["url"], session, i, max_ads_num)
                    )
                    tasks.append(task)

                # Fetch ad details for every 200 ads or when reaching the end
                if len(tasks) >= 200 or i == len(ads) - 1:
                    ad_details_list = await asyncio.gather(*tasks)

                    # Process and cache the results after every 200 ads
                    for j, ad_details in enumerate(ad_details_list):
                        ad_index = i - len(tasks) + j + 1  # Find the original index
                        if ad_details:
                            async with self.lock:  # Ensure single access to shared data
                                container.append(
                                    boat24_json_to_ad(ad_details).to_json()
                                )
                                ads[ad_index]["is_visited"] = True

                    # Ensure safe access to file for writing
                    async with self.lock:
                        tmp = (
                            read_json_file(self.m_cache_ads)
                            if is_file_exist(self.m_cache_ads)
                            else []
                        )
                        tmp.extend(container)
                        container = []  # Reset container after saving
                        save_json_data(self.m_cache_details_links_filepath, ads)
                        save_json_data(self.m_cache_ads, tmp)

                    tasks = []  # Reset tasks for the next batch

        # Ensure any remaining ads are saved
        async with self.lock:  # Ensure safe access to file for writing
            tmp = (
                read_json_file(self.m_cache_ads)
                if is_file_exist(self.m_cache_ads)
                else []
            )
            tmp.extend(container)
            save_json_data(self.m_cache_details_links_filepath, ads)
            save_json_data(self.m_cache_ads, tmp)

        # Convert all ads to Ad objects
        result = []
        async with self.lock:  # Ensure single access to shared data
            for ad in tmp:
                tmp_ad = json_to_ad(ad)
                result.append(tmp_ad)
        return result

    def get_ads(self, num_of_pages=None):
        return self.loop.run_until_complete(self.get_ads_async(num_of_pages))
