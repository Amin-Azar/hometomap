from gmplot import gmplot
import json
import requests
from operator import itemgetter


def write_to_csv(list_of_list):
    f = open("out.csv", "w")
    for row in list_of_list:
        f.write(",".join(str(r) for r in row))
        f.write("\n")

# node.js source @ https://github.com/Froren/realtorca
#CultureId
    # 1 for EN, (Defaulted to 1.)
    # 2 for FR. 
#ApplicationId - Unused. Defaulted to 1.
#PropertySearchTypeId
    # # 0 No Preference
    # 1 Residential
    # 2 Recreational
    # 3 Condo/Strata
    # 4 Agriculture
    # 5 Parking
    # 6 Vacant Land
    # 8 Multi Family
#PriceMin - Defaults to 0
#PriceMax
#LongitudeMin - Designates the bounds of the query, easiest to find these values from browser requests.
#LongitudeMax
#LatitudeMin
#LatitudeMax
#TransactionTypeId- Defaults to 2?
    #1 For sale or rent
    #2 For sale
    #3 For rent
#StoreyRange - "min-max" i.e. "2-3"
#BedRange - "min-max" if min = max, it searches for the exact value. If it's 1-0, it means it's 1+. Maxes at 5
#BathRange - "min-max"
#Sort
    #  1-A: Low to High ($)	
    #  1-D: High to Low ($)	
    #  6-D: Date Posted: New to Old	
    #  6-A: Date Posted: Old to New	
    # 12-D: Open Houses First	
    # 13-D: More Photos First	
    # 11-D: Virtual Tour First	

#CurrentPage - read somewhere that it maxes at 51
#RecordsPerPage - maxes at 200
#MaximumResults
#OwnershipTypeGroupId
    #0 Any
    #1 Freehold
    #2 Condo/Strata
    #3 Timeshare/Fractional
    #4 Leasehold
#ViewTypeGroupId
    #0 Any
    #1 City
    #2 Mountain
    #3 Ocean
    #4 Lake
    #5 River
    #6 Ravine
    #7 Other
    #8 All Water Views
#BuildingTypeId
    #0 Any
    #1 House
    #2 Duplex
    #3 Triplex
    #5 Residential Commercial Mix
    #6 Mobile Home
    #12 Special Purpose
    #14 Other
    #16 Row/Townhouse
    #17 Apartment
    #19 Fourplex
    #20 Garden Home
    #27 Manufactured Home/Mobile
    #28 Commercial Apartment
    #29 Manufactured Home

#Keywords - search text
#OpenHouse - 0 or 1, must include if filtering by open house
#OpenHouseStartDate - MM/DD/YYYY
#OpenHouseEndDate - MM/DD/YYYY

mandatory_opts = {
    "CultureId": 1, 
    "ApplicationId": 1, 
    "PropertySearchTypeId": 1
    }

# https://www.openstreetmap.org/export#map=11/49.2562/-123.0146
opts = {
  "LongitudeMin": -123.2663,
  "LongitudeMax": -122.8965,
  "LatitudeMin": 49.2037,
  "LatitudeMax": 49.3614,
  "PriceMin": 1000000,
  "PriceMax": 2000000,
  "RecordsPerPage": 200,
  #"CurrentPage": 2
  "BuildingTypeId": 17 # apartment
  
}

opts.update(mandatory_opts)
realtor_api = "https://www.realtor.ca/Residential/Map.aspx#LongitudeMin=-79.6758985519409&LongitudeMax=-79.6079635620117&LatitudeMin=43.57601549736786&LatitudeMax=43.602250137362276&PriceMin=100000&PriceMax=425000"
API_URL = 'https://api2.realtor.ca/Listing.svc/PropertySearch_Post'
response = requests.post(url=API_URL, data=opts)
print(response)
data = json.loads(response.text)

#f = open("out.json","w")
#json.dump(data, indent=4, fp=f)

results=[]
for res in data["Results"]:
    # ---ID-------------------------------------------------------------------------
    list_mls_number = res["MlsNumber"]
    # ---TEXT-----------------------------------------------------------------------
    list_text = res["PublicRemarks"]
    # ---SPECS----------------------------------------------------------------------
    list_bed_cnt = int(res["Building"]["Bedrooms"])
    list_bath_cnt = int(res["Building"]["BathroomTotal"])
    list_apt_Size = float(res["Building"]["SizeInterior"].replace(" sqft",""))
    list_apt_price = float(res["Property"]["Price"].replace("$","").replace(",",""))
    # ---TYPE-----------------------------------------------------------------------
    list_type = res["Building"]["Type"]
    list_ownership = res["Property"]["OwnershipType"]
    # ---ADDRESS--------------------------------------------------------------------
    list_address = res["Property"]["Address"]["AddressText"]
    list_lat = float(res["Property"]["Address"]["Latitude"])
    list_long = float(res["Property"]["Address"]["Longitude"])
    list_PostalCode = res["PostalCode"]
    # ------------------------------------------------------------------------------

    list_price_per_sqft = round(list_apt_price/list_apt_Size)
    
    row = [ list_mls_number, 
            list_price_per_sqft, list_bed_cnt, list_bath_cnt,
            list_type, list_ownership,
            list_address, list_PostalCode, list_lat, list_long,
            list_text[0:-10]
            ]
    results.append(row)

results_sorted = sorted(results, key=itemgetter(1))

write_to_csv(results_sorted)

zoom = 11
# Place map
gmap = gmplot.GoogleMapPlotter(opts["LatitudeMin"], opts["LongitudeMin"], zoom)

# https://github.com/vgm64/gmplot

show_cnt =30 # how many to show after sorting
list_lats =[]
list_lons =[]
for row in results_sorted[0:show_cnt]:
    list_lats.append(row[8])
    list_lons.append(row[9])


gmap.scatter(list_lats, list_lons, '#3B0B39', size=40, marker=False)

## Marker
#hidden_gem_lat, hidden_gem_lon = 49.264028, -123.510347
#gmap.marker(hidden_gem_lat, hidden_gem_lon, 'cornflowerblue')

# Draw
gmap.draw("my_map.html")
    