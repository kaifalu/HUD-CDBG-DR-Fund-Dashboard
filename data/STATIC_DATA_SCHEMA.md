# Compact financial data schema

Each record is an array of 25 fields, encoded in `data/rows/rows_*.js`. Missing category/geographic codes use -1. Bootstrap dictionaries translate codes into labels.

| Index | Field |
|---|---|
| 0 | year |
| 1 | disasterType |
| 2 | grantee |
| 3 | project |
| 4 | organization |
| 5 | activityType |
| 6 | activityTitle |
| 7 | quarter |
| 8 | grantCode |
| 9 | activityCode |
| 10 | state |
| 11 | county |
| 12 | city |
| 13 | urban |
| 14 | countyMethod |
| 15 | countyConfidence |
| 16 | cityMethod |
| 17 | cityConfidence |
| 18 | urbanMethod |
| 19 | urbanConfidence |
| 20 | Funds obligated (USD, net) |
| 21 | Funds expended (USD, net) |
| 22 | Grant disbursed (USD, net) |
| 23 | Program income disbursed (USD, net) |
| 24 | Program income received (USD, net) |

All indices in `geographyLevels` match this schema. Geographic polygon assets load only when needed. The standalone HTML embeds the same files without external data requests.
