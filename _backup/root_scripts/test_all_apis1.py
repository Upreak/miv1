import os
from datetime import datetime
# Library for OpenRouter and Grok (xAI)
from openai import OpenAI
# Library for Google Gemini
import google.generativeai as genai
# Library for groq
from groq import Groq

# ==============================================================================
# 1. CONFIGURATION: PASTE YOUR KEYS HERE
# ==============================================================================

# OpenRouter Configuration
OPENROUTER_API_KEY = 
OPENROUTER_MODEL = "openrouter/bert-nebulon-alpha" # Example model to test OpenRouter connection

# Grok (xAI) Configuration
# xAI uses the standard OpenAI client but with a specific base URL
GROQ_API_KEY = 
GROQ_MODEL = "openai/gpt-oss-120b"

# Google Gemini Configuration
GOOGLE_API_KEY = 
GOOGLE_MODEL = "gemini-2.5-flash-lite"

# Output settings
OUTPUT_FILE = "api_test_results.txt"

# ==============================================================================
# 2. THE PROMPT (Resume Parser)
# ==============================================================================
RESUME_PROMPT = """
Task: Extract all information explicitly mentioned in the resume(structured/unstructured text) and structure it according to the Candidate Portfolio format. Do NOT infer, guess, or generate missing details. If a field is not present, leave it blank.

General Rules:
- Use only the content found in the resume.
- Maintain exact wording for skills, certificates, responsibilities, tools, etc.
- Dates must follow DD/MMM/YYYY format when possible.
- For multiple values, return them as arrays.
- Output strictly in JSON.

Fields to Extract (Output):
Identity Basics:
  Full Name:
  Email Address:
  Mobile Number:
  Professional Summary:
  LinkedIn URL:
  Portfolio URL

Education & Skills:
  Highest Education (PhD/Doctorate):
  Second Highest Education (Masters):
  Third Highest Education (Bachelor):
  DIPLOMA:
  ITI:
  PUC:
  SSLC:
  Certificates:
  Skills:
  Field of Study:
  Projects / Profile:
  GitHub / Behance / Kaggle URL:

Job Preferences:
  Total Experience (Years):
  Current Role:
  Expected Role:
  Job Type:
  Current Locations:
  Ready to Relocate:
  Notice Period:
  Work Authorization / Visa:

Salary Info:
  Current CTC (LPA):
  Expected CTC (LPA):

Broader Preferences & Personal Details:
  Preferred Industries:
  Gender:
  Marital Status:
  Date of Birth:
  Languages Known:

Work History (repeat for each job):
  Job Title/Role:
  Company Name:
  Start Date:
  End Date:
  Key Responsibilities:
  Tools Used:

Processing Guidelines:
- Include degree, institution, year, and score if available.
- List certificates individually.
- Extract every skill exactly as written.
- Create separate entries for each job in work history.
- Keep responsibilities true to the resume text.
- Leave blank fields empty.
- Do NOT assume or interpret any information not stated.

Output:
Return ONLY the final JSON.

Resume Text:
{{ Anushya Nataraj 
 
Email: nkanumba2016@gmail.com   
 
Contact: +91 - 9698881600  
91-7538866295  
 
 
OBJECTIVE  
 
To use my knowledge and skills in Industry and I contribute with full involvement, passion & 
dedication for the growth of the Company.  
 
 
PROFESSION AL EXPERIENCE  
 
IT Recruitment  
 
 Involved in End -to-End recruitment Process.  
 Closing entry, middle and senior level positions within given time duration  
 
   Client Coordination  
 
 Maintaining good relations with clients and acting as a client coordinator.  
 Taking regular feedback from clients with regards to quality of profiles sent new openings and status 
of current openings.  
 
 
Current Company:    Teamware Solution,  Chennai  
   
Designation          :  Talent Acquisition   
Duration                :  Apr 2021 – June 2023  
 
Role and Responsibilities:  
 Sourcing the candidates in portal as per the Client  requirement.  
 Screening the resources by posting few queries matching with the job  descriptions.  
 Getting the acknowledgements from the resources for further interview  levels.  
 Submitting the profile to the account managers for client  reviewal.  
 Doing cross checks ensuring candidates interest on the  same.  
 Arranging  for the telephonic  interviews/in -person  interviews/Skype  interviews  of the candidates & 
scheduling their interview as per the availability of the Technical  Panel.  
 Initiating the HR Discussions to be done for the candidates by the  Client.  
 Initiating Document submissions by the candidates to HR  Panel.  
 Offering the candidate and following up wit h the offered candidate till he/she joins the organization , 
handling issues, in getting him/her relieved from his/her current organization as well as having an open 
discussion with the candidates in keeping them interested, to ensure not losing the candida te and to 
make him/her  join. 
 Preparing daily trackers /submission trackers and sending across to the general  manager.  
 Maintaining and Developing Database for Future  Requirements.  
 
Previous Company   :  Talent21 Management & Shared Service Pvt Ltd, Chennai     
   
Designation             :   Associate Consultant  
Duration                   :   June 2019 to Feb 2021  
 
 
Clients   
 
 Capgemini  
  SCB   
 Fidelity  
 PayPal  
 BNP  
  Society General  
  Robert Bosch  
 TechMahindra  
 Epsilon  
 AXA Business Service  
 
Technologies Worked  
 
Microsoft Technologies : .Net, ASP.Net, C#, VB.Net, .net, Share Point, Python, C ++, PHP, ETL  
 , Informatica, Hadoop , Azure, Big data . 
 
Web Technologies : Core java, J2EE (EJB, JSP, WCF, WPF, TDD, Entity Framework, MVC, Web 
Services, Xml, spring, Hibernate, struts, Ajax, Json, XML, HTML, XSLT, CSS, Spring boot, Micro 
service)  
 
ERP/CRM Skills : SAP -Technical/Functional – SAP ABAP, FICO 
Databases : Oracle SOA, PL/SQL, SQL Server, MySQL  
Area of Interest  
 
 HR 
 Finance  
 
 
EDUCATIONAL QUALIFICATION  
 
 
 MBA - Sree Saraswathi Thyagaraja College, Pollachi, 2016  (76%)  
 B. Com - Sree Saradha Nikedhan College, Salem, 2013  (71%)  
 H.S.E - GKN Hr Sec School, Karatumadam, 2010  (76%)  
 S.S.L.C - NGNG Hr Sec School, Reddiarur, 2008  (66%)  
  
PAPER PRESENTATIONS  
 
 Presented a paper entitled on "Integrated Marketing Communication" at national conference 
conducted by SMS College, Coimbatore.  
 Presented  a paper  entitled  on "Make  in India  in banking  sector"  at national  conference  conducted by Sree 
Saraswathi Thyagaraja College,  Pollachi.  
 Presented a paper entitled on "Make in India” at national conference conducted by Sree 
Saraswathi Thyagaraja College,  Pollachi.  
 
PARTICIPATIONS &  ACHIEVENETS  
 
 Won an award for “100% Attendance” in my  PG. 
 Volunteered in "Rapture  2015".  
 Active member in Coimbatore Management  Association.  
 Active Member in TYMA (MBA Students' Association @  STC).  
 
 
AREA OF RESEARCH  
 
 Title of MBA project: A Study on  Cash Management at ROOTS MULTICLEAN LIMITED, 
Coimbatore.  
 
INDUSTRIAL TRAINNING  
 
Tamil nadu Newsprint Paper Limited, Chennai (2 months) - The main purpose of this training is to acquire 
the knowledge about the whole process of the company and to know the fi nancial activities of the company.  
 
COMPUTER PROFICIENCY  
 
 MS-Office  
 Tally  
 
ACHIEVEMENTS  
 
 Winner of Zonal level Kabbadi Competition in SSNS College,  Salem  
 Second Prize in  Relay  
 Won Second prize in singing Competition at NGNG School,  Reddiarur  
 
 
PERSONAL PROFILE  
Nationality                     : Indian   
Religion                         : Hindu  
Date of Birth                 : 04.01.1993  
Gender                          : Female  
Marital  Status               : Married  
   Language                     : Tamil, English  & Malayalam  
 
 
Date:  (Anushya  NK) }}"""

# ==============================================================================
# 2. HELPER FUNCTION TO LOG RESULTS
# ==============================================================================
def log_result(provider, success, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"
    
    separator = "-" * 60
    log_entry = (
        f"{separator}\n"
        f"Time: {timestamp}\n"
        f"Provider: {provider}\n"
        f"Status: {status}\n"
        f"Response/Error: {content}\n"
        f"{separator}\n"
    )

    # Print to console
    print(f"[{provider}] {status}...")
    if success:
        print(f"   > Response: {content[:100]}...") # Show snippet
    else:
        print(f"   > Error: {content}")

    # Save to file
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

# ==============================================================================
# 3. TEST FUNCTIONS
# ==============================================================================

def test_openrouter():
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        
        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": RESUME_PROMPT}]
        )
        response = completion.choices[0].message.content
        log_result("OpenRouter", True, response)
        
    except Exception as e:
        log_result("OpenRouter", False, str(e))

def test_groq_cloud():
    print("--> Testing Groq (Groq Cloud)...")
    try:
        # Initializes the Groq Client (from your snippet)
        client = Groq(api_key=GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": RESUME_PROMPT
                }
            ]
        )
        log_result("Groq Cloud", True, completion.choices[0].message.content)
    except Exception as e:
        log_result("Groq Cloud", False, str(e))

def test_gemini_direct():
    try:
        # Configure the Google SDK
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize model
        model = genai.GenerativeModel(GOOGLE_MODEL)
        
        # Generate content
        response = model.generate_content(RESUME_PROMPT)
        
        # Handle cases where response.text might be None
        if response.text:
            log_result("Gemini Direct (Google)", True, response.text)
        else:
            log_result("Gemini Direct (Google)", True, "Response generated but text is empty (possibly blocked)")

    except Exception as e:
        log_result("Gemini Direct (Google)", False, str(e))

# ==============================================================================
# 4. MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print(f"Starting API Tests. Saving results to {OUTPUT_FILE}...\n")
    
    # 1. Test OpenRouter
    test_openrouter()
    
    # 2. Test Groq (Groq Cloud)
    test_groq_cloud()
    
    # 3. Test Gemini (Google)
    test_gemini_direct()
    
    print("\nTest Run Complete.")