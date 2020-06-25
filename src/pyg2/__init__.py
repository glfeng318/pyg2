import os
import sys
import re
import json
import time
import math
import uuid
import enum
import functools
import inspect
import itertools
import numpy as np
from jinja2 import Environment, PackageLoader
from IPython.display import display, Javascript, HTML



def exception_handler(exception_type, exception, traceback):
    print("%s: %s" % (exception_type.__name__, exception), file=sys.stderr)

if 'ipykernel' in sys.modules:
    ipython = get_ipython()
    ipython._showtraceback = exception_handler


def df2treemap_json(df):
    '''
    convert pandas.core.frame.DataFrame to json for treemap
    the N-1 column are group-column, the last column is value column.
    '''
    entries = []
    # Stopping case
    if df.shape[1] == 2:  # only 2 columns left
        for i in range(df.shape[0]):  # iterating on rows
            entries.append({"name": df.iloc[i, 0], "value": df.iloc[i, 1]})
    # Iterating case
    else:
        values = set(df.iloc[:, 0])  # Getting the set of unique values
        for v in values:
            df_next = df.loc[df.iloc[:, 0] == v].iloc[:, 1:]
            entries.append(
                {"name": v,
                 "color": v,
                 "value": sum(df_next.iloc[:,-1]),
                 # reiterating the process but without the first column
                 # and only the rows with the current value
                 "children": df2treemap_json(df_next)
                }
            )
    return entries

    
class npEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        
        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}
        
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
    
        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return json.JSONEncoder.default(self, obj)
        

class G2(object):
    @enum.unique
    class ChartType(enum.Enum):
        line = 'Line'
        step_line = 'StepLine'
        treemap = 'Treemap'
        bar = 'Bar'
        stacked_bar = 'StackedBar'
        grouped_bar = 'GroupedBar'
        percent_stacked_bar = 'PercentStackedBar'
        range_bar = 'RangeBar'
        area = 'Area'
        stacked_area = 'StackedArea'
        percent_stacked_area = 'PercentStackedArea'
        column = 'Column'
        column_label = 'ColumnLabel'
        grouped_column = 'GroupedColumn'
        stacked_column = 'StackedColumn'
        stacked_column_label = 'StackedColumnLabel'
        range_column = 'RangeColumn'
        percent_stacked_column = 'PercentStackedColumn'
        pie = 'Pie'
        density_heatmap = 'DensityHeatmap'
        heatmap = 'Heatmap'
        word_cloud = 'WordCloud'
        rose = 'Rose'
        funnel = 'Funnel'
        stacked_rose = 'StackedRose'
        grouped_rose = 'GroupedRose'
        radar = 'Radar'
        liquid = 'Liquid'
        histogram = 'Histogram'
        density = 'Density'
        donut = 'Donut'
        waterfall = 'Waterfall'
        scatter = 'Scatter'
        bubble = 'Bubble'
        bullet = 'Bullet'
        calendar = 'Calendar'
        gauge = 'Gauge'
        fan_gauge = 'FanGauge'
        meter_gauge = 'MeterGauge'
    
    def __init__(self, cfg):
        self.env = Environment(loader=PackageLoader('pyg2', 'g2'))
        self.template = env.get_template('g2.ipy.html') if 'ipykernel' in sys.modules else env.get_template('g2.html')
        
        self.cid = uuid.uuid1().hex
        if isinstance(cfg, dict):
            self.cfg = cfg
        else:
            raise TypeError(f'cfg: excepted a dict, got a {type(cfg)}')
        
    def title(self, title='', description='', title_cfg={}, description_cfg={}):
        _title=None
        _description=None
        if title:
            _title = dict(visible=True,text=title)
        if title_cfg and isinstance(title_cfg, dict):
            _title = title_cfg
        
        if description:
            _description = dict(visible=True,text=description)
        if description_cfg and isinstance(description_cfg, dict):
            _description = description_cfg
            
        self.cfg['title'] = _title
        self.cfg['description'] = _description
        return self

    def guide_line(self, cfg):
        if isinstance(cfg, list):
            for item in cfg:
                if not isinstance(item, dict):
                    raise TypeError(f'item in cfg: excepted a dict, got a {type(item)}')
        else:
            raise TypeError(f'cfg: excepted a list, got a {type(cfg)}')
        self.cfg['guideLine'] = cfg
        return self
    
    def legend(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError(f'cfg: excepted a dict, got a {type(cfg)}')
        self.cfg['legend'] = cfg
        return self
    
    def theme(self, theme):
        if theme in ['default','dark']:
            self.cfg['theme'] = theme
        else:
            raise ValueError(f'illegal theme name: {theme}, use "default" or "dark".')
        return self
        
    def axis(self, xAxis={}, yAxis={}):
        if isinstance(xAxis, dict):
            self['cfg']['xAxis'] = xAxis
        if isinstance(yAxis, dict):
            self['cfg']['yAxis'] = yAxis
        return self
    
    def tooltip(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError(f'cfg: excepted a dict, got a {type(cfg)}')
        self.cfg['tooltip'] = cfg
        return self
    
    def render(self):
        self.cfg = json.dumps(self.cfg,ensure_ascii=False)
        return HTML(self.template.render(self.__dict__)) if 'ipykernel' in sys.modules else self.template.render(self.__dict__)
    
    def save(self, path):
        self.cfg = json.dumps(self.cfg,ensure_ascii=False)
        with open(path, 'w') as f:
            f.write(self.template.render(self.__dict__))
    
def validate_field(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        args_dict = dict(zip(inspect.getfullargspec(f)[0], ['self']+list(args)))
        for k,v in args_dict.items():
            if k.endswith('Field') and '.' in v:
                raise ValueError(f'remove the dot(.) in {self.__class__.__name__} args: {k}={v}')
        return f(self,*args,**kwargs)
    return wrapper


class line(G2):
    @validate_field
    def __init__(self, data, xField, yField, seriesField='', cfg={}):
        super(line,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['seriesField'] = seriesField
        self.geom = self.ChartType.line.value
        
class step_line(G2):
    @validate_field
    def __init__(self, data, xField, yField, seriesField='', step='', cfg={}):
        super(step_line,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['seriesField'] = seriesField
        self.geom = self.ChartType.step_line.value


class treemap(G2):
    @validate_field
    def __init__(self, data, maxLevel=2, cfg={}):
        super(treemap,self).__init__(cfg)
        # sort N-1 colmuns by level
        data_sort = data[data.iloc[:,:-1].nunique().to_frame(name='v').sort_values(by=['v']).index.tolist() + [data.columns[-1]]]
        df_json = dict(name="root", value=sum(data.iloc[:,-1]), children=df2treemap_json(data_sort))
        self.data = json.dumps(df_json, cls=npEncoder)
        self.cfg['maxLevel'] = maxLevel
        self.cfg['colorField'] = 'name' if data_sort.shape[1]==2 else 'color'
        self.geom = self.ChartType.treemap.value
        
class bar(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(bar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.bar.value

        
class stacked_bar(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField='', cfg={}):
        super(stacked_bar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.stacked_bar.value

        
class grouped_bar(G2):
    @validate_field
    def __init__(self, data, xField, yField, groupField='',cfg={}):
        super(grouped_bar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['groupField'] = groupField
        self.geom = self.ChartType.grouped_bar.value

        
class percent_stacked_bar(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField, cfg={}):
        super(percent_stacked_bar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.percent_stacked_bar.value

        
class range_bar(G2):
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(range_bar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.range_bar.value

        
class area(G2):
    @validate_field
    def __init__(self, data, xField, yField, seriesField='', cfg={}):
        super(area,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['seriesField'] = seriesField
        self.geom = self.ChartType.area.value

        
class stacked_area(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField ='',cfg={}):
        super(stacked_area,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.stacked_area.value

        
class percent_stacked_area(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField='', cfg={}):
        super(percent_stacked_area,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.percent_stacked_area.value
        
        
class column(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(column,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.column.value
        
        
class grouped_column(G2):
    @validate_field
    def __init__(self, data, xField, yField, groupField='', cfg={}):
        super(grouped_column,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['groupField'] = groupField
        self.geom = self.ChartType.grouped_column.value

        
class stacked_column(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField='', cfg={}):
        super(stacked_column,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.stacked_column.value
        
        
class range_column(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(range_column,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.range_column.value

        
class percent_stacked_column(G2):
    @validate_field
    def __init__(self, data, xField, yField, stackField='', cfg={}):
        super(percent_stacked_column,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.percent_stacked_column.value

        
class pie(G2):
    @validate_field
    def __init__(self, data, colorField, angleField, radius=0.8, cfg={}):
        super(pie,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['angleField'] = angleField
        self.cfg['colorField'] = colorField
        self.cfg['radius'] = radius
        self.geom = self.ChartType.pie.value

        
class density_heatmap(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField, cfg={}):
        super(density_heatmap,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.density_heatmap.value

        
class heatmap(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField, sizeField='', shapeType='rect', cfg={}):
        super(heatmap,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        if sizeField:
            self.cfg['sizeField'] = sizeField
        self.cfg['shapeType'] = shapeType
        self.geom = self.ChartType.heatmap.value

        
class word_cloud(G2):
    @validate_field
    def __init__(self, data, maskImage='', shape='circle', cfg={}):
        super(word_cloud,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['shape'] = shape
        if maskImage:
            self.cfg['maskImage'] = maskImage
        self.geom = self.ChartType.word_cloud.value

        
class rose(G2):
    @validate_field
    def __init__(self, data, radiusField, categoryField, colorField='', cfg={}):
        super(rose,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['radiusField'] = radiusField
        self.cfg['categoryField'] = categoryField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.rose.value

        
class funnel(G2):
    @validate_field
    def __init__(self, data, xField, yField, compareField='', dynamicHeight=False,transpose=False,cfg={}):
        super(funnel,self).__init__(cfg)
        # data = data.sort_values(by=[yField],ascending=False).reset_index()
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['dynamicHeight'] = dynamicHeight
        self.cfg['transpose'] = transpose
        self.cfg['compareField'] = compareField
        self.geom = self.ChartType.funnel.value

        
class stacked_rose(G2):
    @validate_field
    def __init__(self, data, radiusField, categoryField, stackField, cfg={}):
        super(stacked_rose,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['radiusField'] = radiusField
        self.cfg['categoryField'] = categoryField
        self.cfg['stackField'] = stackField
        self.geom = self.ChartType.stacked_rose.value

        
class grouped_rose(G2):
    @validate_field
    def __init__(self, data, radiusField, categoryField, colorField, cfg={}):
        super(grouped_rose,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['radiusField'] = radiusField
        self.cfg['categoryField'] = categoryField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.grouped_rose.value

        
class radar(G2):
    @validate_field
    def __init__(self, data, angleField, radiusField, seriesField='', cfg={}):
        super(radar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['angleField'] = angleField
        self.cfg['radiusField'] = radiusField
        self.cfg['seriesField'] = seriesField
        self.geom = self.ChartType.radar.value

        
class liquid(G2):
    @validate_field
    def __init__(self, value, max, min, cfg={}):
        super(liquid,self).__init__(cfg)
        self.data = []
        self.cfg['value'] = value
        self.cfg['max'] = max
        self.cfg['min'] = min
        self.geom = self.ChartType.liquid.value

        
class histogram(G2):
    @validate_field
    def __init__(self, data, binField, binWidth=None, binNumber=None, cfg={}):
        super(histogram,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['binField'] = binField
        self.cfg['binWidth'] = binWidth
        self.cfg['binNumber'] = binNumber
        self.geom = self.ChartType.histogram.value

        
class density(G2):
    @validate_field
    def __init__(self, data, binField, binWidth=None,binNumber=None, cfg={}):
        super(density,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['binField'] = binField
        if binWidth:
            self.cfg['binWidth'] = binWidth
        self.geom = self.ChartType.density.value

        
class donut(G2):
    @validate_field
    def __init__(self, data, angleField, colorField='', radius=0.8, innerRadius=0.8, cfg={}):
        super(donut,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['angleField'] = angleField
        self.cfg['colorField'] = colorField
        self.cfg['radius'] = radius
        self.cfg['innerRadius'] = innerRadius
        self.geom = self.ChartType.donut.value

        
class waterfall(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(waterfall,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.waterfall.value

        
class scatter(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField='', cfg={}):
        super(scatter,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.geom = self.ChartType.scatter.value

        
class bubble(G2):
    @validate_field
    def __init__(self, data, xField, yField, colorField, sizeField, cfg={}):
        super(bubble,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['xField'] = xField
        self.cfg['yField'] = yField
        self.cfg['colorField'] = colorField
        self.cfg['sizeField'] = sizeField
        self.geom = self.ChartType.bubble.value

        
class bullet(G2):
    @validate_field
    def __init__(self, data, rangeMax, measureSize=20, cfg={}):
        super(bullet,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['rangeMax'] = rangeMax
        self.cfg['measureSize'] = measureSize
        self.geom = self.ChartType.bullet.value

        
class calendar(G2):
    @validate_field
    def __init__(self, data, dateField, valueField, months='', weeks='', cfg={}):
        super(calendar,self).__init__(cfg)
        self.data = data.to_json(orient='records')
        self.cfg['dateField'] = dateField
        self.cfg['valueField'] = valueField
        self.cfg['months'] = months
        self.cfg['weeks'] = weeks
        self.geom = self.ChartType.calendar.value

        
class gauge(G2):
    @validate_field
    def __init__(self, value, range=[], min=0, max=1, cfg={}):
        super(gauge,self).__init__(cfg)
        if not min <= value <= max:
            raise ValueError(f'value out of range [{min},{max}]')
        self.data = []
        self.cfg['value'] = value
        self.cfg['min'] = min
        self.cfg['max'] = max
        self.cfg['range'] = range if range else [min, value]
        self.geom = self.ChartType.gauge.value

        
class fan_gauge(G2):
    @validate_field
    def __init__(self, value, range=[], min=0, max=1, cfg={}):
        super(fan_gauge,self).__init__(cfg)
        if not min <= value <= max:
            raise ValueError(f'value out of range [{min},{max}]')
        self.data = []
        self.cfg['value'] = value
        self.cfg['min'] = min
        self.cfg['max'] = max
        self.cfg['range'] = range if range else [min, value]
        self.geom = self.ChartType.fan_gauge.value

        
class meter_gauge(G2):
    @validate_field
    def __init__(self, value, range=[], min=0, max=1, cfg={}):
        super(meter_gauge,self).__init__(cfg)
        if not min <= value <= max:
            raise ValueError(f'value out of range [{min},{max}]')
        self.data = []
        self.cfg['value'] = value
        self.cfg['min'] = min
        self.cfg['max'] = max
        self.cfg['range'] = range if range else [min, value]
        self.geom = self.ChartType.meter_gauge.value

