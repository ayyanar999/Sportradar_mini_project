# Developing streamlit app for the SportRadar mini project
from matplotlib.backend_bases import cursors
import streamlit as st
import psycopg2
from psycopg2.errors import UniqueViolation
import bcrypt
import base64
import time
import binascii
import pandas as pd

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# Function to create a table in the database

def create_table():

    try:
        conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="SportRadar_db",
        user="postgres",
        password="1418"
    )

        cursor = conn.cursor()
    
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
  
        return conn, cursor  # Ensure both are returned
    
    except psycopg2.Error as e:
        st.error(f"Database Connection Failed: {e}")
        return None, None  # Avoid returning an unusable connection

# Function to hash passwords

def hash_password(password: str) -> str:
    # Generate salt and hash the password
    salt = bcrypt.gensalt()  # Salt generation
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password with the salt
    return base64.b64encode(hashed_password).decode('utf-8')  # Return hashed password as a base64 encoded string

# Function to verify passwords
def verify_password(password: str, hashed_password: str) -> bool:
    try:
        # Decode the base64 encoded hashed password back to bytes
        hashed_password_bytes = base64.b64decode(hashed_password.encode('utf-8'))
        # Convert password to bytes for bcrypt
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password_bytes)
    except (binascii.Error, ValueError) as e:
        print(f"Error decoding base64 hashed password: {e}")
        return False

# Example usage
if __name__ == "__main__":
    password = "my_secure_password"
    hashed_password = hash_password(password)
    print(f"Hashed Password: {hashed_password}")

    # Verify the password
    is_valid = verify_password(password, hashed_password)
    print(f"Password is valid: {is_valid}")
def add_styles():
 st.markdown(
 """
    <style>
        /* Background */
        .stApp {
            background-image: url('https://png.pngtree.com/thumb_back/fw800/background/20240403/pngtree-abstract-tennis-ball-racquet-and-strings-image_15647035.jpg');
            background-size: cover;
            background-position: center;
        }
             
    # /* Input Fields */
    # input[type="username"], input[type="password"]{
    #     border-radius: 8px !important;
    #     border: 5px solid #ccc !important;
    #     padding: 6px !important;
    #     color: #333 !important;  /* Change text color to a darker shade */
    #     background-color: #fff !important;  /* Change background color to white */
    # }
                /* Targeting all input fields */
        section[data-testid="stTextInput"] input {
            background-color: #f0f8ff !important; /* Light Blue */
            color: #000 !important; /* Black text */
            border: 2px solid #3498db !important; /* Blue border */
            border-radius: 5px !important;
            padding: 10px !important;
            font-size: 16px !important;
        }

        /* Style when input is focused */
        section[data-testid="stTextInput"] input:focus {
            border-color: #2c3e50 !important; /* Darker Blue */
            background-color: #e6f7ff !important; /* Lighter Blue */
        }

        /* Style for placeholder text */
        ::placeholder {
            color: #95a5a6 !important; /* Grayish */
        }

        /* Buttons */
        .stButton button {
            background: #4CAF50 !important;
            color: white !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            padding: 10px 20px !important;
            width: 100%;
        }
        
    #    /* Sidebar */
    #     .css-1d391kg {
    #         background-color: #f0f0f0 !important;  /* Change sidebar background color */
    #     }
    #     .css-1d391kg .css-1v3fvcr {
    #         color: #333 !important;  /* Change sidebar text color */
    #     }
    #     .css-1d391kg .css-1v3fvcr:hover {
    #         color: #4CAF50 !important;  /* Change sidebar text hover color */
    #     }

    #     /* Sidebar Header */
    #     .css-1d391kg .css-1v3fvcr h1 {
    #         color: red !important;  /* Change sidebar header text color */
    #     }
        
    </style>
    """,
    unsafe_allow_html=True
)

def signup():
    add_styles()
    # st.markdown('<h2 style="color:#1E90FF;">📝 Create an Account</h2>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:red; margin-top: 20px;">👤 Username </h3>', unsafe_allow_html=True)
    new_user = st.text_input("", key="signup_user", placeholder="Enter your username", help="Enter your username")
    st.markdown('<h3 style="color:red;">🔒 Password </h3>', unsafe_allow_html=True)
    new_pass = st.text_input("", type="password", key="signup_pass", placeholder="Enter your password", help="Enter your password")

    if st.button("Create an Account", key="signup_submit"):
        conn, cursor = create_table()
        if conn is None or cursor is None:
            return  # Exit if connection or cursor is invalid

        # Validate input length
        if len(new_user) > 100:
            st.error("⚠️ Username must be 100 characters or less.")
            return
        if len(new_pass) > 100:
            st.error("⚠️ Password must be 100 characters or less.")
            return
        
        if new_user and new_pass:
            try:
                hashed_pass = hash_password(new_pass)
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_user, hashed_pass))
                conn.commit()
                st.success("✅ Account created successfully! Please login.")
            except UniqueViolation:
                st.error("⚠️ Username already exists! Try a different one.")
                conn.rollback()  # Rollback the transaction on error
            finally:
                cursor.close()
                conn.close()
        else:
            st.warning("⚠️ Please enter a username and password.")

    st.markdown("</div>", unsafe_allow_html=True)

# Login Page
def login():
    add_styles()
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:red;">👤 Username </h3>', unsafe_allow_html=True)
    username = st.text_input("", key="login_user", placeholder="Enter your username", help="Enter your username")
    st.markdown('<h3 style="color:red;">🔒 Password </h3>', unsafe_allow_html=True)
    password = st.text_input("", type="password", key="login_pass", placeholder="Enter your password", help="Enter your password")
    
    if st.button("Go",key="login_submit"):
        conn, cursor = create_table()

        if conn is None or cursor is None:
            return  # Exit if connection or cursor is invalid

        try:
            cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
            result = cursor.fetchone()

            if result and verify_password(password, result[0]):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.1)
                    progress.progress(i + 1)
                st.balloons()
                st.success(f"🎉 Welcome {username}!") 
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")      
        
        finally:
            cursor.close()
            conn.close()

    st.markdown("</div>", unsafe_allow_html=True)

# Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.success("👋 Logged out successfully!")

def fetch_summary():

    conn, cursor = create_table()

#   Dashboard ui

    # st.set_page_config(page_title="🏆 Competitor Dashboard", layout="wide")

    if conn is None or cursor is None:
        return None

    try:
        # Total number of competitors
        cursor.execute("SELECT COUNT(*) FROM competitors")
        total_competitors = cursor.fetchone()[0]

        # Number of countries represented
        cursor.execute("SELECT COUNT(DISTINCT country) FROM competitors")
        total_countries = cursor.fetchone()[0]

        # Highest points scored by competitor
        cursor.execute("""
            SELECT DISTINCT F.name, E.points
            FROM Rankings E JOIN Competitors F
            ON E.competitor_id = F.competitor_id
            WHERE E.points = (SELECT MAX(points) FROM rankings)
        """)
                        
        highest_points = cursor.fetchone()[0]

        return total_competitors, total_countries, highest_points 
    
    except Exception as e:
        st.error(f"⚠️ Database Query Failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Fetch Data

def show_dashboard():

    st.title("🏆 Competitor Dashboard")
    summary = fetch_summary()

    if summary:
        total_competitors, total_countries, highest_points = summary

        #  Display Summary Statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="👥 Total Competitors", value=total_competitors)

        with col2:
            st.metric(label="🌍 Countries Represented", value=total_countries)

        with col3:
            st.metric(label="🔥 Highest Points Scored", value=highest_points)

        # #Show Competitors Data
        # st.subheader("📋 Competitor Data")
        # conn, cursor= create_table()
        # if conn:
        #     df = pd.read_sql("SELECT * FROM competitors LIMIT 20;", conn)  # Show top 20 competitors
        #     df = df.style.set_properties(**{
        #         'background-color': '#f0f2f6', 
        #         'color': 'black', 
        #         'border': '1px solid #ddd'
        #     }).highlight_max(subset=["points"], color="yellow")  # Highlight max points
        #     st.dataframe(df, use_container_width=True, height=400) 
        #     conn.close()
        #     cursor.close()

# 📌 Fetch Competitor Data
def fetch_competitors():
    conn, cursor = create_table()
    if conn:
        try:
            query = """
                SELECT DISTINCT F.competitor_id, F.name as competitor_name, E.rank, E.points,F.country,E.movement
                FROM Rankings E JOIN Competitors F
                ON E.competitor_id = F.competitor_id
                ORDER BY E.rank, E.points DESC
            """
            df = pd.read_sql(query, conn)
            conn.close()
            cursor.close()
            return df
        except Exception as e:
            st.error(f"⚠️ Failed to load data: {e}")
            return pd.DataFrame()  # Return empty dataframe
    return pd.DataFrame()

# Dashboard with Search & Filters

def show_dashboard_filter():

    # Fetch competitor data
    df = fetch_competitors()

    if df.empty:
        st.warning("No competitor data available.")
        return

    # Search & Filter Sidebar
    st.sidebar.header("🔍 Search & Filter Competitors")

    # Search by Name
    search_query = st.sidebar.text_input("🔎 Search Competitor by Name")

    # Filter by Country
    country_filter = st.sidebar.selectbox("🌍 Filter by Country", ["All"] + sorted(df["country"].unique()))

    # Filter by Rank (Index)
    rank_range = st.sidebar.slider("🏅 Filter by Rank Range", 1, len(df), (1, len(df)))

    # Filter by Points
    min_points, max_points = int(df["points"].min()), int(df["points"].max())
    points_range = st.sidebar.slider("🔥 Points Threshold", min_points, max_points, (min_points, max_points))

    # Apply Filters
    filtered_df = df.copy()

    # Search Competitor Name
    if search_query:
        filtered_df = filtered_df[filtered_df["competitor_name"].str.contains(search_query, case=False, na=False)]

    # Filter by Country
    if country_filter != "All":
        filtered_df = filtered_df[filtered_df["country"] == country_filter]

    # Filter by Rank (Index)
    filtered_df = filtered_df.iloc[rank_range[0] - 1 : rank_range[1]]

    # Filter by Points
    filtered_df = filtered_df[(filtered_df["points"] >= points_range[0]) & (filtered_df["points"] <= points_range[1])]
    
    # Sorting
    sort_by = st.sidebar.selectbox("Sort by", ["Rank", "Points"])
    sort_order = st.sidebar.selectbox("Sort order", ["Ascending", "Descending"])

    if sort_by == "Rank":
     filtered_df = filtered_df.sort_values(by="rank", ascending=(sort_order == "Ascending"))
    elif sort_by == "Points":
     filtered_df = filtered_df.sort_values(by="points", ascending=(sort_order == "Ascending"))

    # Display Data
    st.subheader("📋 Filtered Competitor Data")
    st.markdown(
    """
    <style>
    .streamlit-container {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, height=500)

# Function to fetch country statistics from PostgreSQL
def fetch_country_stats():
    conn, cursor = create_table()
    query = """
        SELECT DISTINCT  COUNT(F.name) as total_competitor,  AVG(E.points) AS average_points,F.country
                FROM Rankings E JOIN Competitors F
                ON E.competitor_id = F.competitor_id
                GROUP BY F.country
                ORDER BY total_competitor DESC
    """
    
    # Execute the query and load the result into a DataFrame
    df = pd.read_sql(query, conn)
    conn.close()
    cursor.close()

    return df

def display_country_stats():

    # Streamlit UI

    st.title("🌍 Country Competitor Statistics")

    # Fetch data

    df = fetch_country_stats()

    # Display data in tabs

    tab1, tab2, tab3 = st.tabs(["📊 Country-wise Competitor Stats","📊Total Competitors", "📊Average Points"])

    with tab1:
         st.subheader("📊 Country-wise Competitor Stats")
         st.write("Here is the list of countries with the total number of competitors and their average points:")
         st.dataframe(df,use_container_width=True)  # Display as a DataFrame

    with tab2:
        st.subheader("📊 Total Competitors by Country")
        st.bar_chart(df.set_index('country')['total_competitor'],use_container_width=True)

    with tab3:
        st.subheader("📊 Average Points by Country")
        st.bar_chart(df.set_index('country')['average_points'],use_container_width=True)

# Function to fetch competitors with the highest points

def fetch_top_points_competitors():

    conn,cursor = create_table()

    query = """
        SELECT F.name, E.rank, E.points
        FROM Rankings E
        JOIN Competitors F ON E.competitor_id = F.competitor_id
        ORDER BY E.points DESC
        LIMIT 10;  -- Adjust the number of top competitors as needed
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    cursor.close()

    return df

# Function to fetch the top-ranked competitors
def fetch_top_ranked_competitors():
    conn,cursor = create_table()
    query = """
        SELECT F.name, E.rank, E.points
        FROM Rankings E
        JOIN Competitors F ON E.competitor_id = F.competitor_id
        ORDER BY E.rank ASC
        LIMIT 10;  -- Adjust the number of top competitors as needed
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    cursor.close()

    return df

def display_top_points_competitors():

    # Streamlit UI
    st.title("🏆 Competitor Leaderboards")
        # Fetch the data
    top_ranked_df = fetch_top_ranked_competitors()
    top_points_df = fetch_top_points_competitors()
        
    # Display top-ranked competitors
    st.subheader("🥇 Top-ranked Competitors")
    st.dataframe(top_ranked_df)  # Display as DataFrame
        
    # Display competitors with highest points
    st.subheader("💯 Competitors with the Highest Points")
    st.dataframe(top_points_df)  # Display as DataFrame

# Main Function
def main():
    add_styles()

    # Initialize session state variables if not already set
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "page" not in st.session_state:
        st.session_state["page"] = None  # Default is None

    if st.session_state["logged_in"]:
        # Sidebar navigation after login
        st.sidebar.header("📊 Dashboard Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Country Stats", "Top Ranked Competitor"])
        st.sidebar.success(f"✅ Logged in as {st.session_state['username']}")

        # Add logout button in the right corner of the main page
        col3 = st.columns([2, 2, 2])[2]  # Adjust ratio to push button to the right

        with col3:
            if st.button("🚪 Logout", key="logout_button"):
              logout()
              st.rerun()  # Rerun immediately after logout

        # Page navigation logic
        if page == "Dashboard":
            show_dashboard()
            show_dashboard_filter()
        elif page == "Country Stats":
            display_country_stats()
        elif page == "Top Ranked Competitor":
            display_top_points_competitors()

    else:
        # Centered Login and Signup Section
        st.markdown("<h2 style='text-align: center; color: #1E90FF;'>🎾 Welcome to Tennis Rankings Explorer </h2>", 
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #3498db;'>Please login or sign up to continue.</p>", 
                    unsafe_allow_html=True)

        col2 = st.columns([1, 1, 1])[1]
        with col2:
            # Show login/signup buttons only when no page is selected
            # if st.session_state["page"] is None:
           if st.button("🔑 Login Now", key="login_main"):
                    st.session_state["page"] = "login"
                    st.rerun()  # Rerun immediately

           elif st.button("📝 Signup Now", key="signup_main"):
                    st.session_state["page"] = "signup"
                    # st.rerun()  # Rerun immediately

        # Page redirection after rerun
        if st.session_state["page"] == "login":
           login()  # Call login function directly
        elif st.session_state["page"] == "signup":
           signup()  # Call signup function directly

if __name__ == "__main__":
    main()





        
