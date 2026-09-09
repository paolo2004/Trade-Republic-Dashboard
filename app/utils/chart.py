"""Shared Plotly styling.

Registering a default template means every chart picks up the app's look, even
the ones that never call `style_chart` explicitly.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Categorical slots, in fixed order. Validated against the card surface
# (#10151d) in dark mode: worst adjacent CVD deltaE 9.1, worst normal-vision
# deltaE 19.2, all slots inside the dark lightness band and above 3:1 contrast.
#
# Assign these in order and never cycle past slot 8. Only the first THREE are
# safe when every colour is compared against every other (pie/donut) - past
# that, use a sorted bar chart instead.
CATEGORICAL = [
    "#4c8dff",  # blue
    "#b8d3f8",  # light blue
    "#d95926",  # orange
    "#2aa877",  # green
    "#c98500",  # yellow
    "#d55181",  # magenta
    "#008300",  # deep green
    "#9085e9",  # violet
    "#e66767",  # red
]

# Semantic colours for profit/loss. These sit outside the categorical band on
# purpose: they encode meaning, not identity, and are never used as series 4.
POSITIVE = "#32c48d"
NEGATIVE = "#ff647c"
MIDPOINT = "#64748b"

# Red -> grey -> green reads as a loss/gain axis. It is only legible because
# the charts using it also encode the sign by position (bars diverge from
# zero), so colour is reinforcement rather than the sole channel.
DIVERGING = [NEGATIVE, MIDPOINT, POSITIVE]

TEXT_SECONDARY = "#9aa4b2"
GRID = "rgba(255,255,255,0.06)"


def register_chart_theme():
    """Register and activate the app-wide Plotly template."""
    if "tr" not in pio.templates:
        pio.templates["tr"] = go.layout.Template(
            layout=dict(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                colorway=CATEGORICAL,
                font=dict(color=TEXT_SECONDARY, size=12),
                margin=dict(l=10, r=10, t=10, b=10),
                hoverlabel=dict(
                    bgcolor="#131a23",
                    bordercolor="rgba(255,255,255,0.12)",
                ),
                legend=dict(
                    title=None,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(
                    gridcolor=GRID,
                    zerolinecolor="rgba(255,255,255,0.12)",
                ),
                colorscale=dict(diverging=DIVERGING),
            )
        )
    pio.templates.default = "plotly_dark+tr"


def style_chart(fig, height=350):
    """Apply the per-figure settings the template cannot carry."""
    fig.update_layout(height=height)
    return fig


def show_chart(fig, height=350):
    """Render a chart with consistent sizing and no Plotly toolbar."""
    st.plotly_chart(
        style_chart(fig, height),
        width="stretch",
        config={"displayModeBar": False},
    )
