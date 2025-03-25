def toon_klokstijl_wijzer(score):
    angle = (1 - score) * math.pi  # -1 = 180°, +1 = 0°
    x = 0.5 + 0.3 * math.cos(angle)
    y = 0.5 + 0.3 * math.sin(angle)

    fig = go.Figure()

    # Wijzer (wit, vanaf midden naar eindpunt)
    fig.add_trace(go.Scatter(
        x=[0.5, x],
        y=[0.5, y],
        mode="lines",
        line=dict(color="white", width=6),
        showlegend=False
    ))

    # Neutrale stip (bovenaan)
    fig.add_trace(go.Scatter(
        x=[0.5],
        y=[0.85],
        mode="markers",
        marker=dict(size=12, color="green"),
        showlegend=False
    ))

    # Cirkel als achtergrond
    fig.add_shape(type="circle",
        x0=0.1, y0=0.1, x1=0.9, y1=0.9,
        line=dict(color="gray", width=2)
    )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="black",
        paper_bgcolor="black",
        width=300,
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig)


