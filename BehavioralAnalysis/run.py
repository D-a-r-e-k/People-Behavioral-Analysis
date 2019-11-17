import requests
import pandas as pd
import json

def execute(bluetooh_radar_data, df_all):

    df_all['time'] = pd.to_datetime(df_all['time'])
    df_all['time'] = df_all['time'].apply(lambda x: x.tz_convert('Europe/Helsinki'))

    df = df_all.copy()
    df['hour_time'] = df['time'].apply(lambda x: x.hour)
    df = df.reset_index(drop=True)

    transportation_areas = bluetooh_radar_data[bluetooh_radar_data['is_transportation_node'] == True]
    recreational_areas = bluetooh_radar_data[bluetooh_radar_data['is_recreation_zone'] == True]

    def filter_long_away_trafic(df_by_location):
        mean_distance = df_by_location.distance.mean()
        std_distance = df_by_location.distance.std()
        return df_by_location[df_by_location['distance'] < mean_distance + std_distance]

    def get_dataframes_with_been_in_transport_area(df):
        return df.groupby('hash').filter(lambda x: len(set(x.serial) & set(transportation_areas.serial)) != 0)

    def get_dataframes_with_been_in_recreational_area(df):
        return df.groupby('hash').filter(lambda x: len(set(x.serial) & set(recreational_areas.serial)) != 0)

    def get_tourists(df):
        max_location_threash = 4
        people_who_been_in_port = get_dataframes_with_been_in_transport_area(df)
        people_who_visited_recreational_zones = get_dataframes_with_been_in_recreational_area(people_who_been_in_port)
        port_traveling = people_who_visited_recreational_zones.groupby('hash').filter(
            lambda x: len(x.serial.unique()) >= max_location_threash)
        return port_traveling

    df = df.reset_index(drop=True)
    tourists = get_tourists(df)
    users_spent_at_place = df.groupby(['hash', 'serial']).apply(lambda x: len(x))

    hash_match = users_spent_at_place[users_spent_at_place > 3600 * 4].index.get_level_values('hash').values
    serial_match = users_spent_at_place[users_spent_at_place > 3600 * 4].index.get_level_values('serial').values
    hash_serial_dict = {h: [] for h in hash_match}

    for h, s in zip(hash_match, serial_match):
        hash_serial_dict[h].append(s)

    users_work_place = pd.DataFrame(
        {'hash': list(hash_serial_dict.keys()), 'work_place': list(hash_serial_dict.values())}).set_index('hash',
                                                                                                          drop=False)
    early_birds = [5, 8]
    late_owels = [9, 10]
    evening_times = [22, 2]

    is_late_owel = df.groupby('hash').hour_time.apply(lambda x: late_owels[0] <= x.iloc[0] <= late_owels[1])
    is_early_bird = df.groupby('hash').hour_time.apply(lambda x: early_birds[0] <= x.iloc[0] <= early_birds[1])
    is_spending_evenings = df.groupby('hash').hour_time.apply(lambda x: evening_times[0] >= x.iloc[-1] and x.iloc[0] <= evening_times[1])

    export_csv = pd.concat([pd.DataFrame({'hash': df['hash'].unique()}).set_index('hash', drop=False),
                            pd.DataFrame(is_late_owel.rename('is_late_owl')),
                            pd.DataFrame(is_early_bird.rename('is_early_bird')),
                            pd.DataFrame(is_spending_evenings.rename('is_spending_evenings'))], axis=1)

    export_csv['is_tourist'] = export_csv.index.isin(tourists['hash'].unique())
    export_csv = pd.concat([export_csv, pd.DataFrame(users_work_place.work_place)], axis=1)
    export_csv['work_place'] = export_csv['work_place'].fillna('[]')
    return export_csv.reset_index(drop=True)
