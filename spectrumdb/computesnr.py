
enbw_dbHz = 53.8
desens_db = 13.2
# This table is incomplete.
refLevel = [-30, 5]
noiseFloor=[-168.3, -153.5]

DEFAULT_REFLVL = 5



def get_noise_floor_from_ref_level(ref):
    """
    Use linear interpolation (?) to get noise floor from ref level based on a
    table lookup.
    """
    for i in range (0,len(refLevel)-1):
        if ref == refLevel[i] :
            return noiseFloor[i]
        elif ref == refLevel[i+1] :
            return noiseFloor[i+1]
        else:
            slope = (noiseFloor[i+1] - noiseFloor[i])/(refLevel[i+1] -
                    refLevel[i])
            return (ref - refLevel[i])* slope + noiseFloor[i]
    raise Exception("cannot map refLevel to noise floor")


def get_peak_power_in_dbm_per_hz(peakPower):
    """
    Get the peak poer in db per Hz from the given peak power.
    """
    return peakPower - enbw_dbHz -desens_db


def compute_snr(peak_power,ref_level = 5) :
    """
    Compute the SNR given the peak power and the ref level.
    Default ref level is 5
    """
    noiseFloor = get_noise_floor_from_ref_level(ref_level)
    peakPowerDbmPerHz = get_peak_power_in_dbm_per_hz(peak_power)
    return peakPower - noiseFloor



def compute_snr_for_radar(metadata,radar_metadata) :
    refLvl = DEFAULT_REFLVL
    if "refLvl" in metadata:
        refLvl = metadata["refLvl"]

    peakPower = radar_metadata["peakPowerDbm"]
    return compute_snr(peakPower,refLvl)
