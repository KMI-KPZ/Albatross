import geopandas as gpd
import json

raw = gpd.GeoDataFrame.from_file("../../data/geojson/eurostats/nuts_3/aei_pr_soiler.geojson")
# for index, k in enumerate(raw.loc[:, 'NUTS_ID']):
#     print("{:04}: {}".format(index, k))
# for k in raw.loc[0, :]['OBSERVATIONS']:
#     print(k)
#     for l in raw.loc[0, :]['OBSERVATIONS'][k]:
#         print("\t{}: {} {}".format(l['period'], l['value'], l['unit']))

print("----------------")
to_find = 'AT130'
print(raw.loc[:, 'NUTS_ID'][raw.loc[:, 'NUTS_ID'] == to_find].index[0])