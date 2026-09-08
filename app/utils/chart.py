def style_chart(fig, height=350):
    fig.update_layout(
        height=height,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#9aa4b2",
            size=12,
        ),

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),

        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickprefix="€",
        tickformat=",.0f",
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
    )

    return fig