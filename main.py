import streamlit as st
import requests
import plotly.graph_objects as go
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# API endpoint
API_BASE_URL = "http://209.38.216.189:8000/api/statistics"  # Replace with your actual API endpoint


def fetch_data(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}")
    return response.json() if response.status_code == 200 else None


def main():
    # Header
    st.set_page_config(page_title="Research Data Insights Dashboard", layout="wide")
    st.title("Research Data Insights Dashboard")
    st.markdown("Explore comprehensive insights into academic research trends and impact.")

    # Overview Section
    st.header("Overview")

    # Fetch data
    data_size_stats = fetch_data("/data_size_stats")
    data_coverage_stats = fetch_data("/data_coverage_stats")

    if data_size_stats and data_coverage_stats:
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Professors", data_size_stats["total_professors"])
            st.metric("Avg. Publications per Professor", data_size_stats["average_publications_per_professor"])

        with col2:
            st.metric("Total Publications", data_size_stats["total_publications"])
            st.metric("Avg. Citations per Publication", data_size_stats["average_citations_per_publication"])

        with col3:
            st.metric("Total Citations", data_size_stats["total_citations"])

        # Data Coverage Pie Chart
        st.subheader("Data Coverage")
        total_professors = data_size_stats["total_professors"]
        coverage_data = [
            data_coverage_stats["professors_with_publications"] / total_professors,
            data_coverage_stats["professors_with_citations"] / total_professors,
            data_coverage_stats["professors_with_public_access_info"] / total_professors,
            data_coverage_stats["professors_with_yearly_citations"] / total_professors
        ]

        labels = [
            "With Publications",
            "With Citations",
            "With Public Access Info",
            "With Yearly Citations"
        ]

        fig = go.Figure(data=[go.Pie(labels=labels, values=coverage_data, hole=.3)])
        fig.update_layout(title_text="Professor Data Coverage")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Failed to fetch data from the API. Please check your connection and try again.")

        # Top Researchers and Research Trends
        st.header("Research Insights")
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Top Researchers")
            top_professors = fetch_data("/top_professors")
            if top_professors:
                fig = go.Figure(data=[
                    go.Bar(name='Total Citations', x=[p['name'] for p in top_professors],
                           y=[p['total_citations'] for p in top_professors]),
                    go.Bar(name='H-index', x=[p['name'] for p in top_professors],
                           y=[p['h_index'] for p in top_professors])
                ])
                fig.update_layout(barmode='group', title="Top 10 Researchers by Citations and H-index")
                st.plotly_chart(fig, use_container_width=True)

                # Display top researchers in a table with rankings
                st.table(pd.DataFrame(top_professors).reset_index().rename(columns={'index': 'Rank'}))
            else:
                st.error("Failed to fetch top professors data.")

        with col2:
            st.subheader("Research Trends")
            research_interests = fetch_data("/research_interests")
            if research_interests:
                # Bar chart of top research interests
                df = pd.DataFrame(research_interests)
                fig = px.bar(df, x='interest', y='count', title="Top Research Interests")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to fetch research interests data.")

            yearly_growth = fetch_data("/yearly_data_growth")
            if yearly_growth:
                # Line chart of publication growth
                fig = px.line(x=list(yearly_growth.keys()), y=list(yearly_growth.values()),
                              title="Publication Growth Over Years",
                              labels={'x': 'Year', 'y': 'Number of Publications'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to fetch yearly growth data.")

        # Research Accessibility
        st.header("Research Accessibility")
        public_access_ratio = fetch_data("/public_access_ratio")
        if public_access_ratio:
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=public_access_ratio["public_access_ratio"] * 100,
                    title={'text': "Public Access Ratio"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 80], 'color': "gray"},
                               {'range': [80, 100], 'color': "darkgray"}],
                           'threshold': {
                               'line': {'color': "red", 'width': 4},
                               'thickness': 0.75,
                               'value': 90}}))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.write("### Public Access Statistics")
                st.write(f"Total Publications: {public_access_ratio['total_publications']}")
                st.write(f"Publicly Available: {public_access_ratio['available']}")
                st.write(f"Not Publicly Available: {public_access_ratio['not_available']}")
                st.write("### Importance of Open Access")
                st.write(
                    "Open access to research publications is crucial for advancing scientific knowledge and promoting collaboration. It ensures that research findings are accessible to a wider audience, including researchers, policymakers, and the general public.")
        else:
            st.error("Failed to fetch public access ratio data.")


if __name__ == "__main__":
    main()