import numpy as np
import pandas as pd

def get_driver_telemetry_for_laps(session, driver_abbrv, lap_range, tel_type=None):

    if isinstance(lap_range,list):
        lap_range[1] += 1
    else:
        lap_range = [lap_range, lap_range + 1]

    temp_data = session.laps.pick_drivers(driver_abbrv).pick_laps([i for i in range(lap_range[0],lap_range[1])])

    if tel_type == 'car':
        return temp_data.get_car_data()
    elif tel_type == 'pos':
        return temp_data.get_pos_data()
    else:
        return temp_data.get_telemetry()
    
def fuel_correction(session,df,iFuelLoad=108,FC_factor=0.035):
    laps = session.total_laps
    fuel_burn = iFuelLoad/laps      # kg/lap
    fuel_corr = FC_factor           # s/kg

    return round(df['LapTime'] - (laps - df['LapNumber']) * fuel_burn * fuel_corr, 2)

def get_acc_time(df,target_speed):
    
    t1, s1 = df.iloc[df[df.Speed > target_speed].index[0] - 1].Time, df.iloc[df[df.Speed > target_speed].index[0] - 1].Speed
    t2, s2 = df.iloc[df[df.Speed > target_speed].index[0]].Time, df.iloc[df[df.Speed > target_speed].index[0]].Speed

    t_target = t1 + (t2 - t1)*(target_speed - s1)/(s2 - s1)

    acc_time = t_target #- df.iloc[df[df.Distance > 0].index[0] - 1].Time

    return round(acc_time,2)

def get_acc_df(session):
    drivers = session.drivers
    driver_dict = {}
    for driver in drivers:
        df = session.laps.pick_laps(1).pick_drivers(driver).get_car_data()[['Time','Speed']].add_distance()
        df['Time'] = df['Time'].dt.total_seconds()
        try:
            driver_dict[session.get_driver(driver).Abbreviation] = [get_acc_time(df,100),round(get_acc_time(df,200)-get_acc_time(df,100),2)]
        except:
            driver_dict[session.get_driver(driver).Abbreviation] = [np.nan,np.nan]
    
    return pd.DataFrame(driver_dict).T.set_axis(labels=['0-100','100-200'],axis=1)