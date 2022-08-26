import streamlit as st


def main():
    st.title("Home")
    st.subheader("Bathymetry Tools")
    st.write("Please select a tool from the sidebar.")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
