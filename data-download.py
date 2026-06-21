import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_inside_airbnb_data(city_name, target_dir):
    """
    Automates downloading all available files for a specific city from Inside Airbnb.
    
    :param city_name: The name of the city exactly as it appears in the URL path (e.g., 'london', 'paris')
    :param target_dir: Local path where files should be saved
    """
    base_url = "https://insideairbnb.com/get-the-data/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"🕵️  Scraping page structural details for: {city_name.title()}...")
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"💥 Failed to connect to Inside Airbnb: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    os.makedirs(target_dir, exist_ok=True)
    
    # Inside Airbnb categorizes tables or sections by city sub-URLs. 
    # We look for links containing your target city (e.g., '/london/')
    download_urls = []
    city_pattern = re.compile(rf"/visualisations/custom-data/{city_name.lower()}/|/data.insideairbnb.com/.*{city_name.lower()}/")
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Catch both raw compressed csv files and geojson shapes tied to the city
        if city_name.lower() in href.lower() and (href.endswith('.csv.gz') or href.endswith('.geojson') or href.endswith('.csv')):
            # Resolve relative URLs to absolute URLs if necessary
            full_url = urljoin(base_url, href)
            if full_url not in download_urls:
                download_urls.append(full_url)

    if not download_urls:
        print(f"❌ No matching downloads found for city: '{city_name}'. Check your spelling or URL structure.")
        return

    print(f"📋 Found {len(download_urls)} files for {city_name.title()}. Starting pipeline execution...\n")

    # Ingestion Block
    for url in download_urls:
        # Extract meaningful filename from the URL structure
        # (e.g., http://.../london/2025-09-14/data/listings.csv.gz -> listings.csv.gz)
        url_parts = url.split('/')
        filename = url_parts[-1]
        
        # If the file names overlap (like multiple detailed vs summary files), append the scrape date prefix
        scrape_date = url_parts[-3] if len(url_parts) > 3 else "snapshot"
        if not filename.startswith(scrape_date) and len(scrape_date) == 10: # Check for YYYY-MM-DD
            local_filename = f"{filename}"
        else:
            local_filename = filename

        destination_path = os.path.join(target_dir, local_filename)
        
        print(f"📥 Stream Ingesting: {filename} ({scrape_date})")
        
        try:
            # Using stream=True prevents loading massive .csv.gz components directly into RAM
            with requests.get(url, headers=headers, stream=True) as file_stream:
                file_stream.raise_for_status()
                with open(destination_path, 'wb') as f:
                    for chunk in file_stream.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"     ✅ Saved: {local_filename}")
        except Exception as e:
            print(f"     ❌ Failed downloading {filename}: {e}")

    print(f"\n🚀 Pipeline processing complete. All files localized to:\n   {target_dir}")

# --- EXECUTE THE PIPELINE ---
if __name__ == "__main__":
    CITY = input("Enter the city name: ") # Replace with your target city keyword used on the site
    OUTPUT_FOLDER = f"d:/Data Engineer Assessment/{CITY}" # Local directory to save files, e.g., 'd:/Data Engineer Assessment/london'

    get_inside_airbnb_data(city_name=CITY, target_dir=OUTPUT_FOLDER)