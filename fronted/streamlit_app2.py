import streamlit as st 
import requests

# BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "https://task-management-web-application-tbnu.onrender.com"

# ---------------- PAGE CONFIGURATION ----------------
# This sets the browser tab title, icon, and makes the app wide
st.set_page_config(
    page_title="TaskFlow App", 
    page_icon="✨", 
    layout="wide"
)

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "edit_task" not in st.session_state:
    st.session_state.edit_task = None
if "page" not in st.session_state:
    st.session_state.page = "Login"

# ---------------- API FUNCTIONS ----------------
# (Your exact backend logic remains untouched)
def login(username, password):
    data = {"username": username, "password": password}
    res = requests.post(f"{BASE_URL}/user/login", json=data)
    if res.status_code == 200:
        st.session_state.token = res.json()["Token"]
        st.session_state.page = "Dashboard"
        st.success("Login Successful ✅")
        st.rerun()
    else:
        st.error("Invalid Credentials ❌")

def register(name, username, password, email):
    data = {"name": name, "username": username, "password": password, "email": email}
    res = requests.post(f"{BASE_URL}/user/register", json=data)
    if res.status_code == 201:
        return True
    else:
        st.error("Registration Failed")
        return False

def get_tasks():
    headers = {"Authorization": f"jwt {st.session_state.token}"}
    res = requests.get(f"{BASE_URL}/tasks/all_tasks", headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        st.error("Failed to fetch tasks")
        return []

def create_task(title, desc):
    headers = {"Authorization": f"jwt {st.session_state.token}"}
    data = {"title": title, "desc": desc, "is_completed": False}
    res = requests.post(f"{BASE_URL}/tasks/create", json=data, headers=headers)
    if res.status_code == 201:
        st.success("Task Created Successfully 🚀")
        st.rerun()
    else:
        st.error(res.text)

def delete_task(task_id):
    headers = {"Authorization": f"jwt {st.session_state.token}"}
    res = requests.delete(f"{BASE_URL}/tasks/delete_task/{task_id}", headers=headers)
    if res.status_code == 204:
        st.session_state.edit_task = None
        st.success("Task Deleted 🗑️")
        st.rerun()
    else:
        st.error(res.text)

def update_task(task_id, title, desc):
    headers = {"Authorization": f"jwt {st.session_state.token}"}
    data = {"title": title, "desc": desc}
    res = requests.put(f"{BASE_URL}/tasks/update_task/{task_id}", json=data, headers=headers)
    if res.status_code in [200, 201]:
        st.success("Task Updated Successfully ✏️")
        st.session_state.edit_task = None
        st.rerun()
    else:
        st.error(res.text)

# ---------------- SIDEBAR & NAVIGATION ----------------
# Added a visual "Logo" using an emoji and large text
st.sidebar.markdown("# ✨ :violet[TaskFlow]")
st.sidebar.markdown("**Your personal productivity hub**")
st.sidebar.divider()

menu = ["Login", "Register", "Dashboard"]
choice = st.sidebar.radio(
    "📍 Navigate",
    menu,
    index=menu.index(st.session_state.page)
)
st.session_state.page = choice

# ---------------- MAIN UI ROUTING ----------------

st.title("📋 :blue[Task Management App]")
st.divider()

# ---------------- LOGIN PAGE ----------------
if choice == "Login":
    # Using a bordered container to make it look like a clean "card"
    with st.container(border=True):
        st.markdown("### 🔑 :orange[Login to your account]")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("🚀 Login", use_container_width=True):
            login(username, password)

# ---------------- REGISTER PAGE ----------------
elif choice == "Register":
    with st.container(border=True):
        st.markdown("### 📝 :green[Create a New Account]")
        
        col1, col2 = st.columns(2) # Split form into two columns for a cleaner look
        with col1:
            name = st.text_input("Full Name", key="name")
            username = st.text_input("Username", key="username")
        with col2:
            email = st.text_input("Email Address", key="email")
            password = st.text_input("Password", type="password", key="password")

        if st.button("🎉 Register Now", use_container_width=True):
            success = register(name, username, password, email)
            if success:
                st.success("User Registered Successfully! Please Login. 🎉")
                st.session_state.page = "Login"
                st.rerun()

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    if st.session_state.token is None:
        st.warning("⚠️ Please login first to view your dashboard.")
        st.stop()

    # Top Bar: Dashboard Title & Logout Button
    dash_col1, dash_col2 = st.columns([8, 2])
    with dash_col1:
        st.markdown("### 🏠 :violet[My Dashboard]")
    with dash_col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.page = "Login"
            st.success("Logged out successfully.")
            st.rerun()

    # ---------------- CREATE TASK (Inside an Expander) ----------------
    # Hide the create form inside an expander so it doesn't clutter the screen
    with st.expander("➕ **Add a New Task**", expanded=False):
        st.markdown("#### :blue[What do you need to do?]")
        title = st.text_input("Task Title", key="task_title", placeholder="e.g., Buy Groceries")
        desc = st.text_area("Task Description", key="task_desc", placeholder="e.g., Milk, Eggs, Bread...")

        if st.button("Save Task ✅"):
            if title:
                create_task(title, desc)
            else:
                st.error("Title cannot be empty!")

    st.divider()

    # ---------------- SHOW TASKS (Using bordered cards) ----------------
    st.markdown("### 🎯 :green[Active Tasks]")

    tasks = get_tasks()

    if not tasks:
        st.info("No tasks found! Click 'Add a New Task' above to get started. 🎈")

    for task in tasks:
        # Wrap each task in a beautiful bordered container
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([4, 4, 1, 1])

            # Use markdown colors for the task title
            col1.markdown(f"#### :blue[{task['title']}]")
            col2.write(task["desc"])

            # Use emojis for the buttons
            if col3.button("🗑️", key=f"delete_{task['id']}", help="Delete Task"):
                delete_task(task["id"])

            if col4.button("✏️", key=f"update_{task['id']}", help="Edit Task"):
                st.session_state.edit_task = task

    # ---------------- UPDATE FORM ----------------
    if st.session_state.edit_task is not None:
        task = st.session_state.edit_task

        # Safety check if task was deleted
        if task["id"] not in [t["id"] for t in tasks]:
            st.session_state.edit_task = None
            st.rerun()

        st.markdown("---")
        with st.container(border=True):
            st.markdown(f"### ✏️ :orange[Updating Task:] *{task['title']}*")
            
            new_title = st.text_input("Edit Title", value=task["title"])
            new_desc = st.text_area("Edit Description", value=task["desc"])

            upd_col1, upd_col2 = st.columns([1, 1])
            with upd_col1:
                if st.button("💾 Save Changes", use_container_width=True):
                    update_task(task["id"], new_title, new_desc)
            with upd_col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_task = None
                    st.rerun()