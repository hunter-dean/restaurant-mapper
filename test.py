import folium
import branca
import csv
import sys
#change input file to restaurants1.csv for updated list
INPUT_CSV_FILE = "restaurants.csv"
OUTPUT_MAP_FILE = "map.html"
PORTLAND_COORDINATES = [43.6615, -70.2553]

#  center on Portland
m = folium.Map(location=PORTLAND_COORDINATES, zoom_start=13)


colormap = branca.colormap.LinearColormap(colors=['#00ff00', '#ff0000'], index=[0.0, 0.3])
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
                critical = int(row['C_OUT'])
                noncritical = int(row['NC_OUT'])
                history = row.get('HISTORY_LOG', 'No history')

                # Moved this block UP so 'failed' is defined before use
                if row['FAILED'] == 'Yes':
                    failed = True
                elif row['FAILED'] == 'No':
                    failed = False
                else:
                    failed = "error?"

                # fun graph logic
                history_steps = history.split(' | ')
                graph_html = "<div style='width:200px; border-top:1px solid #ccc; margin-top:10px; padding-top:10px;'><b>History:</b><br>"
                
                for step in history_steps:
                    if "Score:" in step:
                        try:
                            h_score = float(step.split("Score:")[1].split(",")[0])
                            bar_width = min(int(h_score * 300), 100)
                            graph_html += f"<div style='font-size:10px;'>{step.strip()}</div>"
                            graph_html += f"<div style='background:{colormap(h_score)}; width:{bar_width}%; height:5px; margin-bottom:5px;'></div>"
                        except:
                            continue
                
                # goes OUTSIDE the for loop
                graph_html += "</div>" 
                
                # add popyp
                popup_text = f"""
                <h1>{name}</h1><br>{address}<br>
                Critical Violations: {critical}<br>
                Non-Critical Violations: {noncritical}<br>
                calculated score: {score}<br>
                <h2>Failed?: {failed}</h2>
                {graph_html}
                """
                #end graph logic

                #adding skelebones
                if failed == True:
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_text,
                        icon=folium.Icon(
                            color='black',           
                            icon_color='white',     
                            icon='skull-crossbones', 
                            prefix='fa'              
                        )
                    ).add_to(m)
                else:   
                    folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
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
