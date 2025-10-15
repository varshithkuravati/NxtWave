from django.shortcuts import render

from.models import Teacher, Course, Document





import getpass
import os
# Create your views here.


from typing import Annotated
from typing_extensions import TypedDict

from django.http import JsonResponse



from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from langchain_core.messages import BaseMessage


from django.conf import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API Key: ")

from langchain.chat_models import init_chat_model

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import json
from langgraph.checkpoint.memory import InMemorySaver




import base64
import httpx

import re
import ast




def extract_all_dicts(s: str):
    dicts = []
    for match in re.findall(r'\{.*?\}', s, re.DOTALL):
        try:
            d = ast.literal_eval(match)
            if isinstance(d, dict):
                dicts.append(d)
        except Exception:
            continue
    return dicts


def extract_dict_from_string(s: str):
    # Extract the first {...} block from the string using regex
    match = re.search(r'\{.*\}', s, re.DOTALL)
    if not match:
        return None  # No dictionary found
    
    dict_str = match.group(0)

    try:
        # Safely evaluate string to Python dict (no code execution)
        return ast.literal_eval(dict_str)
    except Exception:
        return None
    

def extract_list_from_string(s: str):
    # Extract the first {...} block from the string using regex
    match = re.search(r'\[.*\]', s, re.DOTALL)
    if not match:
        return None  # No dictionary found

    dict_str = match.group(0)

    try:
        # Safely evaluate string to Python list (no code execution)
        return ast.literal_eval(dict_str)
    except Exception:
        return None
    



def teacher_dashboard(req):

    teacher = Teacher.objects.all()
    # teachers = Teacher.objects.all(teacher_user=req.user)
    # courses = Course.objects.all()
    # documents = Document.objects.all()

    context = {
        'teachers': teacher,
        # 'courses': courses,
        
    }

    return render(req, 'teacher/teacher-dashboard.html', context=context)






def docs_upload(req):
        

        if req.method == "POST":
            

            title = req.POST.get('title')
            doc_type = req.POST.get('type')
            
            file = req.FILES.get('file')
            course_id = req.POST.get('course')
            teacher_id = req.POST.get('teacher')

            

        



        



            doc_details = {

                        "type": "syllabus",


            }


            # type = doc_details['type']





            sys_mess = 'you are a good teacher, you new analysis the document. it may syllabus or Notes or reference document. if doument is syllabus or circulum doument then extract the content of what are the chapters and what are the subtopics in each chapter and give output as ("chapters": ( "chapter1_name": ("subtopics": ["topic1","topic2", ..]), "chapter2_name": ("subtopics": ["topic1","topic2", ..]),.. )), in this case case output should be a python dictionary.consider the python dictionary format which i given as curve bracked are replaced with flower brackets . if document is notes or reference document then extract the content of what topics convered in the document and give output as ["topics1","topic2", ..] in this case output should be a pyhon list. strictly dont add any extra content in output'
            user_mess = f" given doument is a {doc_type} document"

            message = {
                        "role": "user",
                        "content": [
                                        {
                                        "type": "text",
                                        "text": sys_mess
                                            },

                                        {
                                            "type": "text",
                                            "text": user_mess
                                        },
                                        



                                    ],
                            }



            # pdf_url = "https://gatenotes.in/GATE-Syllabus-New/GATE-Syllabus-MA%20Mathematics(www.gatenotes.in).pdf"


            # with open("myfile.pdf", "rb") as f:
            #     pdf_data = base64.b64encode(f.read()).decode("utf-8")


            # uploaded_file = request.FILES['file']

            # Temporarily save uploaded file content to memory
            pdf_data = base64.b64encode(file.read()).decode('utf-8')


            # pdf_data = base64.b64encode(httpx.get(pdf_url).content).decode("utf-8")




            docs_file = {

                        "type": "file",
                        "source_type": "base64",
                        "data": pdf_data,
                        "mime_type": "application/pdf",

            }


            message['content'] = message['content'] + [docs_file]





            responce = model.invoke([message])



            if type == "syllabus" or type == "curriculum":

                data_extracted = extract_dict_from_string(responce['messages'][-2].content)

                doc_details = doc_details + data_extracted

            else:

                



                data_extracted = extract_list_from_string(responce.content)

                doc_details["topics_covered"] = data_extracted


            # save this doc_details in discription columbn of databse


            description = doc_details

            document = Document.objects.create(

                title=title,
                type=doc_type,
                file=file,
                # course=course_id,
                # teacher=teacher_id,
                description=description,
            )


            document.save()

            return JsonResponse({"message": "Document content extracted and uploaded successfully"}, status=200)










        return JsonResponse({"error": "Sorry we are facing some problems in backend"}, status=400)







# quiz test function


def quizai_test(req):



    docs_details = {

        "1": { "name": "syllabus","type": "pdf", "description": "it contains detailed syllabus of physics for this academic year", "path": "/docs/syllabus.pdf"}, 
        "2": {"name": "class notes of newtons 3rd law of motion","type": "pdf", "description": "it contains whatever discussed in the class on newtons 3rd law of motion", "path": "/docs/syllabus/3rd_law.pdf"}

        }


    stu_scores = {

                "1": { "test_score": "", "weak_topics": [], "test_topic": "","test_date": "" },


    }


    system_template = "You are a knowledgeable and strict teacher. Your task is to select only the relevant documents needed to prepare a quiz on the given topic. The available documents are provided as a Python dictionary, available documents are {doc_details}, and the quiz topic is {topic}. Each document includes a description. Carefully read the topic and the document descriptions, then select only the documents that are relevant for preparing a quiz on the given topic. Return your answer only as a Python dictionary in the exact same format as the input documents dictionary, but include only the selected documents. Do not add any explanations, comments, or text outside the dictionary. Do not mention that the output is in any format (such as Python dictionary or JSON). Output must strictly contain only the required documents in dictionary format and nothing else."

    user_message = "prepare a quiz on {topic}"

    prompt_template = ChatPromptTemplate.from_messages([

            ("system", system_template),
            ("user", user_message)

        ])

    prompt = prompt_template.invoke({"doc_details": docs_details, "topic": "newtons 3rd law of motion"})

    responce = model.invoke(prompt)





     

    context1 = {
        'responce': responce.content
    }





    return render(req, 'teacher/quizAi.html',context=context1)
     
     