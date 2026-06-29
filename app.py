import streamlit as st
from simulation import run_simulation
from Monte_Carlo import monte_carlo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Cow Production Simulator")
st.title("🐄 Cow Production Simulator")

# ─── Layout ───────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2])

# ─── Left Column: Controls ────────────────────────────────────────────────────
with left:
    st.header("⚙️ Simulation Controls")
    herd_size     = st.slider("Herd Size",        min_value=1,   max_value=100, value=10)
    dairy_ratio   = st.slider("Dairy Cow Ratio",  min_value=0.0, max_value=1.0, value=0.6)
    max_months    = st.slider("Max Months",        min_value=1,   max_value=240, value=120)
    feed_type     = st.selectbox("Feed Type",     ["budget", "standard", "premium"])
    medicine_type = st.selectbox("Medicine Type", ["basic",  "standard", "premium"])
    run_sim       = st.button("🚀 Run Simulation", use_container_width=True)

    st.divider()

    st.header("🎲 Monte Carlo")
    n_runs     = st.slider("Number of Runs", min_value=10, max_value=200, value=50, step=10)
    run_mc     = st.button("▶ Run Monte Carlo", use_container_width=True)

# ─── Session state ────────────────────────────────────────────────────────────
if "cows" not in st.session_state:
    st.session_state.cows = None
if "df" not in st.session_state:
    st.session_state.df = None

# ─── Run simulation ───────────────────────────────────────────────────────────
if run_sim:
    cows = run_simulation(herd_size, dairy_ratio, max_months, feed_type, medicine_type)
    data = []
    for cow in cows:
        profit = cow.cumulative_revenue - cow.cumulative_feed_cost - cow.cumulative_vet_cost
        data.append({
            "id":         cow.id,
            "type":       cow.type,
            "exit":       cow.stage,
            "revenue":    cow.cumulative_revenue,
            "feed_cost":  cow.cumulative_feed_cost,
            "vet_cost":   cow.cumulative_vet_cost,
            "profit":     cow.profit,
            "roi":        cow.roi,
            "feed_type":  cow.feed_type,
            "medicine":   cow.medicine_type,
            "illness":    cow.illness_count,
            "avg_stress": cow.avg_stress_level,
        })
    st.session_state.cows = cows
    st.session_state.df   = pd.DataFrame(data)

# ─── Right Column: Results ────────────────────────────────────────────────────
with right:
    if st.session_state.df is not None:
        df   = st.session_state.df
        cows = st.session_state.cows

        # ── Herd Summary ──────────────────────────────────────────────────────
        st.header("📊 Herd Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Profit",       f"${df['profit'].sum():,.0f}")
        c2.metric("Avg Profit per Cow", f"${df['profit'].mean():,.0f}")
        c3.metric("Best Cow",           f"${df['profit'].max():,.0f}")
        c4.metric("Worst Cow",          f"${df['profit'].min():,.0f}")

        # ── Individual Cow Performance ────────────────────────────────────────
        with st.expander("🐮 Individual Cow Performance", expanded=False):
            st.dataframe(df)
            fig = px.bar(
                df.sort_values("profit", ascending=False),
                x="id", y="profit", color="type",
                color_discrete_map={"dairy": "steelblue", "beef": "darkorange"},
                labels={"id": "Cow ID", "profit": "Profit ($)", "type": "Type"},
                title="Profit per Cow"
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig, use_container_width=True)

        # ── Revenue vs Cost ───────────────────────────────────────────────────
        with st.expander("💰 Revenue vs Cost Analysis", expanded=False):
            summary = df.groupby("type")[["revenue", "feed_cost", "vet_cost"]].mean().reset_index()
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Revenue",   x=summary["type"], y=summary["revenue"],   marker_color="green"))
            fig2.add_trace(go.Bar(name="Feed Cost", x=summary["type"], y=summary["feed_cost"], marker_color="red"))
            fig2.add_trace(go.Bar(name="Vet Cost",  x=summary["type"], y=summary["vet_cost"],  marker_color="orange"))
            fig2.update_layout(barmode="group", title="Average Revenue vs Costs by Cow Type",
                               xaxis_title="Type", yaxis_title="Amount ($)")
            st.plotly_chart(fig2, use_container_width=True)

        # ── Profit Distribution ───────────────────────────────────────────────
        with st.expander("📈 Profit Distribution", expanded=False):
            fig3 = px.histogram(
                df, x="profit", color="type", nbins=20,
                color_discrete_map={"dairy": "steelblue", "beef": "darkorange"},
                labels={"profit": "Profit ($)", "type": "Type"},
                title="Distribution of Profit across Herd",
                barmode="overlay", opacity=0.7
            )
            fig3.add_vline(x=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig3, use_container_width=True)

        # ── Cow Inspector ─────────────────────────────────────────────────────
        with st.expander("🔍 Cow Inspector", expanded=False):
            cow_ids = [cow.id for cow in cows]
            selected_id = st.selectbox("Select Cow", cow_ids)
            selected_cow = next(c for c in cows if c.id == selected_id)

            st.subheader(f"Cow {selected_cow.id} — {selected_cow.type.capitalize()} | {selected_cow.feed_type} feed | {selected_cow.medicine_type} medicine")

            if selected_cow.type == "dairy":
                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Milk (L)",   f"{selected_cow.total_milk_liters:,.0f}")
                m2.metric("Peak Yield (L/mo)", f"{selected_cow.peak_milk_yield:,.0f}")
                avg_fat = sum(q["fat"] for q in selected_cow.monthly_milk_quality) / len(selected_cow.monthly_milk_quality) if selected_cow.monthly_milk_quality else 0
                avg_scc = sum(q["scc"] for q in selected_cow.monthly_milk_quality) / len(selected_cow.monthly_milk_quality) if selected_cow.monthly_milk_quality else 0
                m3.metric("Avg Fat %",        f"{avg_fat:.2f}%")
                m4.metric("Avg SCC",          f"{avg_scc:,.0f}")

                # Milk yield curve
                milk_df = pd.DataFrame({
                    "Month": list(range(1, len(selected_cow.monthly_milk_liters) + 1)),
                    "Liters": selected_cow.monthly_milk_liters
                })
                fig_milk = px.line(milk_df, x="Month", y="Liters",
                                   title="Monthly Milk Yield (Lactation Curve)",
                                   labels={"Liters": "Liters / Month"})
                st.plotly_chart(fig_milk, use_container_width=True)

                # Milk quality over time
                quality_df = pd.DataFrame(selected_cow.monthly_milk_quality)
                quality_df["Month"] = list(range(1, len(quality_df) + 1))
                fig_qual = go.Figure()
                fig_qual.add_trace(go.Scatter(x=quality_df["Month"], y=quality_df["fat"],
                                              name="Fat %", line=dict(color="gold")))
                fig_qual.add_trace(go.Scatter(x=quality_df["Month"], y=quality_df["protein"],
                                              name="Protein %", line=dict(color="steelblue")))
                fig_qual.update_layout(title="Milk Quality — Fat & Protein %",
                                       xaxis_title="Month", yaxis_title="%")
                st.plotly_chart(fig_qual, use_container_width=True)

                # SCC chart
                fig_scc = go.Figure()
                fig_scc.add_trace(go.Scatter(x=quality_df["Month"], y=quality_df["scc"],
                                             name="SCC", line=dict(color="red")))
                fig_scc.add_hline(y=400, line_dash="dash", line_color="darkred",
                                  annotation_text="Rejection threshold")
                fig_scc.add_hline(y=200, line_dash="dash", line_color="orange",
                                  annotation_text="Grade B threshold")
                fig_scc.update_layout(title="Somatic Cell Count (SCC) over Time",
                                      xaxis_title="Month", yaxis_title="SCC (cells/mL × 1000)")
                st.plotly_chart(fig_scc, use_container_width=True)

            else:  # beef
                # Beef grade display
                grade_colors = {"Prime": "gold", "Choice": "silver", "Select": "#cd7f32"}
                grade = selected_cow.beef_grade or "Unknown"
                grade_color = grade_colors.get(grade, "gray")
                st.markdown(f"""
                    <div style='text-align:center; padding:20px; border-radius:12px;
                                background-color:{grade_color}; margin-bottom:20px'>
                        <h1 style='color:black; margin:0'>🥩 {grade}</h1>
                        <p style='color:black; margin:0'>USDA Beef Grade</p>
                    </div>
                """, unsafe_allow_html=True)

                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Carcass Weight",    f"{selected_cow.carcass_weight:,.1f} kg")
                m2.metric("Dressing %",        f"{selected_cow.dressing_percentage:.1%}")
                m3.metric("Slaughter Weight",  f"{selected_cow.weight:,.1f} kg")
                m4.metric("Illness Count",     f"{selected_cow.illness_count}")

                # Weight gain curve
                weight_df = pd.DataFrame({
                    "Month":  list(range(1, len(selected_cow.monthly_weights) + 1)),
                    "Weight": selected_cow.monthly_weights
                })
                fig_w = px.line(weight_df, x="Month", y="Weight",
                                title="Weight Gain over Lifetime",
                                labels={"Weight": "Weight (kg)"})
                fig_w.add_hline(y=600, line_dash="dash", line_color="red",
                                annotation_text="Slaughter threshold")
                st.plotly_chart(fig_w, use_container_width=True)

            # Health & Financial summary (both types)
            st.subheader("🏥 Health Summary")
            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Illness Events",  selected_cow.illness_count)
            h2.metric("Avg Stress",      f"{selected_cow.avg_stress_level:.3f}")
            h3.metric("Feed Type",       selected_cow.feed_type.capitalize())
            h4.metric("Medicine Type",   selected_cow.medicine_type.capitalize())

            st.subheader("💵 Financial Summary")
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Revenue",  f"${selected_cow.cumulative_revenue:,.0f}")
            f2.metric("Cost",     f"${selected_cow.cost:,.0f}")
            f3.metric("Profit",   f"${selected_cow.profit:,.0f}")
            f4.metric("ROI",      f"{selected_cow.roi:.1f}%")

        # ── Herd Production Summary ───────────────────────────────────────────
        with st.expander("🏭 Herd Production Summary", expanded=False):
            dairy_cows = [c for c in cows if c.type == "dairy"]
            beef_cows  = [c for c in cows if c.type == "beef"]

            if dairy_cows:
                st.subheader("🥛 Dairy Production")
                d1, d2, d3, d4 = st.columns(4)
                total_milk = sum(c.total_milk_liters for c in dairy_cows)
                all_quality = [q for c in dairy_cows for q in c.monthly_milk_quality]
                avg_fat_herd     = sum(q["fat"] for q in all_quality) / len(all_quality) if all_quality else 0
                avg_protein_herd = sum(q["protein"] for q in all_quality) / len(all_quality) if all_quality else 0
                avg_scc_herd     = sum(q["scc"] for q in all_quality) / len(all_quality) if all_quality else 0
                rejected         = sum(1 for q in all_quality if q["scc"] > 400)
                rejection_pct    = rejected / len(all_quality) * 100 if all_quality else 0

                d1.metric("Total Milk (L)",    f"{total_milk:,.0f}")
                d2.metric("Avg Fat %",         f"{avg_fat_herd:.2f}%")
                d3.metric("Avg Protein %",     f"{avg_protein_herd:.2f}%")
                d4.metric("Milk Rejection %",  f"{rejection_pct:.1f}%")

                # SCC grade distribution pie
                grade_a  = sum(1 for q in all_quality if q["scc"] <= 200)
                grade_b  = sum(1 for q in all_quality if 200 < q["scc"] <= 400)
                rejected_count = sum(1 for q in all_quality if q["scc"] > 400)
                fig_pie_milk = px.pie(
                    values=[grade_a, grade_b, rejected_count],
                    names=["Grade A (≤200)", "Grade B (200-400)", "Rejected (>400)"],
                    title="Milk Quality Grade Distribution",
                    color_discrete_sequence=["green", "orange", "red"]
                )
                st.plotly_chart(fig_pie_milk, use_container_width=True)

            if beef_cows:
                st.subheader("🥩 Beef Production")
                b1, b2, b3 = st.columns(3)
                total_carcass = sum(c.carcass_weight for c in beef_cows)
                avg_dressing  = sum(c.dressing_percentage for c in beef_cows) / len(beef_cows)
                b1.metric("Total Carcass Weight", f"{total_carcass:,.1f} kg")
                b2.metric("Avg Dressing %",       f"{avg_dressing:.1%}")
                b3.metric("Beef Cows",            len(beef_cows))

                # Beef grade pie
                grades = [c.beef_grade for c in beef_cows if c.beef_grade]
                grade_counts = {g: grades.count(g) for g in ["Prime", "Choice", "Select"]}
                fig_pie_beef = px.pie(
                    values=list(grade_counts.values()),
                    names=list(grade_counts.keys()),
                    title="Beef Grade Distribution",
                    color_discrete_sequence=["gold", "silver", "#cd7f32"]
                )
                st.plotly_chart(fig_pie_beef, use_container_width=True)

# ─── Monte Carlo Results ──────────────────────────────────────────────────────
if run_mc:
    with right:
        st.header("🎲 Monte Carlo — Strategy Comparison")
        with st.spinner("Running Monte Carlo simulations..."):
            budget_results  = monte_carlo("budget",  "basic",   n_runs)
            premium_results = monte_carlo("premium", "premium", n_runs)

        st.subheader("Average Profit")
        mc1, mc2 = st.columns(2)
        mc1.metric("Budget Strategy",  f"${budget_results['avg_profit']:,.0f}",
                   f"±${budget_results['std_dev_profit']:,.0f}")
        mc2.metric("Premium Strategy", f"${premium_results['avg_profit']:,.0f}",
                   f"±${premium_results['std_dev_profit']:,.0f}")

        st.subheader("ROI Comparison")
        mc3, mc4 = st.columns(2)
        mc3.metric("Budget ROI",  f"{budget_results['avg_roi']:.1f}%",
                   f"±{budget_results['std_dev_roi']:.1f}%")
        mc4.metric("Premium ROI", f"{premium_results['avg_roi']:.1f}%",
                   f"±{premium_results['std_dev_roi']:.1f}%")

        # Box plot comparison
        fig_mc = go.Figure()
        for name, res, color in [
            ("Budget",  budget_results,  "coral"),
            ("Premium", premium_results, "steelblue")
        ]:
            fig_mc.add_trace(go.Box(
                name=name,
                q1=[res["q1_profit"]],
                median=[res["avg_profit"]],
                q3=[res["q3_profit"]],
                mean=[res["avg_profit"]],
                lowerfence=[res["q1_profit"]  - 1.5 * res["std_dev_profit"]],
                upperfence=[res["q3_profit"]  + 1.5 * res["std_dev_profit"]],
                marker_color=color
            ))
        fig_mc.update_layout(title="Profit Range — Budget vs Premium",
                             yaxis_title="Total Herd Profit ($)")
        st.plotly_chart(fig_mc, use_container_width=True)