import folium
#from bs4 import BeautifulSoup
import csv
#f = open("C:\Users\hunted\Desktop\code\mapper\Health Inspection Search - Search Results.htm")
addresses = []
with open(r"export.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        full_address = f"{row['ADDRESS']}, {row['CITY']}, {row['STATE']} {row['ZIP']}"
        addresses.append(full_address)
    print(addresses)

# importing geopy library and Nominatim class
from geopy.geocoders import Nominatim
import time

m = folium.Map(location=[45.0, -69.0], zoom_start=7)  # Maine center
loc = Nominatim(user_agent="Geopy Library")
print(len(addresses))
for address in addresses:
    try:
        getLoc = loc.geocode(address)
        if getLoc:
            folium.Marker([getLoc.latitude, getLoc.longitude], popup=address).add_to(m)
        else:
            pass
        time.sleep(1)
        print("marked")
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print("error")
        time.sleep(2)
        continue
print(getLoc.address)

# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)
# m = folium.Map(location=[45.0, -69.0], zoom_start=7)  # Maine center
# folium.Marker([44.5, -68.2], popup="restarant").add_to(m)
# folium.Marker([44.51, -68.21], popup="restarant").add_to(m)
m.save("map.html")
