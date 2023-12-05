"""
MedCoderAI
Takes in description of care given and suggests the proper ICD-10 and CPT-4 codes
Using TruEra to keep PaLM on task and Zillz ICD/CPT descriptions
"""

import json
import pandas as pd
import subprocess
from dotenv import load_dotenv
import weaviate
from weaviate.embedded import EmbeddedOptions
from langchain.chat_models import ChatVertexAI
from langchain.vectorstores import Weaviate
from langchain.document_loaders import CSVLoader
from langchain.embeddings import VertexAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain

# printing dicts in json format
def jprint(json_in):
    print(json.dumps(json_in, indent=2))

def generate_cpt_icd_docs():
    """
    Generate langchain docs from CSVs
    """
    code_docs = []
    try:
        cpt_loader = CSVLoader("./data/2024_DHS_Code_List_Addendum_11_29_2023.csv")
        code_docs += cpt_loader.load()

        icd_loader = CSVLoader("./data/Section111ValidICD10-Jan2024.csv")
        code_docs += icd_loader.load()
    except Exception as err:
        print(f"Error when loading CPT/ICD data: {err}")

    return code_docs

def refresh_token() -> str:
    result = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error refreshing token: {result.stderr}")
        return None
    return result.stdout.strip()

def re_instantiate_weaviate() -> weaviate.Client:
    try:
        token = refresh_token()

        if token:
            client = weaviate.Client(
                embedded_options=EmbeddedOptions(
                    additional_headers={
                        "X-Palm-Api-Key": token
                    },
                    additional_env_vars={
                        "ENABLE_MODULES": "text2vec-palm"
                    }
                )
            )

            return client
        else:
            raise ValueError
    except Exception:
        raise

def main():
    try:
        # start weaviate with schemas
        client = re_instantiate_weaviate()
    except Exception as err:
        print(f"failed to start weviate: {err}")
        pass

    # setup vectorstore and retriever
    vectorstore = Weaviate.from_documents(
        client=client, 
        documents=generate_cpt_icd_docs(), 
        embedding=VertexAIEmbeddings(), 
        by_text=False
    )

    retriever = vectorstore.as_retriever()

    llm = ChatVertexAI()

    system = "You are a medical coder. Take in descriptions of care and return a list of CPT and ICD codes with their description"

    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    conversation = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    
    # human = "Patient had a sore throat and recieved cough medicine"
    # prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    # messages = prompt.format_messages()

    # resp = chat(messages)

    # print(resp)


if __name__ == "__main__":
    load_dotenv()
    main()