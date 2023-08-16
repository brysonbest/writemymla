import streamlit as st
import os
import openai as ai
from PyPDF2 import PdfReader
import requests

ai.api_key = st.secrets["openai_key"]
# ai.api_key = "sk-xxx"
# how creative the AI should be
ai_temp = 0.99

# To fix form state on change.

# Initialize some state for showing postal
if "postalcomplete" not in st.session_state:
    st.session_state.postalcomplete = False

if "requestgeneration" not in st.session_state:
    st.session_state.requestgeneration = False


# Callback function to make sure the state changes with each button click
def postal_submit():
    st.session_state.postalcomplete = not st.session_state.postalcomplete
    st.session_state.requestgeneration = False


# Callback function to make sure the state changes with each button click
def restart_form():
    st.session_state.postalcomplete = False
    st.session_state.requestgeneration = False


def request_letter_generation():
    st.session_state.requestgeneration = not st.session_state.requestgeneration


st.markdown(
    """
# 📝 Write to your Local Provincial Representative with the help of AI

## Dependening on your Province, your local representative may be called an MLA, MPP, MNA, or MHA. This tool will help you generate a letter to your representative. All you need to do is:

1. Enter your postal code in order to find the local representative.
2. Provide some details about the issue you want to write about.
3. Download your letter to send to your representative! You can choose to then print it off and mail it in, or email it to your representative.
"""
)

with st.form("postal_form"):
    # other inputs
    postal = st.text_input(
        "Please enter your postal code to find your local representative."
    )
    postal.replace(" ", "")
    # submit button
    submittedPostal = st.form_submit_button(
        "Find My Representative",
        on_click=postal_submit,
        disabled=st.session_state.postalcomplete,
    )


submitted = False
mla_form_options = False

if st.session_state.postalcomplete:
    st.button("Restart", on_click=restart_form)

    # if submittedPostal:
    # get the MLA
    # attempt geocode first, fallback to postal
    geocodeURL = f"https://geocoder.ca/?locate={postal}&geoit=XML&json=1"
    try:
        georesponse = requests.get(geocodeURL)
        georesponse.raise_for_status()
        data = georesponse.json()
        lat = data["latt"]
        long = data["longt"]
        url = f"https://represent.opennorth.ca/representatives/?point={lat}%2C{long}"
        geocoded = True
    except:
        url = f"https://represent.opennorth.ca/postcodes/{postal}/"
        geocoded = False

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if geocoded:
            dataLocation = "objects"
        else:
            dataLocation = "representatives_centroid"
        if len(data[dataLocation]) != 0:
            filtered_for_mla = []
            for item in data[dataLocation]:
                if (
                    "MLA" in item["elected_office"]
                    or "MHA" in item["elected_office"]
                    or "MPP" in item["elected_office"]
                    or "MNA" in item["elected_office"]
                ):
                    filtered_for_mla.append(item)
            mla = filtered_for_mla[0]["elected_office"].upper()
            mla_name = filtered_for_mla[0]["name"]
            mla_party = filtered_for_mla[0]["party_name"]
            mla_email = filtered_for_mla[0]["email"]
            mla_phone = filtered_for_mla[0]["offices"][0]["tel"]
            mla_district = filtered_for_mla[0]["district_name"]
            mla_address = filtered_for_mla[0]["offices"][0].get("postal")
            if mla_address is None:
                mla_address = "Address not found"
                isAddress = False
            else:
                mla_address = mla_address.replace("\n", " ")
                mla_address = mla_address.replace("\r", " ")
                mla_address = mla_address.replace("\t", " ")
                mla_address = mla_address.replace("  ", " ")
                isAddress = True

            if mla_email is None:
                mla_email = "No email found"

            st.markdown(
                f"""
    # 📝 Your local official is: {mla_name}, for the district of {mla_district}!

    ## If your concern is urgent, you can contact them at {mla_email} or {mla_phone}.
    
    If this information looks correct, fantastic! If not, you can choose to enter your postal code again, or you can manually enter your representatives's information.
    """
            )

            st.write("You can edit these details if you'd like to change them.")
            mla_name = st.text_input(f"""{mla} Name""", value=mla_name)
            mla_party = st.text_input(f"""{mla} Party""", value=mla_party)
            mla_email = st.text_input(f"""{mla} Email""", value=mla_email)
            mla_phone = st.text_input(f"""{mla} Phone""", value=mla_phone)
            mla_district = st.text_input(f"""{mla} District""", value=mla_district)
            mla_address = st.text_input(f"""{mla} Address""", value=mla_address)

            with st.form("input_form"):
                # other inputs
                user_name = st.text_input(
                    "Please enter your name as you'd like it to appear in the letter."
                )
                described_issue = st.text_area(
                    "1. What is your Issue? Why are you writing your MLA?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                issue = st.text_area(
                    "2. Why is this issue concerning to you?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                personal_impact = st.text_area(
                    "3. Are you personally connected to or impacted by this issue? Please tell me how you might be personally impacted, or how you are personally connected to this issue.",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                resolution = st.text_area(
                    "4. How do you want this issue to be resolved?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                support = st.text_area(
                    "5. What support, specific help, or action do you need from your MLA?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                questions = st.text_area(
                    "6. Do you have any questions you would like answered by your MLA? Enter your questions here:",
                    max_chars=250,
                    help="Max 250 characters.",
                )

                # submit button
                submitted = st.form_submit_button(
                    "Generate MLA Letter",
                    on_click=request_letter_generation,
                    disabled=st.session_state.requestgeneration,
                )

    except requests.exceptions.HTTPError as error:
        st.markdown(
            f"""
    # Sorry, there was an error searching for your local representative! 

    ## Please confirm the accuracy of your postal code and try again.

    """
        )
        print(error)


# if the form is submitted run the openai completion
if st.session_state.requestgeneration:
    # get the letter from openai
    addressResponse = f"""Their address is: {mla_address}.""" if isAddress else None
    completion = ai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-3.5-turbo",
        temperature=ai_temp,
        messages=[
            {
                "role": "user",
                "content": f"You will need to generate a letter to my local political representative based on a description of my issues, and how I would like them addressed.",
            },
            {
                "role": "user",
                "content": f"Here is the information of the local political representative that I am writing to: Their title is: {mla}. Their name is: {mla_name}. Their party is: {mla_party}. Their email is: {mla_email}. Their phone number is: {mla_phone}. Their district is: {mla_district}. {addressResponse} Use this information to address the letter and content to the correct person.",
            },
            {
                "role": "user",
                "content": f"The issues that I am dealing with are: {described_issue}",
            },
            {
                "role": "user",
                "content": f"The sender's name to include on the letter: {user_name}",
            },
            {
                "role": "user",
                "content": f"Here is how this issue is personally connected to myself and how it personally impacts me: {personal_impact}",
            },
            {
                "role": "user",
                "content": f"Here is my proposed resolution for my issues: {resolution}",
            },
            {
                "role": "user",
                "content": f"Here is how I would like my representative to help or support me: {support}",
            },
            {
                "role": "user",
                "content": f"These are additional related questions that I have for my representative: {questions}",
            },
            {
                "role": "user",
                "content": f"The letter should not be longer than 2500 words.",
            },
            {
                "role": "user",
                "content": f""" 
        In the letter, keep the content professional. You are writing to a political representative and trying to bring attention to your specific issues and concerns.
        """,
            },
            # Maybe include additional segments on specific structure of the letter
            #     {
            #         "role": "user",
            #         "content": f"""
            # In the first paragraph introduce the writer and indicate the issue and how the writer is personally connected to the issue.
            # """,
            #     },
            {
                "role": "user",
                "content": f""" 
        Note that the writer would like to be contacted about this issue, and would like to be kept aware of any updates towards resolving their issue.
            """,
            },
            {
                "role": "user",
                "content": f"Use {user_name} as the writer of the letter",
            },
            {
                "role": "user",
                "content": f"Generate a specific letter to my local political representative based on the information above. Prioritize the issue and the personal impacts and connections of that issue. Generate the response and include appropriate spacing between the paragraph text.",
            },
        ],
    )

    response_out = completion["choices"][0]["message"]["content"]
    st.write(response_out)

    # include an option to download a txt file
    st.download_button("Download the letter", response_out)
