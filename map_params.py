def get_map_params(toponym, apikey):
    coords = toponym["Point"]["pos"].split()
    lon, lat = coords[0], coords[1]
    envelope = toponym["boundedBy"]["Envelope"]
    lower = envelope["lowerCorner"].split()
    upper = envelope["upperCorner"].split()
    spn_lon = abs(float(upper[0]) - float(lower[0]))
    spn_lat = abs(float(upper[1]) - float(lower[1]))
    return {
        "ll": f"{lon},{lat}",
        "spn": f"{spn_lon},{spn_lat}",
        "apikey": apikey,
    }


def get_map_params_two_points(point1, point2, apikey):
    lon1, lat1 = point1
    lon2, lat2 = point2
    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2
    spn_lon = abs(lon1 - lon2) + 0.01
    spn_lat = abs(lat1 - lat2) + 0.01
    return {
        "ll": f"{center_lon},{center_lat}",
        "spn": f"{spn_lon},{spn_lat}",
        "apikey": apikey,
    }
