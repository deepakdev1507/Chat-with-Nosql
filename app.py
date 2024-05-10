import streamlit as st
from pymongo import MongoClient
import urllib,io,json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from openai import OpenAI

Oclient = OpenAI(api_key=st.secrets["openaiKey"])

llm=ChatOpenAI(api_key=st.secrets["openaiKey"],model="gpt-3.5-turbo-0125",temperature=0.0)


client=MongoClient(st.secrets["mongoURI"])
db=client["sample_airbnb"]
collection=db["listingsAndReviews"]



with io.open("sample.txt","r",encoding="utf-8")as f1:
    sample=f1.read()
    f1.close()

def check_login(username, password):
    env_username = st.secrets["userName"]
    env_password = st.secrets["password"]
    # print(env_username)
    # print(env_password)
    return username == env_username and password == env_password

prompt="""
        you are a very intelligent AI assitasnt who is expert in identifying relevant questions fro user
        from user and converting into nosql mongodb agggregation pipeline query.
        Note: You have to just return the query as to use in agggregation pipeline nothing else. Don't return any other thing
        Please use the below schema to write the mongodb queries , dont use any other queries.
       schema:
       the mentioned mogbodb collection talks about listing for an accommodation on Airbnb. The schema for this document represents the structure of the data, describing various properties related to the listing, host, reviews, location, and additional features. 
       your job is to get python code for the user question
       Here’s a breakdown of its schema with descriptions for each field:

1. **_id**: Unique identifier for the listing.
2. **listing_url**: URL to the listing on Airbnb.
3. **name**: Name of the listing.
4. **summary**: A brief summary of the listing.
5. **space**: Description of the space provided.
6. **description**: Full description of the listing.
7. **neighborhood_overview**: Overview of the neighborhood.
8. **notes**: Additional notes provided by the host.
9. **transit**: Information about local transit options.
10. **access**: Information about what parts of the property guests can access.
11. **interaction**: Description of how the host will interact with the guests.
12. **house_rules**: House rules that guests must follow.
13. **property_type**: Type of property (e.g., House, Apartment).
14. **room_type**: Type of room (e.g., Entire home/apt, Private room).
15. **bed_type**: Type of bed provided.
16. **minimum_nights**: Minimum number of nights required for booking.
17. **maximum_nights**: Maximum number of nights allowed for booking.
18. **cancellation_policy**: Cancellation policy for the listing.
19. **last_scraped**: Date when the data was last scraped.
20. **calendar_last_scraped**: Date when the calendar was last scraped.
21. **first_review**: Date of the first review.
22. **last_review**: Date of the last review.
23. **accommodates**: Number of guests the listing accommodates.
24. **bedrooms**: Number of bedrooms.
25. **beds**: Number of beds.
26. **number_of_reviews**: Total number of reviews.
27. **bathrooms**: Number of bathrooms.
28. **amenities**: List of amenities provided.
29. **price**: Nightly price for the listing.
30. **security_deposit**: Amount of the security deposit.
31. **cleaning_fee**: Cleaning fee charged.
32. **extra_people**: Fee for extra guests.
33. **guests_included**: Number of guests included in the booking price.
34. **images**: Object containing URLs for various images of the listing.
35. **host**: Object containing information about the host.
36. **address**: Object containing detailed address of the listing.
37. **availability**: Object detailing availability for different time spans (30, 60, 90, and 365 days).
38. **review_scores**: Object containing different review scores (overall, accuracy, cleanliness, checkin, communication, location, value).
39. **reviews**: Array of review objects, each containing details about individual reviews.

##Embedded Objects

**Host Details:**
   - **host_id**: Unique identifier for the host.
   - **host_url**: URL to the host’s profile.
   - **host_name**: Name of the host.
   - **host_since**: Date when the host joined Airbnb.
   - **host_location**: Location of the host.
   - **host_about**: Information about the host.
   - **host_response_time**: Average response time of the host.
   - **host_response_rate**: Host's response rate.
   - **host_acceptance_rate**: Rate at which the host accepts reservations.
   - **host_is_superhost**: Whether the host is a superhost.
   - **host_thumbnail_url**: URL to the host's thumbnail image.
   - **host_picture_url**: URL to the host's picture.
   - **host_neighbourhood**: Neighbourhood of the host.
   - **host_listings_count**: Number of listings the host has.
   - **host_total_listings_count**: Total number of listings including joint listings.
   - **host_verifications**: List of verifications the host has completed.
   - **host_has_profile_pic**: Whether the host has a profile picture.
   - **host_identity_verified**: Whether the host's identity has been verified.

**Address Details:**
   - **street**: Street address of the listing.
   - **suburb**: Suburb in which the listing is located.
   - **government_area**: Government area the listing belongs to.
   - **market**: Market area for the listing.
   - **country**: Country where the listing is located.
   - **country_code**: Country code for the listing.
   - **location**: Object containing geographical coordinates (longitude, latitude).

**Location Object:**
   - **type**: Type of location data (Point).
   - **coordinates**: Array of coordinate values (longitude, latitude).
   - **is_location_exact**: Whether the location is exact.

**Images Object:**
   - **thumbnail_url**: URL of the thumbnail image.
   - **medium

_url**: URL of the medium-sized image.
   - **picture_url**: URL of the picture.
   - **xl_picture_url**: URL of the extra-large picture.

##Arrays

**Amenities**:
   - List of amenities available at the listing (e.g., Wifi, Kitchen, etc.).

**Reviews**:
   - **_id**: Unique identifier for the review.
   - **date**: Date of the review.
   - **listing_id**: ID of the listing reviewed.
   - **reviewer_id**: ID of the reviewer.
   - **reviewer_name**: Name of the reviewer.
   - **comments**: Text of the comment left by the reviewer.

This schema provides a comprehensive view of the data structure for an Airbnb listing in MongoDB, 
including nested and embedded data structures that add depth and detail to the document.
use the below sample_examples to generate your queries perfectly
sample_example:

Below are several sample user questions related to the MongoDB document provided, 
and the corresponding MongoDB aggregation pipeline queries that can be used to fetch the desired data.
Use them wisely.

sample_question: {sample}
As an expert you must use them whenever required.
Note: You have to just return the query nothing else. Don't return any additional text with the query.Please follow this strictly
input:{question}
output:
"""
query_with_prompt=PromptTemplate(
    template=prompt,
    input_variables=["question","sample"]
)
llmchain=LLMChain(llm=llm,prompt=query_with_prompt,verbose=True)


def getChartFromOpenAI(ans):
     response = Oclient.chat.completions.create(
          model="gpt-3.5-turbo-0125",
          temperature=0.0,
          messages=[
               {"role":"system","content":"Based on the data provided below , you have to write a code to make a pandas chart/ graph/ pie chart/ doughnut graph in python , assuming pandas and plotly is installed in the system make a very informative chart for the stack holders , Based on data you can decide which type of diagram best describes the data"},
               {"role":"system","content":"Always respond back in json format with Key as code: value of the same should the actual code to display graph with pandas and plotly for the data, don't make assumtion for the data use the data which is only provided"},            
               {"role":"system","content":"always use the data given below to create the chart dont make assumptions for the data and dont miss out any data for making the chart , write complete code"},
               # {"role":"system","content":"Always write code in such a way that the graph made by you should stored as a png image at location 'temp.png' and dont use command fig.show()"},
               {"role":"user","content": str(ans) }
          ],
          response_format={ "type": "json_object" }
     )
     print(response.choices[0].message.content)
     data = json.loads(response.choices[0].message.content)
     print(data["code"])
     code =data["code"] 
     exec(data["code"])
     code= code.replace("fig.show()","fig.write_image('temp.png')")
     exec(code)


def makeProperResponse(input,ans):
     response = Oclient.chat.completions.create(
          model="gpt-3.5-turbo-0125",
          temperature=0.0,
          messages=[
              {"role":"system","content":"You will be given user's input and an answer"},
              {"role":"system","content":"user's question is "+input},
              {"role":"system","content":"Answer by a machine algorithm"+ ans},
              {"role":"system","content":"your task is to make and answer a proper answer according to the users question using the context of the unstructured answer"},
              {"role":"system","content":"always respond back in json format with the following keys and details , keys are finalResponse: value should be a answer in natural language "},
              {"role":"system","content":"Keep the keys always same as mentioned above do not change the keys, and do not miss any data while making the response"}
              
              
          ],
          response_format={ "type": "json_object" }
     )
    
     data = json.loads(response.choices[0].message.content)
     return data["finalResponse"]
   #   st.write(data["formattedanswer"])
    
   #   print(data["code"])
   #   exec(data["code"])

st.title("Smartdocs POC for chat with Mongo and get Interactive graph ")
st.write("- POC start date 08-05-2024")


if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False

if st.session_state['login_status']:
   input=st.text_area("Enter question")
   if input is not None:
      button = st.button("Submit")
      if button:
         response = llmchain.invoke({
               "question": input,
               "sample": sample
         })
         print(str(response))
         query = json.loads(response["text"])
         results = list(collection.aggregate(query))
         print(query)
         
         if not results:  # Check if results is empty
               print("No results found.")
               st.write("No results found.")
               
         else:
            print(str(results))
            
            ans = ""
            for result in results:
                  # st.write(result)
                  ans += str(result)
                  print(ans)
                  if(len(ans)>=10000):
                     break
            
            ans = makeProperResponse(input,ans)
            st.write(ans)
            getChartFromOpenAI(ans)
            st.image('temp.png')

else:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_login(username, password):
                st.session_state['login_status'] = True
                st.experimental_rerun()
            else:
                st.error("Incorrect username or password")