import json
import os
from pprint import pprint

private_key_id = os.getenv('private_key_id')
private_key = os.getenv('private_key')
client_email = os.getenv('client_email')
client_id = os.getenv('client_id')
auth_uri = os.getenv('auth_uri')
token_uri = os.getenv('token_uri')
auth_provider_x509_cert_url = os.getenv('auth_provider_x509_cert_url')
client_x509_cert_url = os.getenv('client_x509_cert_url')
universe_domain =  os.getenv("universe_domain")

service_account_info = {
    "type": "service_account",
    "project_id": os.getenv('project_id'),
    "private_key_id": private_key_id,
    "private_key": private_key,
    "client_email": client_email,
    "client_id": client_id,
    "auth_uri": auth_uri,
    "token_uri": token_uri,
    "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    "client_x509_cert_url": client_x509_cert_url,
    "universe_domain": universe_domain
}
# pprint(service_account_info)

with open('service_account.json', 'w') as f:
    json.dump(service_account_info, f, indent=2)

token = os.getenv('token')
refresh_token = os.getenv('refresh_token')
token_uri = os.getenv('token_uri')
client_id_mail = os.getenv('client_id_mail')
client_secret = os.getenv('client_secret')
scopes = os.getenv('scopes')
universe_domain = os.getenv('universe_domain')
account = os.getenv('account')
expiry = os.getenv('expiry')

token_info = {
    "token": token,
    "refresh_token": refresh_token,
    "token_uri": token_uri,
    "client_id": client_id_mail,
    "client_secret": client_secret,
    "scopes": ["https://www.googleapis.com/auth/gmail.send"],
    "universe_domain": universe_domain,
    "account": account,
    "expiry": expiry
}
# pprint(token_info)

with open('token.json', 'w') as f:
    json.dump(token_info, f)


import streamlit as st
from agents import BlogAgent, LinkedinAgent, TwitterAgent, EmailAgent
from tools import youtube_transcript_loader
from utils import twitter_tweet
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

st.title("YouTube video Manager")

# Inputs for the topic and URL
topic = st.text_input("Enter the topic")
url = st.text_input("Enter the URL")
to_mail = st.text_input("Enter your Email")

options = st.multiselect("Select what to generate", ["LinkedIn Post", "Twitter Tweet"])

if st.button("Submit"):
    if topic and url and to_mail and options:
        llm = ChatOpenAI(model='gpt-4o-mini')
        
        with st.spinner("Researching content..."):
            if 'youtube' in url:
                print('extracting youtube transcript')
                summarized_content = youtube_transcript_loader(url)
                # st.text_area("summarixedsummarized_content)

        with st.spinner("Creating Blog..."):
            with st.expander("Blog"):
                blog_agent = BlogAgent(llm, topic, url, summarized_content)
                blog_content, blog_md, imgs, blog_status = blog_agent.generate_blog()
                st.markdown(blog_status)

        if "LinkedIn Post" in options:
            with st.spinner("Creating LinkedIn Post..."):
                with st.expander("LinkedIn Post"):
                    linkedin_agent = LinkedinAgent(llm, topic, url, blog_content)
                    post_content = linkedin_agent.generate_text()
                    st.write(post_content)
                    st.image(imgs, ['image 1', 'image 2'], width=320)
                    token = st.text_input("LinkedIn Access Token", type="password")
                    if st.button('Post with image 1'):
                        if token:
                            linkedin_agent.post_on_linkedin(token, post_content, imgs[0])
                            st.success('posted')
                        else:
                            st.warning("Please enter a LinkedIn access token.")
                    if st.button('Post with image 2'):
                        if token:
                            linkedin_agent.post_on_linkedin(token, post_content, imgs[0])
                            st.success('posted')
                        else:
                            st.warning("Please enter a LinkedIn access token.")


        if "Twitter Tweet" in options:
            with st.spinner("Creating Twitter Tweet..."):
                with st.expander("Twitter Tweet"):
                    twitter_agent = TwitterAgent(llm, topic, url, blog_content)
                    twitter_content = twitter_agent.generate_tweet()
                    st.write(len(twitter_content))
                    st.write(twitter_content)
                    consumer_key        = st.text_input(label='', placeholder='consumer key')
                    consumer_secret     = st.text_input(label='', placeholder='consumer secret')
                    access_token        = st.text_input(label='', placeholder='access token')
                    access_token_secret = st.text_input(label='', placeholder='access token secret')
                    if st.button('Tweet'):
                        twitter_status = twitter_tweet(twitter_content, consumer_key, consumer_secret, access_token, access_token_secret)
                        st.success(twitter_status)


        email_agent = EmailAgent(llm, to_mail)
        mail = email_agent.send_email(to_mail, blog_status)

    else:
        st.warning("Please enter a topic, URL, and email.")




    
