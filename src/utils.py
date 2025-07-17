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