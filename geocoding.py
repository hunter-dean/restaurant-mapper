import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
import sys

class Restaurant:
    def __init__(self, est_id, establishment_name, c_out, nc_out, insp_date, lic_exp, lic_type, failed, address, city, state, zip_code, telephone, inspection_type_code, owner_name, county, calculated):
        self.est_id = est_id
        self.establishment_name = establishment_name
        self.c_out = c_out
        self.nc_out = nc_out
        self.insp_date = insp_date
        self.lic_exp = lic_exp
        self.lic_type = lic_type
        self.failed = failed
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.telephone = telephone
        self.inspection_type_code = inspection_type_code
        self.owner_name = owner_name
        self.county = county
        self.calculated = calculated
        self.latitude = None
        self.longitude = None

def geocode_address(address):
    geolocator = Nominatim(user_agent="restaurant_geocoder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        time.sleep(1)
        return None, None

input_filename = "export.csv"
output_filename = "restaurants.csv"

total_restaurants = 0
try:
    with open(input_filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["CITY"].strip().lower() == "portland":
                total_restaurants += 1
except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
    sys.exit()

if total_restaurants == 0:
    print("No restaurants found in the input file.")
    sys.exit()

print(f"Found {total_restaurants} total restaurants. Geocoding...")

restaurants = []
processed_count = 0

with open(input_filename, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["CITY"].strip().lower() == "portland":
            processed_count += 1
            percentage = (processed_count / total_restaurants) * 100
            print(f"Progress: {processed_count}/{total_restaurants} ({percentage:.2f}%)", end='\r')

            r = Restaurant(
                est_id=row["EST ID #"], establishment_name=row["ESTABLISHMENT_NAME"],
                c_out=row["C_OUT"], nc_out=row["NC_OUT"], insp_date=row["INSP_DATE"],
                lic_exp=row["LIC_EXP"], lic_type=row["LIC_TYPE"], failed=row["FAILED"],
                address=row["ADDRESS"], city=row["CITY"], state=row["STATE"],
                zip_code=row["ZIP"], telephone=row["TELEPHONE"],
                inspection_type_code=row["INSPECTION_TYPE_CODE"], owner_name=row["OWNER_NAME"],
                county=row["COUNTY"], calculated=row["CALCULATED"]
            )

            full_address = f"{r.address}, {r.city}, {r.state} {r.zip_code}"
            lat, lon = geocode_address(full_address)

            if lat and lon:
                r.latitude = lat
                r.longitude = lon
                restaurants.append(r)
                if len(restaurants) >= 4510:
                    break

print("\n")

output_headers = [
    "EST ID #", "ESTABLISHMENT_NAME", "C_OUT", "NC_OUT", "INSP_DATE",
    "LIC_EXP", "LIC_TYPE", "FAILED", "ADDRESS", "CITY", "STATE", "ZIP",
    "TELEPHONE", "INSPECTION_TYPE_CODE", "OWNER_NAME", "COUNTY", "CALCULATED",
    "latitude", "longitude"
]

with open(output_filename, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_headers, extrasaction='ignore')
    writer.writeheader()
    for r in restaurants:
        restaurant_data = {
            "EST ID #": r.est_id, "ESTABLISHMENT_NAME": r.establishment_name,
            "C_OUT": r.c_out, "NC_OUT": r.nc_out, "INSP_DATE": r.insp_date,
            "LIC_EXP": r.lic_exp, "LIC_TYPE": r.lic_type, "FAILED": r.failed,
            "ADDRESS": r.address, "CITY": r.city, "STATE": r.state,
            "ZIP": r.zip_code, "TELEPHONE": r.telephone,
            "INSPECTION_TYPE_CODE": r.inspection_type_code,
            "OWNER_NAME": r.owner_name, "COUNTY": r.county,
            "CALCULATED": r.calculated, "latitude": r.latitude, "longitude": r.longitude
        }
        writer.writerow(restaurant_data)

print(f"Finished. Geocoded {len(restaurants)} restaurants.")
print(f"Data has been written to {output_filename}")
