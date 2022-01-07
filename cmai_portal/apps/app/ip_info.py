import geoip2.database
from apps.app.data import log_file


def get_visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ip_location(ip):
    reader = geoip2.database.Reader('./GeoLite2-City_20190430/GeoLite2-City.mmdb')
    response = reader.city(ip)

    log_file.write("ISO Code:" + response.country.iso_code)
    print(response.country.name)
    print(response.country.names['zh-CN'])
    print(response.subdivisions.most_specific.name)
    print(response.subdivisions.most_specific.iso_code)
    print(response.city.name)
    print(response.postal.code)
    print(response.location.latitude)
    print(response.location.longitude)

    reader.close()
