from idealista_scraper import IdealistaScraper
import pandas as pd
import logging
from datetime import datetime
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize scraper
    scraper = IdealistaScraper()
    
    # Set search parameters
    city = "a-coruna-a-coruna"
    property_type = "local-comercial"
    operation = "venta"
    
    # Generate search URL
    search_url = scraper.generate_search_url(city, property_type, operation)
    print(f"Generated URL: {search_url}")
    logging.info(f"Starting scrape for URL: {search_url}")
    
    # Scrape properties
    properties = scraper.scrape_search_results(search_url)
    
    if not properties:
        logging.error("No properties were found. Exiting.")
        return
    
    # Output file
    output_file = "idealista_properties.csv"
    
    # Create DataFrame from properties
    new_df = pd.DataFrame(properties)
    
    # Update existing properties or create new file
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        # Merge old and new data
        df = pd.concat([existing_df, new_df])
        # Remove duplicates keeping latest version
        df = df.sort_values('last_updated').drop_duplicates(
            subset=['property_id'], 
            keep='last'
        )
    else:
        df = new_df
    
    # Add metadata
    df['last_query'] = datetime.now().isoformat()
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    # Log statistics
    new_properties = len(new_df)
    total_properties = len(df)
    logging.info(f"Total properties in database: {total_properties}")
    logging.info(f"New/updated properties: {new_properties}")
    logging.info(f"Data saved to {output_file}")

if __name__ == "__main__":
    main() 