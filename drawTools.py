from abc import ABC, abstractmethod
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt


class DrawChart(ABC):

    """Type of available interpolation

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
    """

    def __init__(self, title, data, target='дата', type_='quantitative', interpolate='linear', point=False, height=600, 
        width=800, scheme='category10', level=False, poly=None):

        self.title = title
        self.target = target
        self.data = data.melt(target, var_name='показатель', value_name='y')
        self.type_ = type_
        self.interpolate = interpolate
        self.point = point
        self.width = width
        self.height = height
        self.scheme = scheme
        self.level = level
        self.poly = poly

    @abstractmethod
    def draw(self):
        pass

    def select(self):
        # Create a selection that chooses the nearest point & selects based on x-value
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
                axis=alt.Axis(grid=True, offset=10)
                ),
            alt.Y('y', 
                type=self.type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=True, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme=self.scheme),
                legend=alt.Legend(
                    labelFontSize=16, 
                    labelColor='#808080', 
                    orient='top-left', title='', 
                    labelLimit=320
                    )
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
                scale=alt.Scale(scheme=self.scheme)
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
        # Create a chart
        # With baseline == level
        rule = alt.Chart(pd.DataFrame({'y': [self.level]})
            ).mark_rule().encode(
                y='y',
                size=alt.value(0.5),
                )
        return self.chart + rule

    def polynomialchart(self):
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
        return self.chart


class Linear(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_line(interpolate=self.interpolate, point=self.point)
        self.select()


class Point(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_point(interpolate=self.interpolate)
        self.select()


class Area(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_area(interpolate=self.interpolate)
        self.select()


class Bar(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_bar()
        self.select()
