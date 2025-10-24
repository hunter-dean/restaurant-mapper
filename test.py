import folium
import branca
import csv
import sys

INPUT_CSV_FILE = "portland_restaurants.csv"
OUTPUT_MAP_FILE = "portland_map.html"
PORTLAND_COORDINATES = [43.6615, -70.2553]

#  center on Portland
m = folium.Map(location=PORTLAND_COORDINATES, zoom_start=13)


colormap = branca.colormap.LinearColormap(colors=['#00ff00', '#ff0000'])
#colormap = colormap.to_step(n=6)
colormap.caption = "Restaurant Health Score (Lower is Better)"
colormap.add_to(m)


try:
    with open(INPUT_CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                name = row['ESTABLISHMENT_NAME']
                score = float(row['CALCULATED'])
                address = row['ADDRESS']

                popup_text = f"<b>{name}</b><br>Score: {score}<br>{address}"

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    popup=popup_text,
                    color=colormap(score),
                    fill=True,
                    fill_color=colormap(score)
                ).add_to(m)

            except (ValueError, KeyError):
                #
                continue

except FileNotFoundError:
    print(f"Error: Could not find the file '{INPUT_CSV_FILE}'.")
    print("Please run the first script to create it.")
    sys.exit()


m.save(OUTPUT_MAP_FILE)

print(f"Map has been created")
