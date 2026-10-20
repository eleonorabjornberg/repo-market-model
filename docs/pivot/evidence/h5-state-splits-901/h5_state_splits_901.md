# H5 headlines by the as-of scarcity state of the decision day (#901)

Decision days 2018-06-29 to 2025-12-23 (n = 1868); studentized stationary bootstrap, 10000 draws, one-sided 95%, seed 634; panel `4ddc3882…`. Development data, not a verdict.

State: ample is states 0 and 1, scarce is 2 and 3 (ruling on #515), public at the decision instant, each leg at its own latest public row. Decision days by cut: pooled 1868, state:ample 1359, state:scarce 509, state:scarce without_2019-09-18 508, without_2019-09-18 1867.

The pooled column reproduces the tracked figures of #634 and #805 to the digit (checked by the script before it wrote anything).

## Grid CRPS (the primary score)

### a_published_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +20.2% [+12.4%, +41.9%] |
| state:ample | 1359 | +7.1% [-0.3%, +12.7%] |
| state:scarce | 509 | +27.9% [+18.0%, +54.7%] |
| state:scarce without_2019-09-18 | 508 | +19.2% [+12.8%, +28.6%] |
| without_2019-09-18 | 1867 | +14.3% [+9.9%, +20.5%] |

### a_published_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +26.9% [+17.6%, +36.0%] |
| state:ample | 1359 | +31.8% [+20.2%, +43.4%] |
| state:scarce | 509 | +22.6% [+8.9%, +36.7%] |
| state:scarce without_2019-09-18 | 508 | +22.6% [+8.7%, +36.9%] |
| without_2019-09-18 | 1867 | +26.9% [+17.4%, +36.1%] |

### b_gbm_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +20.1% [+12.3%, +41.4%] |
| state:ample | 1359 | +7.2% [+0.4%, +12.3%] |
| state:scarce | 509 | +27.7% [+17.4%, +54.2%] |
| state:scarce without_2019-09-18 | 508 | +18.9% [+11.7%, +29.1%] |
| without_2019-09-18 | 1867 | +14.2% [+9.6%, +21.0%] |

### b_gbm_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +26.8% [+17.5%, +36.0%] |
| state:ample | 1359 | +31.9% [+19.4%, +44.2%] |
| state:scarce | 509 | +22.3% [+8.9%, +35.7%] |
| state:scarce without_2019-09-18 | 508 | +22.3% [+8.5%, +35.9%] |
| without_2019-09-18 | 1867 | +26.8% [+17.1%, +36.0%] |

### c_two_part_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +20.3% [+11.0%, +38.0%] |
| state:ample | 1359 | +3.6% [-9.4%, +14.6%] |
| state:scarce | 509 | +30.2% [+19.4%, +50.3%] |
| state:scarce without_2019-09-18 | 508 | +21.8% [+13.1%, +32.1%] |
| without_2019-09-18 | 1867 | +14.5% [+7.7%, +22.2%] |

### c_two_part_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +27.0% [+18.0%, +36.0%] |
| state:ample | 1359 | +29.2% [+18.7%, +40.7%] |
| state:scarce | 509 | +25.1% [+10.2%, +40.4%] |
| state:scarce without_2019-09-18 | 508 | +25.1% [+10.3%, +40.2%] |
| without_2019-09-18 | 1867 | +27.0% [+17.9%, +35.8%] |

### gbm_funding against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +20.7% [+13.3%, +40.0%] |
| state:ample | 1359 | +9.1% [+2.8%, +14.0%] |
| state:scarce | 509 | +27.6% [+17.5%, +51.8%] |
| state:scarce without_2019-09-18 | 508 | +18.7% [+11.3%, +29.0%] |
| without_2019-09-18 | 1867 | +14.9% [+10.3%, +21.3%] |

### gbm_funding against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +27.4% [+17.4%, +36.6%] |
| state:ample | 1359 | +33.3% [+21.2%, +45.2%] |
| state:scarce | 509 | +22.2% [+7.8%, +36.4%] |
| state:scarce without_2019-09-18 | 508 | +22.1% [+7.2%, +36.5%] |
| without_2019-09-18 | 1867 | +27.3% [+17.2%, +36.7%] |

## Upper-tail twCRPS (weight 1{y > 0 bp})

### a_published_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +32.3% [+23.2%, +54.4%] |
| state:ample | 1359 | +32.4% [+22.6%, +41.5%] |
| state:scarce | 509 | +32.3% [+22.2%, +57.0%] |
| state:scarce without_2019-09-18 | 508 | +22.9% [+14.8%, +33.7%] |
| without_2019-09-18 | 1867 | +23.7% [+16.0%, +32.5%] |

### a_published_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +17.1% [+6.2%, +29.1%] |
| state:ample | 1359 | +37.4% [+1.1%, +70.5%] |
| state:scarce | 509 | +15.0% [+4.2%, +27.5%] |
| state:scarce without_2019-09-18 | 508 | +14.9% [+3.8%, +27.6%] |
| without_2019-09-18 | 1867 | +17.0% [+5.9%, +29.5%] |

### b_gbm_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +31.6% [+22.3%, +52.4%] |
| state:ample | 1359 | +39.8% [+29.0%, +49.8%] |
| state:scarce | 509 | +30.9% [+20.5%, +55.5%] |
| state:scarce without_2019-09-18 | 508 | +21.3% [+13.0%, +32.8%] |
| without_2019-09-18 | 1867 | +22.8% [+14.8%, +32.3%] |

### b_gbm_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +16.2% [+4.9%, +28.5%] |
| state:ample | 1359 | +44.3% [+8.8%, +77.5%] |
| state:scarce | 509 | +13.3% [+2.6%, +25.8%] |
| state:scarce without_2019-09-18 | 508 | +13.2% [+2.1%, +25.9%] |
| without_2019-09-18 | 1867 | +16.1% [+4.4%, +28.9%] |

### c_two_part_new against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +35.7% [+26.3%, +51.6%] |
| state:ample | 1359 | +43.3% [+33.9%, +54.1%] |
| state:scarce | 509 | +35.2% [+24.7%, +53.3%] |
| state:scarce without_2019-09-18 | 508 | +26.2% [+15.6%, +37.6%] |
| without_2019-09-18 | 1867 | +27.6% [+17.5%, +37.4%] |

### c_two_part_new against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +21.3% [+8.5%, +34.0%] |
| state:ample | 1359 | +47.5% [+20.0%, +75.1%] |
| state:scarce | 509 | +18.6% [+5.9%, +32.4%] |
| state:scarce without_2019-09-18 | 508 | +18.6% [+6.1%, +32.3%] |
| without_2019-09-18 | 1867 | +21.3% [+8.1%, +34.1%] |

### gbm_funding against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +31.3% [+22.1%, +50.4%] |
| state:ample | 1359 | +42.6% [+31.2%, +52.4%] |
| state:scarce | 509 | +30.4% [+20.0%, +53.4%] |
| state:scarce without_2019-09-18 | 508 | +20.7% [+11.8%, +32.4%] |
| without_2019-09-18 | 1867 | +22.5% [+13.7%, +32.2%] |

### gbm_funding against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +15.9% [+3.8%, +29.0%] |
| state:ample | 1359 | +46.9% [+10.9%, +79.4%] |
| state:scarce | 509 | +12.7% [+1.2%, +26.0%] |
| state:scarce without_2019-09-18 | 508 | +12.5% [+0.7%, +25.9%] |
| without_2019-09-18 | 1867 | +15.8% [+3.2%, +29.1%] |

## B3 on its own five levels, CRPS (B1 and B2 read at the same five)

### B3 against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +21.8% [+14.4%, +41.0%] |
| state:ample | 1359 | +10.6% [+3.8%, +16.0%] |
| state:scarce | 509 | +28.5% [+18.5%, +53.0%] |
| state:scarce without_2019-09-18 | 508 | +19.8% [+13.0%, +29.4%] |
| without_2019-09-18 | 1867 | +16.1% [+11.6%, +22.1%] |

### B3 against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +27.4% [+17.8%, +36.5%] |
| state:ample | 1359 | +33.2% [+22.2%, +44.2%] |
| state:scarce | 509 | +22.3% [+8.0%, +37.0%] |
| state:scarce without_2019-09-18 | 508 | +22.2% [+7.5%, +37.2%] |
| without_2019-09-18 | 1867 | +27.4% [+17.5%, +36.5%] |

## B3 on its own five levels, twCRPS

### B3 against B1

| cut | days | skill against B1 |
|---|---|---|
| pooled | 1868 | +32.5% [+23.3%, +52.8%] |
| state:ample | 1359 | +33.6% [+24.2%, +43.0%] |
| state:scarce | 509 | +32.4% [+22.2%, +55.4%] |
| state:scarce without_2019-09-18 | 508 | +23.0% [+14.5%, +34.1%] |
| without_2019-09-18 | 1867 | +23.9% [+15.8%, +33.0%] |

### B3 against B2

| cut | days | skill against B2 |
|---|---|---|
| pooled | 1868 | +17.1% [+5.4%, +29.7%] |
| state:ample | 1359 | +42.5% [+8.5%, +72.4%] |
| state:scarce | 509 | +14.3% [+2.8%, +27.5%] |
| state:scarce without_2019-09-18 | 508 | +14.1% [+2.4%, +27.4%] |
| without_2019-09-18 | 1867 | +17.0% [+5.0%, +29.9%] |

