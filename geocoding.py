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
        #history log
        self.history_log = ""

def geocode_address(full_address):
    geolocator = Nominatim(user_agent="ME_restaurant_geocoder") # changes UID to be "unique"
    try:
        time.sleep(1) #for nonatim gods
        location = geolocator.geocode(full_address, timeout=10)
        #i used the wrong variable above and that threw me for a loop for some time. good now. ;
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        #time.sleep(1) #this time.sleep was in the wrong place :(
        return None, None
        return None, None
        #retrn none twice? dont care
input_filename = "export.csv"
output_filename = "restaurants1.csv"

#counting for progress bar and stuff
total_rows = 0
try:
    with open(input_filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            #if row["CITY"].strip().lower() == "portland":
            total_rows += 1

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
    sys.exit()

print(f"{total_rows} records. cleaner & geocofer go!")
print(f"to {output_filename}")

if total_rows == 0:
    print("No restaurants found in the input file.")
    sys.exit()

#print(f"Found {total_restaurants} total restaurants. Geocoding...")
#above depreciated.

master_restaurants = {}
coord_cache = {}
#as to avoid 'straining' nonatim / geocoding <3
processed_count = 0

with open(input_filename, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #if row["CITY"].strip().lower() == "portland":
            if processed_count > 1000:                                     # <-------- DELETE THIS!!!!!!!!!!!!!!!
                break                                                      # <-------- DELETE THIS!!!!!!!!!!!!!!!
            processed_count += 1
            percentage = (processed_count / total_rows) * 100
            print(f"Progress: {processed_count}/{total_rows} ({percentage:.2f}%)", end='\r')


            eid = row["EST ID #"]
            full_addr = f"{row['ADDRESS']}, {row['CITY']}, {row['STATE']} {row['ZIP']}"

            #for specific inspection
            # this_insp = f"Date{row["INSP_DATE"]}, Score:{row["CALCULATED"]}", Failed:{row["FAILED"]}" | '
            #dawg i aint gonna lie its past 4am and i have no damn clue why the above line didnt work im too tired to figure it out; i need sleep boss. cant really be mad at anyone but myself for saving all this work to the last damn minute to do as i always do. still got a bunch to do. fuck me
            #this comment kept for "authenticity" ( ? )
            this_insp = f"Date:{row['INSP_DATE']}, Score:{row['CALCULATED']}, Failed:{row['FAILED']} | "
            #this.. works (i hope)
            if eid in master_restaurants:
                #alredy exists
                master_restaurants[eid].history_log += this_insp


                #if new
                if row["INSP_DATE"] > master_restaurants[eid].insp_date:
                    # 
                    master_restaurants[eid].insp_date = row["INSP_DATE"]
                    master_restaurants[eid].c_out = row["C_OUT"]
                    master_restaurants[eid].nc_out = row["NC_OUT"]
                    master_restaurants[eid].failed = row["FAILED"]
                    master_restaurants[eid].calculated = row["CALCULATED"]
            else:
            #new restaurant


                r = Restaurant(
                    est_id=eid, establishment_name=row["ESTABLISHMENT_NAME"],
                    c_out=row["C_OUT"], nc_out=row["NC_OUT"], insp_date=row["INSP_DATE"],
                    lic_exp=row["LIC_EXP"], lic_type=row["LIC_TYPE"], failed=row["FAILED"],
                    address=row["ADDRESS"], city=row["CITY"], state=row["STATE"],
                    zip_code=row["ZIP"], telephone=row["TELEPHONE"],
                    inspection_type_code=row["INSPECTION_TYPE_CODE"], owner_name=row["OWNER_NAME"],
                    county=row["COUNTY"], calculated=row["CALCULATED"]
                )
                r.history_log = this_insp


                #checl cache
                if full_addr in coord_cache:
                    r.latitude, r.longitude = coord_cache[full_addr]
                else:
                    lat, lon = geocode_address(full_addr)
                    coord_cache[full_addr] = (lat, lon) #-> cache
                    r.latitude = lat
                    r.longitude = lon

                master_restaurants[eid] = r
print(f"\nsaving to csv {output_filename}   ")
    
output_headers = [
        "EST ID #", "ESTABLISHMENT_NAME", "C_OUT", "NC_OUT", "INSP_DATE",
        "LIC_EXP", "LIC_TYPE", "FAILED", "ADDRESS", "CITY", "STATE", "ZIP",
        "TELEPHONE", "INSPECTION_TYPE_CODE", "OWNER_NAME", "COUNTY", "CALCULATED",
        "latitude", "longitude", "HISTORY_LOG"
]

with open(output_filename, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_headers, extrasaction='ignore')
    writer.writeheader()
    for eid in master_restaurants:
        r = master_restaurants[eid]

        if r.latitude:
            writer.writerow({
                "EST ID #": r.est_id, "ESTABLISHMENT_NAME": r.establishment_name,
                "C_OUT": r.c_out, "NC_OUT": r.nc_out, "INSP_DATE": r.insp_date,
                "LIC_EXP": r.lic_exp, "LIC_TYPE": r.lic_type, "FAILED": r.failed,
                "ADDRESS": r.address, "CITY": r.city, "STATE": r.state,
                "ZIP": r.zip_code, "TELEPHONE": r.telephone,
                "INSPECTION_TYPE_CODE": r.inspection_type_code,
                "OWNER_NAME": r.owner_name, "COUNTY": r.county,
                "CALCULATED": r.calculated, "latitude": r.latitude, "longitude": r.longitude,
                "HISTORY_LOG": r.history_log #also screwed this line up somehow earlier but good now :)
            })

            #couldent tell you wy i ever had geocoder calls here.
            # full_address = f"{r.address}, {r.city}, {r.state} {r.zip_code}"
            # lat, lon = geocode_address(full_address)

            # if lat and lon:
            #     r.latitude = lat
            #     r.longitude = lon
            #     restaurants.append(r)

print("\n")

#more scary zombie people coding


# output_headers = [
#     "EST ID #", "ESTABLISHMENT_NAME", "C_OUT", "NC_OUT", "INSP_DATE",
#     "LIC_EXP", "LIC_TYPE", "FAILED", "ADDRESS", "CITY", "STATE", "ZIP",
#     "TELEPHONE", "INSPECTION_TYPE_CODE", "OWNER_NAME", "COUNTY", "CALCULATED",
#     "latitude", "longitude"
# ]

print(f"done. {output_filename} created.")


#scary zombie code: do not interact


# with open(output_filename, "w", newline="", encoding="utf-8") as outfile:
#     writer = csv.DictWriter(outfile, fieldnames=output_headers, extrasaction='ignore')
#     writer.writeheader()
#     for r in restaurants:
#         restaurant_data = {
#             "EST ID #": r.est_id, "ESTABLISHMENT_NAME": r.establishment_name,
#             "C_OUT": r.c_out, "NC_OUT": r.nc_out, "INSP_DATE": r.insp_date,
#             "LIC_EXP": r.lic_exp, "LIC_TYPE": r.lic_type, "FAILED": r.failed,
#             "ADDRESS": r.address, "CITY": r.city, "STATE": r.state,
#             "ZIP": r.zip_code, "TELEPHONE": r.telephone,
#             "INSPECTION_TYPE_CODE": r.inspection_type_code,
#             "OWNER_NAME": r.owner_name, "COUNTY": r.county,
#             "CALCULATED": r.calculated, "latitude": r.latitude, "longitude": r.longitude
#         }
#         writer.writerow(restaurant_data)

# print(f"Finished. Geocoded {len(restaurants)} restaurants.")
# print(f"Data has been written to {output_filename}")
