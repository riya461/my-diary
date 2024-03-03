

from langchain_openai import OpenAI,OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers.json import SimpleJsonOutputParser

json_parser = SimpleJsonOutputParser()

import os
import json
from dotenv import load_dotenv
load_dotenv()
openapi_key=os.getenv('OPENAI_API_KEY')


openai = OpenAI(temperature=0.7)
gemma = Ollama(model="gemma:2b")
gemini = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=os.getenv('GEMINI_API_KEY'), temperature=0.1)



def keywords_extractor(user_entry):
    keywords_template=PromptTemplate(
            input_variables=['user_entry'],
            template=''' Given the user journel entry: {user_entry}, analyze and extract the main 
            keywords that represent the core topics or subjects addressed. 
            Please list these keywords in a structured json format, emphasizing the 
            specific terms with no extra wordings.'''
        )
    keyword_chain=LLMChain(llm=gemma,prompt=keywords_template)
    keywords=keyword_chain.invoke(user_entry)
    return keywords

def summary_extractor(user_entry):
    summary_template=PromptTemplate(
            input_variables=['user_entry'],
            template='''
            Given the user journel entry, analyse the text and provide a 
            one sentence title for describing the experience. use the examples to curate necessary output. 
        Example 1: User entry: "I finally finished the marathon I've been training for months. It was challenging, but crossing the finish line felt amazing."
        Title: Marathon Victory
        
        Example 2: User entry: "Spent the afternoon baking cookies with my kids. We made a huge mess, but the fun and laughter were worth it."
        Title: " Messy Kitchen, Happy Hearts"
        
        Example 3: User entry: "Had a difficult day at work. Felt overwhelmed by the projects piling up and the looming deadlines."
        Title: Work Woes
        
        User entry: "{user_entry}"
        Title:
        '''
        )
    summary_chain=LLMChain(llm=gemini,prompt=summary_template)
    summary_text=summary_chain.invoke(user_entry)
    return summary_text['text']


def sentimental_analysis(user_entry):
    sentiment_template1=PromptTemplate(
            input_variables=['user_entry'],
            template=''' Analyze the following text and determine the overall sentiment. 
            Provide a sentiment classification from the ones below:
            1. Happy 
            2. Sad
            3. Productive
            4. Frustrated
            5. Lonely
            . 
            Example 1: User entry: "I finally finished the marathon I've been training for months. It was challenging, but crossing the finish line felt amazing."
            Productive
            
            Example 2: User entry: "Spent the afternoon baking cookies with my kids. We made a huge mess, but the fun and laughter were worth it."
            Happy
            
            Example 3: User entry: "Had a difficult day at work. Felt overwhelmed by the projects piling up and the looming deadlines."
            Frustrated
            Please provide the sentiment classification ONLY and not in double quotes.
            Text: {user_entry}"'''
        )
    sentiment_chain=LLMChain(llm=gemini,prompt=sentiment_template1)
    sentiment_category=sentiment_chain.invoke(user_entry)
    
    return sentiment_category['text']



def suggession(user_entry,age,sex,person,calm,hobby):
    
    summary_template=PromptTemplate(
            input_variables=['user_entry', 'age', 'sex', 'person', 'calm', 'hobby'],
            
            template='''
            You are an expert therapist. You give highly valuable suggessions according to 
            your patients thoughts and give reccomendations to them. Yout patient writes
            journel daily and your job is analyse the entry, analyse the situation and give 
            proper recommendation to the user which highly aligns with the interests and activities.
            Give reccommendation on how user can cpe with the situation, encourage morale and mood.
            Give Quests which the user can do to cope from adverse situations.
            A {sex} user is present who is {age} years old. 
            He described about his interests and hobbies as {hobby}.
            He calms himself with {calm} and describes his cherished people as {person}.
            With the following journel entry {user_entry}. Help the patient. Return the summarised response in a proper json format with keys reccomendations. 

            Example:
            ["Write a gratitude journal each day, listing three things you're grateful for.", "Spend time in nature for at least 30 minutes each day."]
            ["Do something kind for someone else each day.", "Learn a new skill or hobby.", "Meditate or practice mindfulness for 10 minutes each day."] 
            ["Set a goal to connect with one friend or family member each day.", "Challenge one negative thought each day by reframing it in a more positive way."]
            '''
        )
    json_chain = summary_template | gemini | json_parser
    # suggestion_chain=LLMChain(llm=gemini,prompt=summary_template)
    suggestion_result = json_chain.stream({
        'user_entry': user_entry,
        'age': age,
        'sex': sex,
        'person': person,
        'calm': calm,
        'hobby': hobby
    })
    
    return list(suggestion_result)

def check_sensitive_words(user_text):
    
    sensitive_keys={
        "emotional_distress":['Depressed','Hopeless','Worthless','Overwhelmed','Anxious','Panic','Fearful','Isolated','Lonely'],
        "crisis":['Suicidal thoughts','Self harm','No reason to live','Unbearable pain','Feeling trapped','Wanting to die','End it all'],
        "negative_perception":['Hate myself','Cant do anything right','Failure','Disappointment','Useless','Invisible'],
        "personal_struggle":['Conflict','Breakup','Divorce','Abuse','Bullying','Betrayal','Rejection'],
        "health_symptoms":['Fatigue','Insomnia','appetite', 'tired','Numb','Cant focus'],
        "bad_behaviour":['Withdrawing','Isolating','Drinking','Using' ,'drugs','Aggression'],
        "trauma":['Trauma','Assault','Accident','Disaster','Death','Loss']
    }

    user_text_lower = user_text.lower()
    matched_categories = {}

    for category, keywords in sensitive_keys.items():
        matched_keywords = [keyword for keyword in keywords if keyword.lower() in user_text_lower]
        if matched_keywords:
            matched_categories[category] = matched_keywords
    return matched_categories

# user_entry='''Today felt like a rollercoaster of emotions. The morning started off on a high note—I received an email confirming my promotion at work, something I’ve been working towards for the past year. I felt a surge of excitement and pride. It was a moment of validation for all the hard work and late nights. I decided to treat myself to a nice breakfast, basking in the glow of my accomplishment.
#                 But, as the day progressed, a cloud seemed to hover over me. I had a long and draining meeting in the afternoon. Discussions went in circles, and it felt like we were not making any progress. The frustration from the meeting lingered longer than I expected, casting a shadow over my earlier joy.
#                 Later in the evening, I went for a walk to clear my head. The park was serene, with the gentle rustling of leaves and distant laughter of children playing. It was a bittersweet feeling—peaceful yet tinged with the day’s earlier frustrations. I couldn’t shake off a sense of loneliness, wondering why I didn’t have someone to share my day's ups and downs with.'''

# print(suggession(user_entry, "20","Male", "Amma","Beach","Guitar")[3]["recommendations"][0:3])





# input1='Arjun'

# # # print(summary_extractor(user_entry))
# # output=suggession(user_entry,input1,'20','talking with peple, interacting with kids','love playing guitar,drawing','getting treated well, having good friends')
# # output_json=data = json.loads(output)
# # # recomendatios=output[4]['recommendations']
# print(list(check_sensitive_words('I am feeling so worthless and hopeless', sensitive_keys).keys())[0])