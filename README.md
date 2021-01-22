[UNMAINTAINED] please check https://github.com/hustcc/PyG2Plot for instead. Or you are [rg2](https://github.com/13kay/rg2) for R library.

# pyg2

## Overview

rg2 is a wrapper of [G2Plot](https://g2plot.antv.vision/) for R.

![logo](./docs/_media/cover.png)

## Installation

see https://github.com/13kay/pyg2/releases/tag/0.1

## Installation

``` python
import pandas as pd
from pyg2 import bar

df = pd.DataFrame.from_records([
  { 'action': '浏览', 'pv': 50000 },
  { 'action': '加购', 'pv': 35000 },
  { 'action': '下单', 'pv': 25000 },
  { 'action': '支付', 'pv': 15000 },
  { 'action': '成交', 'pv': 8500 },
])
cfg = {
    'width':600,
    'conversionTag': {'visible': True}
}
bar(df,'pv','action',cfg=cfg).title(title='店铺转化率',description='浏览->加购->下单->支付->成交').render()
```

<img src="./docs/_media/quickstart.png" width="639" />
