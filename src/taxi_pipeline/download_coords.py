import pandas as pd
import io

# Розширений список координат для всіх округів NYC
csv_content = """LocationID,Borough,Zone,lat,long
1,EWR,Newark Airport,40.6895,-74.1745
132,Queens,JFK Airport,40.6413,-73.7781
138,Queens,LaGuardia Airport,40.7769,-73.8740
161,Manhattan,Midtown Center,40.7551,-73.9813
162,Manhattan,Midtown East,40.7577,-73.9723
163,Manhattan,Midtown North,40.7618,-73.9785
164,Manhattan,Midtown South,40.7484,-73.9856
236,Manhattan,Upper East Side North,40.7756,-73.9575
237,Manhattan,Upper East Side South,40.7703,-73.9635
238,Manhattan,Upper West Side North,40.7954,-73.9715
239,Manhattan,Upper West Side South,40.7847,-73.9792
7,Queens,Astoria,40.7684,-73.9298
129,Queens,Jackson Heights,40.7557,-73.8831
25,Brooklyn,Bushwick North,40.7024,-73.9238
26,Brooklyn,Bushwick South,40.6943,-73.9235
33,Brooklyn,Brooklyn Heights,40.6974,-73.9933
61,Brooklyn,Crown Heights North,40.6720,-73.9311
181,Brooklyn,Park Slope,40.6675,-73.9806
51,Bronx,Co-op City,40.8742,-73.8239
182,Bronx,Parkchester,40.8379,-73.8614
259,Bronx,Woodlawn/Wakefield,40.8980,-73.8550
147,Staten Island,Mariners Harbor,40.6339,-74.1611
214,Staten Island,South Beach/Dongan Hills,40.5841,-74.0903
5,Staten Island,Arden Heights,40.5526,-74.1884
44,Staten Island,Charleston,40.5300,-74.2322
84,Staten Island,Eltingville,40.5400,-74.1600
110,Staten Island,Great Kills,40.5500,-74.1500
221,Staten Island,Stapleton,40.6300,-74.0800
245,Staten Island,West Brighton,40.6300,-74.1100
"""

def create_local_coords():
    print("🛠️ Оновлення локального файлу координат для всіх округів...")
    df = pd.read_csv(io.StringIO(csv_content))
    save_path = "src/taxi_pipeline/taxi_zones_with_coords.csv"
    df.to_csv(save_path, index=False)
    print(f"✅ Готово! Тепер Бруклін, Бронкс та Стейтен-Айленд мають точки на карті.")

if __name__ == "__main__":
    create_local_coords()