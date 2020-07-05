# pyg2 <img src="./docs/_media/whale.128.png" align="right" width="128" />

## 概览

[G2Plot](https://g2plot.antv.vision/) 是开箱即用、易于配置、具有良好视觉和交互体验的通用统计图表库, pyg2由此而来。

* API 设计简洁, 默认好看
* 响应式图表 保证图表在任何显示尺寸、任何数据状态下的可读性
* 使用 pandas DataFrame 作为作图的数据源格式
* 支持20+以上的图表类型
* 支持**迷你图表**
* 支持 Jupyter Notebook(IPython Notebook)

![logo](./docs/_media/cover.png)

## 安装

see https://github.com/13kay/pyg2/releases/tag/0.1

## 1 分钟上手

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
