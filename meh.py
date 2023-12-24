import requests
import json
from requests_cache import CachedSession

PAGE_SIZE = 1000

# client = requests.Session()
client = CachedSession('plex_cache')
client.headers.update({
	'accept': 'application/json, text/plain, */*'
})

PLEX_URL = None
PLEX_TOKEN = None

# ----------------------------------------------------------------------

def process_episodes(response):
	episodes_json = response['Metadata']
	# episodes_json = json.loads(response.content)['MediaContainer']['Metadata']
	# Loop through each episode and get its direct download link
	for episode in episodes_json:
		# episode_title = episode["title"]
		# episode_season = episode["parentIndex"]
		# episode_number = episode["index"]
		# episode_key = episode["key"]
		# print(episode)
		file_info = episode["Media"][0]["Part"][0]
		episode_file_name = file_info["file"].split('/')[-1]
		episode_file_key = file_info["key"]
		url = f"{PLEX_URL}{episode_file_key}?download=1&X-Plex-Token={PLEX_TOKEN}"
		with open('out.txt', 'a') as f:
			print(episode_file_name)
			# print(f"Season {episode_season} Episode {episode_number}: {episode_title}")
			f.write(f"{url}\n")
			# f.write

# ----------------------------------------------------------------------

def process_movies(movies_json):
	for movie in movies_json:
		file_info = movie["Media"][0]["Part"][0]
		episode_file_name = file_info["file"].split('/')[-1]
		episode_file_key = file_info["key"]
		url = f"{PLEX_URL}{episode_file_key}?download=1&X-Plex-Token={PLEX_TOKEN}"
		if episode_file_name in d:
			print(f"-[SKIPPED]-{episode_file_name}")
			return
		d[episode_file_name] = url
		print(episode_file_name)
	# with open('out.txt', 'a') as f:
	# 	print(f"Season {episode_season} Episode {episode_number}: {episode_title}")
	# 	# f.write(f"{url}\n")

# ----------------------------------------------------------------------

def fetch_all_meta(url, params_extra={}):
	p_cur = p.copy()
	p_cur.update(params_extra)
	meta_items = []
	res = client.get(url, params=p_cur).json()["MediaContainer"]
	total_items = res['totalSize']
	pages = int(total_items/PAGE_SIZE + 1)

	print('Getting Page: ')
	for i in range(pages):
		print(f"{i + 1} ")
		p_cur['X-Plex-Container-Start'] = str(i * PAGE_SIZE)
		res = client.get(url, params=p_cur).json()
		meta_items += res['MediaContainer']['Metadata']
	return meta_items

# ----------------------------------------------------------------------

def handle_movie_library(library):
	library_key = library
	url = f"{PLEX_URL}/library/sections/{library_key}/all"
	movies = fetch_all_meta(url)
	print(f'Found {len(movies)} shows')
	process_movies(movies)


def handle_tv_library(library):
	library_key = library
	# print(f"Scanning TV library {library['title']}")
	# Get the list of all TV shows in the library
	url = f"{PLEX_URL}/library/sections/{library_key}/all"
	shows = fetch_all_meta(url)
	print(f'Found {len(shows)} shows')
	
	# Loop through each TV show and get its list of seasons and episodes
	for show in shows:
		# show = shows[6]
		show_title = show["title"]
		show_key = show["key"].replace('/children', '')
		print(f"\nScanning TV show {show_title}")

		url = f"{PLEX_URL}{show_key}/allLeaves?X-Plex-Token={PLEX_TOKEN}"
		seasons_json = client.get(url, params=p).json()['MediaContainer']

		process_episodes(seasons_json)

PLEX_URL = 'https://12345.plex.direct:12345'
PLEX_TOKEN = '12345'
p = {
    "sort": "titleSort",
    "X-Plex-Container-Start": 0,
    "X-Plex-Container-Size": PAGE_SIZE,
    "X-Plex-Token": PLEX_TOKEN
}
# handle_movie_library(3)
handle_tv_library(6)

# with open('TV_Shows.json', 'w', encoding ='utf8') as json_file:
#     json.dump(d, json_file, ensure_ascii = True, indent = 4)

# with open('Movies.txt', 'a') as f:
# with open(f'TV Shows.txt', 'a') as f:
#     for l in d.values():
#         f.write(l+'\n')

# url = f"{PLEX_URL}/library/sections?X-Plex-Token={PLEX_TOKEN}"
# libraries_json = client.get(url).json()
# print(libraries_json)

# for library in libraries_json["MediaContainer"]["Directory"]:
# 	library_type = library["type"]
# 	print(f'{library["key"]} | {library["type"]} | {library["title"]}')
	
	# if library_type == "movie":
	# 	handle_movie_library(library)
	# elif library_type == "show":
	# 	handle_tv_library(library)
	# else:
	# 	print(f"Skipping unknown library type {library_type}")
	# 	continue

	
