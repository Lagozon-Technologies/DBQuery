# **********************************************************************************************#
# File name: main.py
# Created by: Krushna B.
# Creation Date: 25-Jun-2024
# Application Name: DBQUERY_NEW.AI
#
# Change Details:
# Version No:     Date:        Changed by     Changes Done         
# 01             25-Jun-2024   Krushna B.     Initial Creation
# 02             04-Jul-2024   Krushna B.     Added logic for data visualization 
# 03             23-Jul-2024   Krushna B.     Added logic for capturing user's feedback
# 04             25-Jul-2024   Krushna B.     Added new departments - Insurance and Legal
# 05             13-Aug-2024   Krushna B.     Added logic for Speech to Text
# 06             20-Aug-2024   Krushna B.     Changed Manufacturing to Inventory and added more tables inside it           
#**********************************************************************************************#
import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text
from whisper_stt import whisper_stt
from table_details import *
#from openai import OpenAI
import configure 
from configure import gauge_config
from PIL import Image
import plotly.graph_objects as go
img = Image.open(r"images.png")
st.set_page_config(page_title="DBQuery.AI", page_icon=img)
from newlangchain_utils import *
import plotly.express as px
from io import BytesIO
# with st.sidebar:
#     #st.image("img.jpg", width=110)
#     st.title("DBQuery.AI")
col1, col2 = st.columns([1, 5])
with col1:
    st.image("img.jpg", width=110)
with col2:
    st.title("DBQuery : Generative AI assistant to your Database")
# Set OpenAI API key from Streamlit secrets
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# DATABASES = os.getenv("databases").split(',')
# MODELS = os.getenv("models").split(',')
#SUBJECT_AREAS = os.getenv("subject_areas").split(',')

if "selected_model" not in st.session_state:
    st.session_state.selected_model = configure.models[0]
    
if "selected_database" not in st.session_state:
    st.session_state.selected_database = configure.database[0]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "connection_status" not in st.session_state:
    st.session_state.connection_status = False
if "response" not in st.session_state:
        st.session_state.response = None
if "chosen_tables" not in st.session_state:
        st.session_state.chosen_tables = []
if "tables_data" not in st.session_state:
        st.session_state.tables_data = {}
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

if "generated_query" not in st.session_state:
    st.session_state.generated_query = ""
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Setup'
# if "selected_subject" not in st.session_state:
#     st.session_state.selected_subject = SUBJECT_AREAS[0]
# if "previous_subject" not in st.session_state:
#     st.session_state.previous_subject = ""

# Function to create a circular gauge chart
def create_circular_gauge_chart(title, value, min_val, max_val, color, subtext):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 9, 'color': 'black'}, },
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.6},
            'bgcolor': "white",
            'borderwidth': 0,
            'bordercolor': "white",
            
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        },
        number={'suffix': subtext, 'font': {'size': 10, 'color': 'gray'}}
    ))
    fig.update_layout(width=200, height=200, margin=dict(t=0, b=0, l=0, r=0))
    return fig

# Sidebar with small circular gauge charts
with st.sidebar:
    st.title("Evaluation Dashboard")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    for i, (title, config) in enumerate(gauge_config.items()):
        with eval(f'col{i + 1}'):  # Dynamically select the column
            st.plotly_chart(create_circular_gauge_chart(title, config["value"], 0, 100, config["color"], ""), use_container_width=True)
# Setup and Query Tabs
tab1, tab2 = st.tabs(["Setup", "Query"])

with tab1:
    st.session_state.active_tab = 'Setup'
    st.header("Setup")
    
    #database = ['PostgreSQL', 'Oracle', 'SQLite', 'MySQL']
    st.session_state.selected_database = st.selectbox("Select a Database", configure.database, index=configure.database.index(st.session_state.selected_database))
    #models = ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o']
    st.session_state.selected_model = st.selectbox("Select a Model",configure.models, index=configure.models.index(st.session_state.selected_model))
    if st.button("Connect"):
        st.session_state.connection_status = True
        st.success("Connection established")
        
with tab2:
    st.session_state.active_tab = 'Query'
    st.header("Query")
    #subject_areas = ['Employee', 'Customer Support', 'Medical', 'Manufacturing', 'Sales', 'Finance']
    if "selected_subject" not in st.session_state:
       st.session_state.selected_subject = configure.subject_areas[0]
    if "previous_subject" not in st.session_state:
       st.session_state.previous_subject = ""
    configure.selected_subject = st.selectbox("Select a Subject Area", configure.subject_areas, index=configure.subject_areas.index(st.session_state.selected_subject))

    
   
    if configure.selected_subject != st.session_state.previous_subject:
        
      st.session_state.messages = []
      st.session_state.response = None
      #st.session_state.tables_data = {}
      st.session_state.selected_subject = configure.selected_subject
      table_details = get_table_details()
    # Display the selected subject area
    tables = [line.split("Table Name:")[1].strip() for line in table_details.split("\n") if "Table Name:" in line]

    st.write(f"_You selected: {st.session_state.selected_subject}_")
    st.write(f"_Number of tables in {st.session_state.selected_subject}: {len(tables)}_")
    selected_table = st.selectbox("_Tables in this Subject Area :_", tables)    
    if st.button("Clear"):
        st.session_state.clear()
        st.experimental_rerun()
    def plot_chart(data_df, x_axis, y_axis, chart_type):
      if chart_type == "Line Chart":
        fig = px.line(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Bar Chart":
        fig = px.bar(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Scatter Plot":
        fig = px.scatter(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Pie Chart":
        fig = px.pie(data_df, names=x_axis, values=y_axis)
      elif chart_type == "Histogram":
        fig = px.histogram(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Box Plot":
        fig = px.box(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Heatmap":
        fig = px.density_heatmap(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Violin Plot":
        fig = px.violin(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Area Chart":
        fig = px.area(data_df, x=x_axis, y=y_axis)
      elif chart_type == "Funnel Chart":
        fig = px.funnel(data_df, x=x_axis, y=y_axis)
      else:
        st.write("Unsupported chart type selected")
        return
    
      st.plotly_chart(fig)
    def download_as_excel(data, filename="data.xlsx"):
       output = BytesIO()
       with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
          data.to_excel(writer, index=False, sheet_name='Sheet1')
       output.seek(0)  
       return output
    def voting_interface(table_name):
        votes = load_votes(table_name)

        col1, col2, col3, col4, col5, col6= st.columns(6)

        with col1:
            if st.button(f"👍{votes['upvotes']}"):
                votes["upvotes"] += 1
                save_votes(table_name, votes)
                insert_feedback(configure.selected_subject, st.session_state.user_prompt, st.session_state.generated_query, table_name, data, "like")
                st.experimental_rerun()

        # with col2:
        #     st.write(f"Upvotes: {votes['upvotes']}")
        #     st.write(f"Downvotes: {votes['downvotes']}")

        with col2:
            if st.button(f"👎 {votes['downvotes']}"):
                votes["downvotes"] += 1
                save_votes(table_name, votes)
                insert_feedback(configure.selected_subject, st.session_state.user_prompt, st.session_state.generated_query, table_name, data, "dislike")
                st.experimental_rerun()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
       with st.chat_message(message["role"]):
           st.markdown(message["content"])
    selected_subject_input = "What you would like to know about : Subject area - ", configure.selected_subject, "?" 
    print(' '.join(selected_subject_input))
    selected_subject_final = ' '.join(selected_subject_input)
    st.write("Click start recording to speak:")
    text = whisper_stt(openai_api_key=OPENAI_API_KEY, language='en')    

    if prompt := st.chat_input(selected_subject_final):
        #st.session_state.user_prompt = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.user_prompt = prompt
        with st.spinner("Generating response..."):
            response, chosen_tables, tables_data, agent_executor = invoke_chain(prompt, st.session_state.messages, st.session_state.selected_model)
            if isinstance(response, str):
                st.session_state.generated_query = ""  # Or handle it accordingly
            else:
                st.session_state.chosen_tables = chosen_tables
                st.session_state.tables_data = tables_data
                #st.session_state.user_prompt = prompt
                st.session_state.generated_query = response["query"]
            # x=response.split(";")[0]+";"
            # y=response.split(";")[1]
            # st.markdown(x)
            #st.markdown(response["query"])
            st.markdown(f"*Relevant Tables:* {', '.join(chosen_tables)}")
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif prompt := text:
        #st.session_state.user_prompt = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.user_prompt = prompt
        with st.spinner("Generating response..."):
            response, chosen_tables, tables_data, agent_executor = invoke_chain(prompt, st.session_state.messages, st.session_state.selected_model)
            if isinstance(response, str):
                st.session_state.generated_query = ""  # Or handle it accordingly
            else:
                st.session_state.chosen_tables = chosen_tables
                st.session_state.tables_data = tables_data
                #st.session_state.user_prompt = prompt
                st.session_state.generated_query = response["query"]

            # x=response.split(";")[0]+";"
            # y=response.split(";")[1]
            # st.markdown(x)
            #st.markdown(response["query"])
            st.markdown(f"*Relevant Tables:* {', '.join(chosen_tables)}")
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
       #st.error("The input prompt is empty. Please enter a valid question.")
       pass


        
    if "response" in st.session_state and "tables_data" in st.session_state:
            st.markdown(st.session_state.user_prompt)
            st.markdown(st.session_state.generated_query)
            for table, data in st.session_state.tables_data.items():
                    st.markdown(f"*Data from {table}:*")
                    st.dataframe(data)
                    st.markdown("**Was this response helpful?**")
                    voting_interface(table)

                    if not data.empty:
                        x_axis = st.selectbox(f"Select X-axis for {table}", data.columns, key=f"x_axis_{table}")
                        y_axis = st.selectbox(f"Select Y-axis for {table}", data.columns, key=f"y_axis_{table}")
                        chart_type = st.selectbox(
                            f"Select Chart Type for {table}", 
                            ["Line Chart", "Bar Chart", "Scatter Plot", "Pie Chart", "Histogram", 
                            "Box Plot", "Heatmap", "Violin Plot", "Area Chart", "Funnel Chart"], 
                            key=f"chart_type_{table}"
                        )

                        if st.button(f"Generate Chart for {table}", key=f"generate_chart_{table}"):
                            plot_chart(data, x_axis, y_axis, chart_type)

                    excel_data = download_as_excel(data)
                    st.download_button(
                            label="Download as Excel",
                            data=excel_data,
                            file_name=f"{table}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    def load_votes(table):
                        # Add your database connection and querying logic here to fetch the votes
                        # For demonstration, return a dictionary with upvotes and downvotes
                        return {"upvotes": 0, "downvotes": 0}

                    # Function to save votes to the database
                    def save_votes(table, votes):
                        # Add your database connection and updating logic here to save the votes
                        pass

