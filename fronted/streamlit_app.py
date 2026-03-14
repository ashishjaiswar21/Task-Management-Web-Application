import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None

if "edit_task" not in st.session_state:
    st.session_state.edit_task = None

if "page" not in st.session_state:
    st.session_state.page = "Login"


# ---------------- LOGIN FUNCTION ----------------
def login(username, password):

    data = {
        "username": username,
        "password": password
    }

    res = requests.post(f"{BASE_URL}/user/login", json=data)

    if res.status_code == 200:
        token = res.json()["Token"]
        st.session_state.token = token

        st.session_state.page = "Dashboard"

        st.success("Login Successful ✅")
        st.rerun()
    else:
        st.error("Invalid Credentials ❌")


# ---------------- REGISTER FUNCTION ----------------
def register(name, username, password, email):

    data = {
        "name": name,
        "username": username,
        "password": password,
        "email": email
    }

    res = requests.post(f"{BASE_URL}/user/register", json=data)

    if res.status_code == 201:
        return True
    else:
        st.error("Registration Failed")
        return False


# ---------------- GET TASKS ----------------
def get_tasks():

    headers = {
        "Authorization": f"jwt {st.session_state.token}"
    }

    res = requests.get(
        f"{BASE_URL}/tasks/all_tasks",
        headers=headers
    )

    if res.status_code == 200:
        return res.json()
    else:
        st.error("Failed to fetch tasks")
        return []


# ---------------- CREATE TASK ----------------
def create_task(title, desc):

    headers = {
        "Authorization": f"jwt {st.session_state.token}"
    }

    data = {
        "title": title,
        "desc": desc,
        "is_completed": False
    }

    res = requests.post(
        f"{BASE_URL}/tasks/create",
        json=data,
        headers=headers
    )

    if res.status_code == 201:
        st.success("Task Created Successfully 🚀")
        st.rerun()
    else:
        st.error(res.text)


# ---------------- DELETE TASK ----------------
def delete_task(task_id):

    headers = {
        "Authorization": f"jwt {st.session_state.token}"
    }

    res = requests.delete(
        f"{BASE_URL}/tasks/delete_task/{task_id}",
        headers=headers
    )

    if res.status_code == 204:
        st.session_state.edit_task = None
        st.success("Task Deleted 🗑️")
        st.rerun()
    else:
        st.error(res.text)


# ---------------- UPDATE TASK ----------------
def update_task(task_id, title, desc):
    headers = {
        "Authorization": f"jwt {st.session_state.token}"
    }

    data = {
        "title": title,
        "desc": desc
    }
    res = requests.put(
        f"{BASE_URL}/tasks/update_task/{task_id}",
        json=data,
        headers=headers
    )
    
    if res.status_code in [200, 201]:

        st.success("Task Updated Successfully ✏️")

        st.session_state.edit_task = None

        st.rerun()

    else:
        st.error(res.text)

# ---------------- UI ----------------

st.title("📋 Task Management App")

menu = ["Login", "Register", "Dashboard"]

choice = st.sidebar.selectbox(
    "Menu",
    menu,
    index=menu.index(st.session_state.page)
)

st.session_state.page = choice


# ---------------- LOGIN PAGE ----------------
if choice == "Login":

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login(username, password)


# ---------------- REGISTER PAGE ----------------
elif choice == "Register":

    st.subheader("Register User")

    name = st.text_input("Name", key="name")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    email = st.text_input("Email", key="email")

    if st.button("Register"):

        success = register(name, username, password, email)

        if success:
            st.success("User Registered Successfully 🎉")

            # redirect to login instead of clearing session state
            st.session_state.page = "Login"

            st.rerun()


# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":

    if st.session_state.token is None:
        st.warning("Please login first")
        st.stop()

    st.subheader("Dashboard")

    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.page = "Login"
        st.success("Logged out")
        st.rerun()


    # ---------------- CREATE TASK ----------------
    st.subheader("Create Task")

    title = st.text_input("Task Title", key="task_title")
    desc = st.text_input("Task Description", key="task_desc")

    if st.button("Create Task"):

        create_task(title, desc)

        st.session_state.task_title = ""
        st.session_state.task_desc = ""

        st.rerun()


    # ---------------- SHOW TASKS ----------------
    st.subheader("My Tasks")

    tasks = get_tasks()

    h1, h2, h3, h4 = st.columns([3,3,1,1])
    h1.markdown("**Title**")
    h2.markdown("**Description**")
    h3.markdown("**Delete**")
    h4.markdown("**Update**")

    for task in tasks:

        col1, col2, col3, col4 = st.columns([3,3,1,1])

        col1.markdown(f"**{task['title']}**")
        col2.write(task["desc"])

        if col3.button("Delete", key=f"delete_{task['id']}"):
            delete_task(task["id"])

        if col4.button("Update", key=f"update_{task['id']}"):
            st.session_state.edit_task = task


    # ---------------- UPDATE FORM ----------------
    if st.session_state.edit_task is not None:

        task = st.session_state.edit_task

        if task["id"] not in [t["id"] for t in tasks]:
            st.session_state.edit_task = None
            st.rerun()

        st.subheader("Update Task")

        new_title = st.text_input("Edit Title", value=task["title"])
        new_desc = st.text_input("Edit Description", value=task["desc"])

        if st.button("Save Update"):
            update_task(task["id"], new_title, new_desc)