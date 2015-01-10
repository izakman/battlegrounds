import math

#########################################################################
# return distance (m) for compass quadrant (90 degrees)
# spherical law of cosines formula
# elevation is ignored
# acknowledgement: theory referenced from
# http://www.movable-type.co.uk/scripts/latlong.html
def distanceBetween (latitude1, longitude1, latitude2, longitude2):
    R = 6371
    lat1 = math.radians (latitude1)
    lon1 = math.radians (longitude1)
    lat2 = math.radians (latitude2)
    lon2 = math.radians (longitude2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1) * math.cos(lat2) * \
        math.sin(dLon/2) * math.sin(dLon/2)
          
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c * 1000.0;


def distanceBetweenPoints (point1, point2):
    return distanceBetween (point1[0], point1[1], point2[0], point2[1])


def angleBetweenPoints (point1, point2):
    lat1 = math.radians (point1[0])
    lon1 = math.radians (point1[1])
    lat2 = math.radians (point2[0])
    lon2 = math.radians (point2[1])

    if lat1 == lat2 and lon1 == lon2:
        return None
    
    dLon = lon2 - lon1
    
    y = math.sin (dLon) * math.cos (lat2)
    x = math.cos (lat1) * math.sin (lat2) - \
        math.sin (lat1) * math.cos (lat2) * math.cos (dLon)
        
    angleTmp = math.degrees (math.atan2 (y, x))
    
    return angleTmp if (angleTmp >= 0) else (angleTmp + 360)


def withinField (point1, point2, bearing, fieldRange):
    targetAngle = angleBetweenPoints(point1, point2)
    
    if not targetAngle:
        return False
    
    angleDiff = math.fabs((targetAngle + 180 -  bearing) % 360 - 180)
    
    if angleDiff <= fieldRange:
        return True
    else: return False
    