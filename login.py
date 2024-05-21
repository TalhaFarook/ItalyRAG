import streamlit as st
from time import sleep

st.set_page_config(page_title="Login", page_icon="🤖")

st.html("""<h1 style="text-align: center;">Welcome</h1>""")

for i in range(3):
    st.text("")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Log in", type="primary"):
    if username in st.secrets["username"] and st.secrets["password"] == password:
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/qna.py")
    else:
        st.error("Incorrect username or password")