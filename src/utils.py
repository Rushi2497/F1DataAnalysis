import numpy as np
import pandas as pd
    
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