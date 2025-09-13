# email_generator.py
"""
AI Cold Email Generator with ChromaDB Integration

"""

import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

os.environ['USER_AGENT'] = 'ColdEmailGenerator/1.0'
load_dotenv()

class EmailGenerator:
    def __init__(self, vectorstore_path="chroma_db"):
        self.llm = ChatGroq(
            temperature=0.6,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )
        
        self.vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

    def load_job_from_url(self, url):
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs[0].page_content[:3000]

    def extract_job_info(self, job_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### JOB POSTING TEXT:
            {job_text}
            
            ### INSTRUCTION:
            Extract the job information into JSON format with these keys: 
            - `role`: job title/position
            - `experience`: required experience level  
            - `skills`: list of required technical skills
            - `description`: main responsibilities/requirements
            
            Return only valid JSON, no other text.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"job_text": job_text})
        
        try:
            json_parser = JsonOutputParser()
            return json_parser.parse(res.content)
        except OutputParserException:
            return {"description": job_text}

    def generate_email(self, job_input):
        if job_input.startswith(('http://', 'https://')):
            raw_text = self.load_job_from_url(job_input)
        else:
            raw_text = job_input

        job_info = self.extract_job_info(raw_text)
        relevant_docs = self.retriever.invoke(str(job_info))
        portfolio_context = "\n".join([doc.page_content for doc in relevant_docs])
        
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB REQUIREMENTS:
            {job_info}
            
            ### MY QUALIFICATIONS (FROM PORTFOLIO):
            {portfolio_context}
            
            ### INSTRUCTION:
            Write a professional cold email that matches my qualifications with this job.
            Highlight specific relevant skills and experiences.
            Keep it concise (under 200 words), professional, and include a call to action.
            Strictly follow the limit of the 200 words and keep the email relevant and to the point.
            ### EMAIL (NO PREAMBLE):
            """
        )
        
        chain_email = prompt_email | self.llm
        email = chain_email.invoke({
            "job_info": str(job_info),
            "portfolio_context": portfolio_context
        }).content
        
        return job_info, email