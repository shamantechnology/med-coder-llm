"""
MedCoderAI
Takes in description of care given and suggests the proper ICD-10 and CPT-4 codes
Using TruEra to keep PaLM on task and Zillz ICD/CPT descriptions
"""

from medcoderai import MedCoderAI
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    md = MedCoderAI()
    md.run()

    user_msg = ""
    while user_msg != "/quit":
        user_msg = input("Enter in patient description. To quit type \"/quit\" \n")
        md.ask_question(user_msg)