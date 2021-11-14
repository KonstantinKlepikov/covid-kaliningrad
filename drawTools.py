from abc import ABC, abstractmethod
from altair.vegalite.v4.schema.channels import Opacity
import numpy as np
import pandas as pd
import altair as alt


def my_color_theme():
  return {
    'config': {
      'view': {'continuousHeight': 300, 'continuousWidth': 400},
      'range': {'category': ['#e83b3b', '#4d9be6', '#0b8a8f', '#fb6b1d', '#a884f3', '#fbb954', '#1ebc73', '#f04f78', '#4d65b4', '#91db69', '#c32454', '#cd683d', '#905ea9', '#831c5d', '#0b8a8f', '#f68181', 
'#8fd3ff', '#fca790', '#8ff8e2', '#fbff86', '#e3c896', '#0b5e65', '#eaaded', '#7a3045', '#905ea9', '#9e4539', '#ab947a', '#484a77', '#3e3546', '#966c6c', '#625565', '#30e1b9',]}
    }
  }
alt.themes.register('my_color_theme', my_color_theme)
alt.themes.enable('my_color_theme')


class DrawChart(ABC):

    """ ABC class for draw charts

        Args:
            title (string): title for chart

            data (pandas DataFrame): data for chart drawing

            target (string): axis X, default'дата'
            
            type_ (string): type of representation data, default 'quantitative'

            interpolate (string): type of line interpolation on chart, default 'linear'
                Type of available interpolation:
                basis
                basis-open
                basis-closed
                bundle
                cardinal
                cardinal-open
                cardinal-closed
                catmull-rom
                linear
                linear-closed
                monotone
                natural
                step
                step-before
                step-after
            
            point (bool): markers on chart are pointed, default False

            height (int): height of chart window, default 600

            width (int): width of chart window, default 800

            level (bool): is available baseline, default False

            poly (int): is drawing polynomial regression, default None
                numerical define degree of regression

            grid (bool): is used a grid on main chart, default True
    """

    def __init__(self, title, data, target='дата', type_='quantitative', interpolate='linear', point=False, height=600, 
        width=800, level=False, poly=None, grid=True):

        self.title = title
        self.target = target
        self.data = data.melt(target, var_name='показатель', value_name='y')
        self.type_ = type_
        self.interpolate = interpolate
        self.point = point
        self.width = width
        self.height = height
        self.level = level
        self.poly = poly
        self.grid = grid
        self.legend = alt.Legend(
            labelFontSize=16, 
            labelColor='#808080', 
            orient='top-left', title='', 
            labelLimit=320,
            zindex=1
            )

    @abstractmethod
    def draw(self):
        pass

    def _select(self):
        """Create a selection that chooses the nearest point & selects based on x-value
        """

        nearest = alt.selection(
            type='single',
            nearest=True,
            on='mouseover',
            fields=[self.target],
            empty='none'
            )

        # Selection in a legend
        self.leg = alt.selection_multi(fields=['показатель'], bind='legend')

        # Draw a chart
        self.line = self.draw.encode(
            alt.X(self.target, 
                type='temporal', 
                title=' ', 
                axis=alt.Axis(grid=self.grid, offset=10)
                ),
            alt.Y('y', 
                type=self.type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=self.grid, offset=10)
                ),
            alt.Color('показатель:N',
                legend=self.legend
                ),
            opacity=alt.condition(self.leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )

        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        self.selectors = alt.Chart(self.data).mark_point().encode(
                            alt.X(self.target, type='temporal'),
                            opacity=alt.value(0),
                        ).add_selection(
                            nearest
                        )
        
        # Draw points on the line, and highlight based on selection
        self.points = self.line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        # Draw text labels near the points, and highlight based on selection
        self.text = self.line.mark_text(
            align='right', 
            dx=-5, 
            fill='#000000', 
            fontSize=16, 
            clip=False).encode(
                text=alt.condition(nearest, 'y', alt.value(''), type=self.type_)
        )

        # Draw X value on chart
        self.x_text = self.line.mark_text(
            align="left", 
            dx=-5, dy=15, 
            fill='#808080', 
            fontSize=16).encode(
                text=alt.condition(nearest, self.target, alt.value(''), type='temporal', format='%Y-%m-%d')
        )

        # Draw a rule at the location of the selection
        self.rules = alt.Chart(self.data).mark_rule(color='gray').encode(
            alt.X(self.target, type='temporal')
        ).transform_filter(
            nearest
        )

    def leanchart(self):
        """Simple selection on chart
        """

        self.chart = alt.layer(
            self.line, self.selectors, self.rules
        ).properties(
            title=self.title,
            width=self.width,
            height=self.height
        ).add_selection(
            self.leg
        )

    def richchart(self):
        """Complicated selection on chart
        """

        self.chart = alt.layer(
            self.line, self.selectors, self.points, self.rules, self.text, self.x_text
        ).properties(
            title=self.title,
            width=self.width,
            height=self.height
        ).add_selection(
            self.leg
        )

    def selectionchart(self):
        """Chart with bottom time period selection

        Returns:
            [obj]: [altair chart object with time selection chart]
        """

        brush = alt.selection(type='interval', encodings=['x'])
        upper = self.chart.encode(
            alt.X('date:T', scale=alt.Scale(domain=brush))
        )
        inline = self.draw.encode(
            alt.X(self.target, 
                type='temporal',
                title=' ', 
                axis=alt.Axis(grid=False)
                ),
            alt.Y('y', 
                type=self.type_, 
                scale=alt.Scale(zero=False),
                title=' ',
                axis=alt.Axis(grid=False, labels=False)
                ),
            alt.Color('показатель:N',
                ),
            opacity=alt.condition(self.leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )
        lower = alt.layer(
            inline, self.rules
        ).properties(
            width=self.width,
            height=20
        ).add_selection(
            brush
        )
        return upper & lower

    def baselinechart(self):
        """Baseline on chart

        Returns:
            [obj]: [altair chart object with baseline]
        """

        # baseline == level
        rule = alt.Chart(pd.DataFrame({'y': [self.level]})
            ).mark_rule().encode(
                y='y',
                size=alt.value(0.5),
                )
        return self.chart + rule

    def polynomialchart(self):
        """Polynomial regression addon for chart

        Returns:
            [obj]: [altair chart object with polinimial regression]
        """

        degree_list = self.poly,
        polynomial_fit = [
            self.line.transform_regression(
                self.target, 'y', method='poly', order=order, as_=[self.target, str(order)]
            ).mark_line(
            ).transform_fold(
                [str(order)], as_=['регрессия', 'y']
            ).encode(alt.Color('регрессия:N'))
            for order in degree_list
        ]
        return alt.layer(self.chart, *polynomial_fit)

    def emptychart(self):
        """Chart

        Returns:
            [obj]: [altair chart object]
        """

        return self.chart


class Linear(DrawChart):
    """Draw linear chart
    """

    def draw(self):
        self.draw = alt.Chart(self.data).mark_line(interpolate=self.interpolate, point=self.point)
        self._select()


class Point(DrawChart):
    """Draw point chart
    """

    def draw(self):
        self.draw = alt.Chart(self.data).mark_point(interpolate=self.interpolate)
        self._select()


class Area(DrawChart):
    """Draw area linear chart
    """

    def draw(self):
        self.draw = alt.Chart(self.data).mark_area(interpolate=self.interpolate)
        self._select()


class Bar(DrawChart):
    """Draw histogram
    """

    def draw(self):
        self.draw = alt.Chart(self.data).mark_bar()
        self._select()
