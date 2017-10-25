# Format of the GeoJSON

The expansion of the GeoJSON with multidimensional data should be in the `propertys` field with the `OBSERVATIONS` field:

```json
{
    // ...
    "properties": {
        "NUTS_ID": "AT124",
        "STAT_LEVL_": 3,
        "SHAPE_AREA": 0.582627509491,
        "SHAPE_LEN": 3.03923142882,
        "OBSERVATIONS": [
            {
                "soil": [
                    {
                        "period": "2001-01-01",
                        "unit": "T_HA",
                        "value": 123
                    }
                ]
            }
        ]
    },
// ...
}
```