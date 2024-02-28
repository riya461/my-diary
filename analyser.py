from langchain_openai import OpenAI,OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

import os
import json
from dotenv import load_dotenv
load_dotenv()
openapi_key=os.getenv('OPENAI_API_KEY')


openai = OpenAI(temperature=0.7)
gemma = Ollama(model="gemma:2b")


def sentimental_analysis(user_entry):
    sentiment_template1=PromptTemplate(
            input_variables=['user_entry'],
            template=''' Analyze the following text and determine the overall sentiment. 
            Provide a sentiment classification from the ones below:
            . 
            Text: {user_entry}"'''
        )
    sentiment_chain=LLMChain(llm=openai,prompt=sentiment_template1)
    sentiment_category=sentiment_chain.invoke(user_entry)
    
    return sentiment_category

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
        Title: "Marathon Victory: A Challenge Overcome"
        
        Example 2: User entry: "Spent the afternoon baking cookies with my kids. We made a huge mess, but the fun and laughter were worth it."
        Title: "Baking Bliss: Messy Kitchen, Happy Hearts"
        
        Example 3: User entry: "Had a difficult day at work. Felt overwhelmed by the projects piling up and the looming deadlines."
        Title: "Work Woes: Overwhelmed by Deadlines"
        
        User entry: "{user_entry}"
        Title:
        '''
        )
    summary_chain=LLMChain(llm=openai,prompt=summary_template)
    summary_text=summary_chain.invoke(user_entry)
    return summary_text['text']

user_entry='''Today felt like a rollercoaster of emotions. The morning started off on a high note—I received an email confirming my promotion at work, something I’ve been working towards for the past year. I felt a surge of excitement and pride. It was a moment of validation for all the hard work and late nights. I decided to treat myself to a nice breakfast, basking in the glow of my accomplishment.
                But, as the day progressed, a cloud seemed to hover over me. I had a long and draining meeting in the afternoon. Discussions went in circles, and it felt like we were not making any progress. The frustration from the meeting lingered longer than I expected, casting a shadow over my earlier joy.
                Later in the evening, I went for a walk to clear my head. The park was serene, with the gentle rustling of leaves and distant laughter of children playing. It was a bittersweet feeling—peaceful yet tinged with the day’s earlier frustrations. I couldn’t shake off a sense of loneliness, wondering why I didn’t have someone to share my day's ups and downs with.'''




print(summary_extractor(user_entry))