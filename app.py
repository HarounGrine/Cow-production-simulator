import streamlit as st
from simulation import run_simulation
from Monte_Carlo import monte_carlo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Cow Simulation")
st.write("Click the button Run Simulation for a single herd simulation or use the Monte Carlo simulation to compare strategies.")

herd_size = st.sidebar.slider("Herd Size", min_value=1, max_value=100, value=10)
dairy_ratio = st.sidebar.slider("Dairy Cow Ratio", min_value=0.0, max_value=1.0, value=0.6)
max_months = st.sidebar.slider("Max Months", min_value=1, max_value=240, value=120)
feed_type = st.sidebar.selectbox("Feed Type", ["budget", "standard", "premium"])
medicine_type = st.sidebar.selectbox("Medicine Type", ["basic", "standard", "premium"])


if st.sidebar.button("Run Simulation"):
    cows = run_simulation(herd_size, dairy_ratio, max_months, feed_type, medicine_type)
    data = []
    for cow in cows:
        profit = cow.cumulative_revenue - cow.cumulative_feed_cost - cow.cumulative_vet_cost
        data.append({
            "id": cow.id,
            "type": cow.type,
            "exit": cow.stage,
            "revenue": cow.cumulative_revenue,
            "feed_cost": cow.cumulative_feed_cost,
            "vet_cost": cow.cumulative_vet_cost,
            "profit": profit
        })

    df = pd.DataFrame(data) 
    st.dataframe(df)

    st.header("Herd Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Herd Profit", f"${df['profit'].sum():,.0f}")
    col2.metric("Avg Profit per Cow", f"${df['profit'].mean():,.0f}")
    col3.metric("Best Cow", f"${df['profit'].max():,.0f}")
    col4.metric("Worst Cow", f"${df['profit'].min():,.0f}")

    with st.expander("Individual Cow Performance"):
        fig = px.bar(
            df.sort_values("profit", ascending=False),
            x="id",
            y="profit",
            color="type",
            color_discrete_map={"dairy": "steelblue", "beef": "darkorange"},
            labels={"id": "Cow ID", "profit": "Profit ($)", "type": "Type"},
            title="Profit per Cow"
        )

        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Revenue vs Cost Analysis"):
        summary = df.groupby("type")[["revenue", "feed_cost", "vet_cost"]].mean().reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Revenue", x=summary["type"], y=summary["revenue"], marker_color="green"))
        fig2.add_trace(go.Bar(name="Feed Cost", x=summary["type"], y=summary["feed_cost"], marker_color="red"))
        fig2.add_trace(go.Bar(name="Vet Cost", x=summary["type"], y=summary["vet_cost"], marker_color="orange"))

        fig2.update_layout(barmode="group", title="Average Revenue vs Costs by Cow Type",
                        xaxis_title="Type", yaxis_title="Amount ($)")
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Profit Distribution"):

        fig3 = px.histogram(
            df,
            x="profit",
            color="type",
            nbins=20,
            color_discrete_map={"dairy": "steelblue", "beef": "darkorange"},
            labels={"profit": "Profit ($)", "type": "Type"},
            title="Distribution of Profit across Herd",
            barmode="overlay",
            opacity=0.7
        )
        fig3.add_vline(x=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig3, use_container_width=True)

#Monte carlo simulation

with st.expander("Strategy Comparison — Monte Carlo", expanded=False):
    st.write("Automatically compares **budget + basic medicine** vs **premium + premium medicine** using the same herd size and dairy ratio.")
    n_runs = st.slider("Number of Monte Carlo Runs", min_value=10, max_value=1000, value=100, step=10)
    if st.button("Run Monte Carlo"):
        with st.spinner("Running simulations..."):
            budget_results = monte_carlo("budget", "basic", n_runs)
            premium_results = monte_carlo("premium", "premium", n_runs)

        st.subheader("Average Profit Comparison")
        col1, col2 = st.columns(2)
        col1.metric("Budget Strategy — Avg Profit",
                    f"${budget_results['avg_profit']:,.0f}",
                    f"±${budget_results['std_dev_profit']:,.0f}")
        col2.metric("Premium Strategy — Avg Profit",
                    f"${premium_results['avg_profit']:,.0f}",
                    f"±${premium_results['std_dev_profit']:,.0f}")

        st.subheader("ROI Comparison")
        col3, col4 = st.columns(2)
        col3.metric("Budget ROI", f"{budget_results['avg_roi']:.1f}%",
                    f"±{budget_results['std_dev_roi']:.1f}%")
        col4.metric("Premium ROI", f"{premium_results['avg_roi']:.1f}%",
                    f"±{premium_results['std_dev_roi']:.1f}%")

        st.subheader("Profit Distribution — Budget vs Premium")
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Box(
            name="Budget",
            q1=[budget_results['q1_profit']],
            median=[budget_results['avg_profit']],
            q3=[budget_results['q3_profit']],
            mean=[budget_results['avg_profit']],
            lowerfence=[budget_results['q1_profit'] - 1.5 * budget_results['std_dev_profit']],
            upperfence=[budget_results['q3_profit'] + 1.5 * budget_results['std_dev_profit']],
            marker_color="coral"
        ))
        fig_mc.add_trace(go.Box(
            name="Premium",
            q1=[premium_results['q1_profit']],
            median=[premium_results['avg_profit']],
            q3=[premium_results['q3_profit']],
            mean=[premium_results['avg_profit']],
            lowerfence=[premium_results['q1_profit'] - 1.5 * premium_results['std_dev_profit']],
            upperfence=[premium_results['q3_profit'] + 1.5 * premium_results['std_dev_profit']],
            marker_color="steelblue"
        ))
        fig_mc.update_layout(title="Profit Range — Budget vs Premium Strategy",
                             yaxis_title="Total Herd Profit ($)")
        st.plotly_chart(fig_mc, use_container_width=True)