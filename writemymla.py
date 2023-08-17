import streamlit as st
import openai as ai
import requests
from datetime import date

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

if "formincomplete" not in st.session_state:
    st.session_state.formincomplete = False


# Callback function to make sure the state changes with each button click
def postal_submit():
    st.session_state.postalcomplete = not st.session_state.postalcomplete
    st.session_state.requestgeneration = False


# Callback function to make sure the state changes with each button click
def restart_form():
    st.session_state.postalcomplete = False
    st.session_state.requestgeneration = False


def request_letter_generation():
    if (
        mla_name
        and mla_email
        and user_name
        and described_issue
        and personal_impact
        and resolution
        and support
        and questions
    ):
        st.session_state.requestgeneration = not st.session_state.requestgeneration
        st.session_state.formincomplete = False
    else:
        st.session_state.formincomplete = True


github_link = "https://github.com/brysonbest/writemymla"
st.markdown(
    """
# 📝 Write to your Local Provincial Representative with the help of AI - Canada Only

## Dependening on your Province, your local representative may be called an MLA, MPP, MNA, or MHA. This tool will help you generate a letter to your representative. All you need to do is:

1. Enter your postal code in order to find the local representative.
2. Provide some details about the issue you want to write about.
3. Download your letter to send to your representative! You can choose to then print it off and mail it in, or email it to your representative.

This application uses the OpenAI API, which is currently a paid model. Due to this, there are limited resources, and capacity for this website may be reached quickly. If you're a developer, or a non-profit interested in creating a verison of this website, it is available open source here: [link](%s). You can launch your own version of this website in order to help you support your non-profit and local consituents.
"""
    % github_link
)

openAIAPIlink = "https://openai.com/blog/openai-api"

st.markdown(
    """
Additionally, if you'd like to use this website without limits, you can use your own [openAI API key](%s). You must consent to the use of your key through this portal. For your protection and privacy, the key is not saved, and is sent directly to the openAI API when you request your letter generated.
"""
    % openAIAPIlink
)

useownkeyagree = st.checkbox("I agree, use my own key!")

if useownkeyagree:
    st.write("Great! Your key will be used during this application.")
    personal_key = st.text("Enter key here", help="The key should begin with sk-")

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
            mla = mla
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
                    max_chars=500,
                    help="Max 500 characters.",
                )
                personal_impact = st.text_area(
                    "2. Are you personally connected to or impacted by this issue? Please tell me how you might be personally impacted, or how you are personally connected to this issue.",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                resolution = st.text_area(
                    "3. How do you want this issue to be resolved?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                support = st.text_area(
                    "4. What support, specific help, or action do you need from your MLA?",
                    max_chars=250,
                    help="Max 250 characters.",
                )
                questions = st.text_area(
                    "5. Do you have any questions you would like answered by your MLA? Enter your questions here:",
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


if st.session_state.formincomplete:
    st.warning(
        "You are missing some information. Please check the form and confirm that everything is completed."
    )

# if the form is submitted run the openai completion
if st.session_state.requestgeneration:
    # check for completed form:
    # get the letter from openai
    addressResponse = f"""Address: {mla_address}.""" if isAddress else None
    if useownkeyagree and personal_key and len(personal_key) > 0:
        ai.api_key = personal_key
    try:
        completion = ai.ChatCompletion.create(
            # model="gpt-3.5-turbo-16k",
            model="gpt-3.5-turbo",
            temperature=ai_temp,
            # optimized input to 421 tokens
            # text input at 1 question @ 500 and 5 questions @ 250 characters ~ 1750 characters ~ 300 tokens
            # response of 1000 words should be maximum of 3000 tokens
            aisuggestedmessages=[
                {
                    "role": "user",
                    "content": "Generate a letter to my local political representative regarding my issues and desired solutions.",
                },
                {
                    "role": "system",
                    "content": "You will need to address the letter to the local political representative using the provided information.",
                },
                {
                    "role": "user",
                    "content": f"Local Political Representative Information:\nTitle: {mla}\nName: {mla_name}\nParty: {mla_party}\nEmail: {mla_email}\nPhone: {mla_phone}\nDistrict: {mla_district}\n{addressResponse}",
                },
                {
                    "role": "user",
                    "content": f"Issues I'm Dealing With:\n{described_issue}",
                },
                {
                    "role": "user",
                    "content": f"Sender's Name for the Letter: {user_name}",
                },
                {
                    "role": "user",
                    "content": f"Personal Impact of the Issues: {personal_impact}",
                },
                {
                    "role": "user",
                    "content": f"Proposed Resolution for My Issues: {resolution}",
                },
                {
                    "role": "user",
                    "content": f"Requested Support from Representative: {support}",
                },
                {
                    "role": "user",
                    "content": f"Additional Questions for Representative: {questions}",
                },
                {"role": "user", "content": f"Letter Length Limit: 1000 words"},
                {
                    "role": "user",
                    "content": f"Maintain Professional Tone: Addressing a Political Representative",
                },
                {
                    "role": "user",
                    "content": f"Writer Would Like to Be Contacted About the Issue and Kept Informed",
                },
                {"role": "user", "content": f"Use Writer's Name: {user_name}"},
                {
                    "role": "user",
                    "content": f"Generate a letter to the local political representative emphasizing the issue, its personal impact, and potential solutions.",
                },
            ],
        )
        response_out = completion["choices"][0]["message"]["content"]

        st.markdown(f"""# Your Generated Letter: """)
        st.divider()
        st.write(response_out)
        st.divider()

        # create custom email link with response in body
        email_body = response_out.replace(" ", "%20").replace("\n", "%0A")
        email_date = date.today()
        email_user = user_name.replace(" ", "%20")
        email_mla = mla.replace(" ", "%20")
        email_mla_name = mla_name.replace(" ", "%20")
        email_subject = (
            f"""{email_user}%20-{email_date}%20to%20{mla}%20{email_mla_name}"""
        )
        email_link = f"""mailto:{mla_email}?subject={email_subject}&body={email_body}"""

        st.markdown(
            f"""
                # What to do next:

                ## It is always important to check your letter for any mistakes or misunderstandings. You are also able to make any changes that you want, and add any information that you want.
                ## 1. You can download this letter in multiple formats, with the option to send directly as is to your local representative.
                ## 2. You can send it as an email by clicking on this link: [link](%s). Before sending the email, you should check to confirm that all information in the email is correct.
                """
            % email_link
        )
        # include an option to download a txt file
        st.download_button("Download the letter", response_out)

    except ai.error.RateLimitError as error:
        print(error)
        st.markdown(
            f"""
            # Sorry, there was an error sending your responses to chatGPT for generation, as the service has run out of free generation for this month.
            ### As a non-profit service, there are a limited number of letters that may be generated in a month.
            
            If you are interested in supporting this project, and increasing the number of available generations, please consider making a donation. All proceeds go directly towards the ongoing support of this web application. If you make a donation, it will usually take 24-48 hours before funding is added to this website and letters can continue to be generated.
            
            Otherwise, please try again later. Once donations are exhausted, the limit will reset naturally every month.
            
            If you are a non-profit or developer looking to provide similar support, this application is available as an open-source project, and you can freely deploy a version of it yourself.

            """
        )
    except:
        st.markdown(
            f"""
                # Sorry, there was an error sending your responses to chatGPT for generation.
                ## Please try again.

                """
        )
