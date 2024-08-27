from src.Scrapper import Scrapper
import requests
from bs4 import BeautifulSoup
from src.utils.adapters import boat24_json_to_ad
from src.utils.utils import save_json_data, is_file_exist, read_json_file

class Scrapper_boat24(Scrapper):

	def __init__(self, url="https://www.boat24.com/en/secondhandboats/"):
		self.m_url = url
		self.m_cache_details_links_filepath = "data/tmp_boat24_cache_retrieved_links.json"
		self.m_cache_ads = "data/tmp_boat24_cache_ads.json"

	def __get_page(self, url):
		response = requests.get(url)
		if response.status_code == 200:
			return response.text
		else:
			print(f"Failed to retrieve {url}") # Todo add logger
			return None

	def __get_max_page_number(self):
		response = self.__get_page(self.m_url)
		soup = BeautifulSoup(response, 'html.parser')
		# Find the pagination section
		pagination = soup.find('ul', class_='pagination__pages')
		# Extract the last page number
		max_page = int(pagination.find_all('li')[-1].text.strip())
		return max_page


	def __extract_ad_links(self, page_content):
		soup = BeautifulSoup(page_content, 'html.parser')
		ad_links = set()
		# Find all links to boat details
		for link in soup.select('a[href*="/detail/"]'):
			ad_links.add(link.get('href'))
		res = []
		for i in ad_links:
			res.append({"url": i, "is_visited": False})
		return res

	# get linkto each ad detail page, posted on the website.
	def __get_links_to_ad_details(self, num_of_pages=None):
		max_page = self.__get_max_page_number()
		page_number = 1
		all_ad_links = []

		while True:
			try:
				print(f"Scraping page {page_number}/{max_page}")
				requested_page = (page_number * 20) - 20 # pages are paggined by 20.
				url = f"{self.m_url}?page={requested_page}"
				page_content = self.__get_page(url)
				if not page_content:
					break  # Stop if the page could not be retrieved
				
				ad_links = self.__extract_ad_links(page_content)
				
				if not ad_links:
					print("No more ads found. Exiting.")
					break  # Stop if no more ads are found
				all_ad_links.extend(ad_links)
			except Exception as e:
				print(f"Exception occured during getting link to page with details: {e}")
			
			page_number += 1
			if (num_of_pages != None and page_number > num_of_pages) or (page_number > max_page):
				break
		return all_ad_links
	
	def __get_ad_details(self, ad_details_page_url):
		response = requests.get(ad_details_page_url)
		soup = BeautifulSoup(response.content, 'html.parser')
		boat_info = {}

		# Extract ads_name (Boat Name)
		title = soup.find('h2', class_='heading__title')
		boat_info['ads_name'] = title.get_text(strip=True) if title else None
		
		# Extract price and currency
		boat_info['price'] = None
		boat_info['currency'] = None
		price = soup.find('span', class_='list__value list__value--large')
		if price:
			tmp = price.get_text(strip=True).split()
			boat_info['currency'] = tmp[0]
			try:
				boat_info['price'] = float(tmp[1].split(",")[0].replace('.', ''))
			except:
				boat_info['price'] = None
		# Extract favorites_count
		boat_info['favorites_count'] = None
		favorites_tag_tags = soup.find_all('span')
		for tag in favorites_tag_tags:
			if "In the favorites of " in tag.text:
				boat_info['favorites_count'] = tag.text.split("In the favorites of")[1].strip().split()[0]

		# Extract year_built
		year_built = soup.find('span', string='Year Built')
		boat_info['year_built'] = year_built.find_previous('span').get_text(strip=True) if year_built else 'N/A'

		# Extract ad_date
		boat_info['ad_date'] = ""
		ad_date_tags = soup.find_all('li')
		for ad_date_tag in ad_date_tags:
			# Check if the <li> tag contains "Ad Date"
			if "Ad Date" in ad_date_tag.text:
				# Extract the date part after "Ad Date: "
				boat_info['ad_date'] = ad_date_tag.text.split("Ad Date: ")[1].strip()

		# Extract views
		boat_info['views'] = ""
		views_tags = soup.find_all('li', class_='text text--light text--small')
		for tag in views_tags:
			if "Views" in tag.text:
				boat_info['views'] = tag.find('strong').text.strip().split()[0]
				if '\'' in boat_info["views"]:
					boat_info["views"] = boat_info["views"].replace("'", "")
				try:
					boat_info["views"] = int(boat_info["views"])-1 # -1 because each time we can the page, the views counter increases
				except:
					boat_info["views"] = None

		# Include 'other' field (can be None for now)
		boat_info['other'] = None
		return boat_info

	def get_ads(self, num_of_pages=None):
		if is_file_exist(self.m_cache_details_links_filepath) == True:
			ads = read_json_file(self.m_cache_details_links_filepath)
		else:
			ads = self.__get_links_to_ad_details(num_of_pages)
		save_json_data(self.m_cache_details_links_filepath, ads)

		# container for storing ads details.
		container = []
		# maximum number of unvisited(unparsed) ads details.
		max_ads_num = sum(1 for item in ads if not item["is_visited"])

		for i in range(0, len(ads)):
			
			# if add details are not parsed yet.
			if ads[i]["is_visited"] == False:
				
				# caching condition: each 200 details do caching
				if i%200 == 0:
					tmp = []
					if is_file_exist(self.m_cache_ads) == True:
						tmp = read_json_file(self.m_cache_ads)
					tmp.extend(container)
					container = []
					save_json_data(self.m_cache_details_links_filepath, ads)
					save_json_data(self.m_cache_ads, tmp)
				res = self.__get_ad_details(ads[i]["url"])
				container.append(boat24_json_to_ad(res).to_json())
				ads[i]["is_visited"] = True
				print(f"Retrieving ads details: {i}/{max_ads_num}")
		
		tmp = []
		if is_file_exist(self.m_cache_ads) == True:
			tmp = read_json_file(self.m_cache_ads)
			tmp.extend(container)
			save_json_data(self.m_cache_details_links_filepath, ads)
			save_json_data(self.m_cache_ads, tmp)
		print("Ads are pased")
		return ads


