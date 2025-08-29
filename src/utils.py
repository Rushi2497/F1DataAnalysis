import numpy as np
import pandas as pd
import statsmodels.api as sm
import fastf1.plotting as plotting
    

def fuel_correction(session,df,iFuelLoad=108,FC_factor=0.035):

    """
    Apply a simple linear fuel correction to lap times for a given stint.

    Parameters
    ----------
    session : fastf1.core.Session
        The loaded FastF1 session object. Used to determine the total number of laps.
    df : pandas.DataFrame
        DataFrame containing at least 'LapNumber' and 'LapTime' columns.
        - 'LapTime' must already be converted to seconds.
        - The DataFrame should represent a single stint.
    iFuelLoad : float, optional, default=108
        Initial fuel load in kilograms.
    FC_factor : float, optional, default=0.035
        Fuel correction factor in seconds per kilogram.

    Returns
    -------
    pandas.Series
        Series of fuel-corrected lap times (in seconds), rounded to 2 decimals.
    """

    laps = session.total_laps
    fuel_burn = iFuelLoad/laps      # kg/lap
    fuel_corr = FC_factor           # s/kg

    return round(df['LapTime'] - (laps - df['LapNumber']) * fuel_burn * fuel_corr, 2)


def get_acc_time(df,target_speed):
    
    """
    Estimate the timestamp at which a car reaches a given target speed.

    This function interpolates linearly between the two telemetry points
    surrounding the target speed to estimate the exact time.

    Parameters
    ----------
    df : pandas.DataFrame
        Telemetry DataFrame containing 'Time' and 'Speed' columns.
        - 'Time' must already be converted to seconds.
    target_speed : float
        Target speed in km/h at which to estimate the time.

    Returns
    -------
    float
        Estimated time (in seconds) at which the car reaches the target speed,
        rounded to 2 decimals.
    """

    t1, s1 = df.iloc[df[df.Speed > target_speed].index[0] - 1].Time, df.iloc[df[df.Speed > target_speed].index[0] - 1].Speed
    t2, s2 = df.iloc[df[df.Speed > target_speed].index[0]].Time, df.iloc[df[df.Speed > target_speed].index[0]].Speed

    t_target = t1 + (t2 - t1)*(target_speed - s1)/(s2 - s1)

    acc_time = t_target    #- df.iloc[df[df.Distance > 0].index[0] - 1].Time, use if you want to exclude reaction time

    return round(acc_time,2)


def get_acc_df(session):

    """
    Compute acceleration performance metrics (0–100 km/h and 100–200 km/h) for all drivers in a session.

    For each driver:
    - Extracts telemetry (time and speed) from lap 1.
    - Computes the time to 100 km/h.
    - Computes the time difference between 100 and 200 km/h.
    - Returns NaN if data is unavailable or incomplete.

    Parameters
    ----------
    session : fastf1.core.Session
        The loaded FastF1 session object.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by driver abbreviations with two columns:
        - '0-100' : time in seconds to reach 100 km/h
        - '100-200' : time in seconds from 100 to 200 km/h
    """

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


def get_driver_stint_models(session, drivers, iFuelLoad=108, FC_factor=0.035):
    """
    Extract stint-wise OLS models for given drivers in a session.
    
    Parameters
    ----------
    session : fastf1.core.Session
        Already loaded FastF1 session object.
    drivers : list
        List of driver abbreviations (e.g., ["NOR", "VER"]).
    iFuelLoad : float, optional, default=108
        Initial fuel load in kilograms.
    FC_factor : float, optional, default=0.035
        Fuel correction factor in seconds per kilogram.
    
    Returns
    -------
    dict
        {driver_abbr: [(compound, model_object), ...]}
    """
    results = {}

    for drv_abbr in drivers:
        laps = session.laps.pick_drivers(drv_abbr)[[
            'LapNumber', 'LapTime', 'Stint', 'Compound', 'TyreLife',
            'TrackStatus', 'PitInTime', 'PitOutTime'
        ]].pick_quicklaps()

        # Drop laps under yellow/red flags
        laps = laps[~(laps.TrackStatus.str.contains('4'))]

        stint_models = []

        for stint_num, stint_df in laps.groupby('Stint'):
            if len(stint_df) < 10:
                continue

            # Exclude in/out laps
            stint_df = stint_df[(stint_df.PitInTime.isnull()) & (stint_df.PitOutTime.isnull())].copy()
            if stint_df.empty:
                continue

            # Convert to seconds
            stint_df['LapTime'] = stint_df.LapTime.dt.total_seconds()

            # Apply fuel correction
            corrected_times = fuel_correction(session, stint_df, iFuelLoad=iFuelLoad, FC_factor=FC_factor)

            x = sm.add_constant(stint_df['TyreLife'])
            y = corrected_times

            try:
                model = sm.OLS(y, x).fit()
                compound = stint_df['Compound'].iloc[0]
                stint_models.append((compound, model))
            except Exception as e:
                print(f"Error for {drv_abbr} stint {stint_num}: {e}")

        if stint_models:
            results[drv_abbr] = stint_models

    return results


def compare_car_speeds(session, drivers, corner_inputs, delta=10):
    """
    Compare car performance in terms of Top Speed, High-Speed Corner Avg,
    and Low-Speed Corner Avg using FastF1 telemetry data.

    Parameters
    ----------
    session : fastf1.core.Session
        A FastF1 session object (already loaded).
    drivers : list[str]
        List of driver abbreviations, e.g., ["VER", "HAM", "NOR"].
    corner_inputs : dict
        Dictionary specifying corner categories:
        {
            "high": [list of high-speed corner numbers],
            "low": [list of low-speed corner numbers],
            "medium": [list of medium-speed corners]),
            "optional": any additional category list
        }
    delta : float, optional
        Distance window (in meters) around each corner marker to average
        speeds. Default = 10m.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by driver abbreviations with columns:
        ["TopSpeed", "HighSpeedAvg", "LowSpeedAvg", MediumSpeedAvg]
    """
    corner_df = session.get_circuit_info().corners
    results = {}

    for drv in drivers:
        tel = session.laps.pick_drivers(drv).pick_fastest().get_telemetry()
        metrics = {}

        # --- Top Speed (track max) ---
        metrics["TopSpeed"] = tel.Speed.max()

        # --- Loop through corner categories (high/low/medium etc.) ---
        for category, corners in corner_inputs.items():
            speeds = []
            for c in corners:
                d = corner_df.iloc[c-1].Distance
                mask = (tel.Distance > d - delta) & (tel.Distance < d + delta)
                speeds.extend(tel[mask].Speed.tolist())
            # store category average
            if speeds:
                metrics[f"{category.capitalize()}SpeedAvg"] = sum(speeds) / len(speeds)
            else:
                metrics[f"{category.capitalize()}SpeedAvg"] = None

        results[drv] = metrics

    return round(pd.DataFrame(results).T)


def compute_track_dominance_multi(session, drivers, circuit_length, window_size=200, rotation=None, colors_map=None):
    """
    Compute track dominance visualization data among multiple drivers.

    Parameters
    ----------
    session : fastf1.core.Session
        Loaded FastF1 session object.
    drivers : list[str]
        List of driver identifiers (e.g. ['VER', 'NOR', 'HAM']).
    circuit_length : int or float
        Circuit length in meters.
    window_size : int, optional
        Window size for smoothing the speed values (default=100).
    rotation : float, optional
        Track rotation in degrees. If None, uses session.get_circuit_info().rotation.
    colors_map : dict[str, str], optional
        Mapping from driver identifier -> color hex string.
        If None, colors will be fetched using FastF1 plotting.get_driver_color.

    Returns
    -------
    points : np.ndarray
        Array of (x, y) coordinates reshaped for LineCollection plotting.
    segments : np.ndarray
        Array of line segments for LineCollection.
    colors : np.ndarray
        Array of colors corresponding to which driver is fastest at each point.
    """
    # Distance grid
    distance_grid = np.linspace(0, circuit_length, num=int(circuit_length)+1)

    # If no colors_map provided, build it
    if colors_map is None:
        colors_map = {drv: plotting.get_driver_color(session=session, identifier=drv)
                      for drv in drivers}

    # Store data for all drivers
    xs, ys, speeds = [], [], []

    for drv in drivers:
        df = session.laps.pick_drivers(drv).pick_fastest().telemetry[['Distance','X','Y','Speed']].copy()

        # Interpolation
        x = np.interp(distance_grid, df['Distance'], df['X'])
        y = np.interp(distance_grid, df['Distance'], df['Y'])
        speed = np.interp(distance_grid, df['Distance'], df['Speed'])

        # Smooth speed
        speed = pd.Series(speed).rolling(window=window_size, center=True, min_periods=1).mean().to_numpy()

        xs.append(x)
        ys.append(y)
        speeds.append(speed)

    # Convert to arrays
    xs = np.array(xs)   # shape: (n_drivers, n_points)
    ys = np.array(ys)
    speeds = np.array(speeds)

    # Who’s fastest at each point?
    fastest_idx = np.argmax(speeds, axis=0)
    fastest_drivers = [drivers[i] for i in fastest_idx]
    colors = np.array([colors_map[d] for d in fastest_drivers])

    # Use average X,Y of all drivers for track midline
    x = xs.mean(axis=0)
    y = ys.mean(axis=0)

    # Rotation
    if rotation is None:
        rotation = session.get_circuit_info().rotation
    theta = np.deg2rad(rotation)
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)

    # Segments
    points = np.array([x_rot, y_rot]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    return points, segments, colors