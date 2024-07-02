import streamlit as st
import requests
import plotly.graph_objects as go
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# API endpoint
API_BASE_URL = "http://209.38.216.189:8000/api"


def fetch_data(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}")
    return response.json() if response.status_code == 200 else None


st.set_page_config(page_title="Research Data Insights Dashboard", layout="wide")


def fetch_professor_data(professor_id):
    query = """
    query ($id: Int!) {
      professor(professorId: $id) {
        name
        affiliation
        hindex
        totalCitations
        scholarId
        publications {
          title
          year
          numCitations
        }
      }
    }
    """
    variables = {'id': professor_id}
    response = requests.post(f"{API_BASE_URL}/graphql", json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()['data']['professor']
    else:
        return None


def fetch_all_professors():
    query = """
    query {
      allProfessors {
        id
        name
        scholarId
      }
    }
    """
    response = requests.post(f"{API_BASE_URL}/graphql", json={'query': query})
    if response.status_code == 200:
        return response.json()['data']['allProfessors']
    else:
        return None


def main():
    # Header
    # Add a title at the top of the sidebar
    st.sidebar.title("ScholarSync")

    # Add a horizontal line for visual separation
    st.sidebar.markdown("---")

    nav_option = st.sidebar.radio(
        "Navigate to:",
        ("Chat Bot", "Research Insights")
    )

    if nav_option == "Research Insights":
        show_research_insights()
    elif nav_option == "Chat Bot":
        show_chat_bot()


def show_research_insights():
    st.title("This was developed by ScholarSync")
    st.title("Research Data Insights Dashboard")
    st.markdown("Explore comprehensive insights into academic research trends and impact.")

    # Overview Section
    st.header("Overview")

    # Fetch data
    data_size_stats = fetch_data("/statistics/data_size_stats")
    data_coverage_stats = fetch_data("/statistics/data_coverage_stats")

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

    all_professors = fetch_all_professors()

    if all_professors:
        # Create a dropdown to select a professor
        selected_professor = st.selectbox(
            "Select a Professor",
            options=all_professors,
            format_func=lambda x: x['name']
        )

        if selected_professor:
            # Fetch and display the selected professor's data
            professor_data = fetch_professor_data(selected_professor['id'])
            print(f'all the data {professor_data} ||  {selected_professor["id"]}')
            if professor_data:
                st.header(f"Professor: {professor_data['name']}")
                st.write(f"Affiliation: {professor_data['affiliation']}")
                st.write(f"H-index: {professor_data['hindex']}")
                st.write(f"Total Citations: {professor_data['totalCitations']}")

                # Display publications
                st.subheader("Top Publications")
                publications_df = pd.DataFrame(professor_data['publications'])
                st.table(publications_df)

                # Visualize citations per publication
                fig = px.bar(publications_df, x='title', y='numCitations',
                             title='Citations per Publication',
                             labels={'title': 'Publication Title', 'numCitations': 'Number of Citations'})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

                # Visualize publications over time
                pub_by_year = publications_df.groupby('year').size().reset_index(name='count')
                fig = px.line(pub_by_year, x='year', y='count',
                              title='Publications Over Time',
                              labels={'year': 'Year', 'count': 'Number of Publications'})
                st.plotly_chart(fig)
            else:
                st.error("Failed to fetch professor data.")
    else:
        st.error("Failed to fetch the list of professors.")


def chat_with_professor(professor_id, message):
    url = f"{API_BASE_URL}/chat/{professor_id}"
    headers = {
        "Content-Type": "application/json",
    }
    data = {"question": message}

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        return response.json()['answer']
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}"


def show_chat_bot():
    st.title("This was developed by ScholarSync")
    st.write("Chat with an AI assistant about specific professors and their research.")

    # Fetch the list of professors
    all_professors = fetch_all_professors()
    if not all_professors:
        st.error("Failed to fetch the list of professors.")
        return

    # Professor selection
    selected_professor = st.selectbox(
        "Select a Professor to chat about:",
        options=all_professors,
        format_func=lambda x: x['name']
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input(f"Ask about {selected_professor['name']}'s research:"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response with loading spinner
        with st.spinner('Generating response...'):
            response = chat_with_professor(selected_professor['scholarId'], prompt)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

    # Display some example questions
    st.sidebar.header("Example Questions")
    example_questions = [
        f"What are {selected_professor['name']}'s main research areas?",
        f"What is {selected_professor['name']}'s h-index?",
        f"What is {selected_professor['name']}'s most cited paper?",
        f"How many publications does {selected_professor['name']} have?",
        f"What is {selected_professor['name']}'s current research focus?"
    ]
    for question in example_questions:
        if st.sidebar.button(question):
            # Add the example question to the chat input
            st.session_state.messages.append({"role": "user", "content": question})
            st.experimental_rerun()

if __name__ == "__main__":
    main()
