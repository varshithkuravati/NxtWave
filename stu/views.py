from django.shortcuts import render

from teacher.models import Teacher, Course, Document

from stu.models import Student


from uuid import uuid4

from langgraph.store.memory import InMemoryStore




# Create your views here.

import getpass
import os
# Create your views here


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


from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import json
from langgraph.checkpoint.memory import InMemorySaver




import base64
import httpx



# normal views


def stu_dashboard(req):
     

     student_details = Student.objects.get(student_user=req.user.id)


     no_courses = student_details.enrolled_courses.count()

     i = 1

     avg_score = 0
          


     for j in student_details.quiz_scores.values():


          avg_score = avg_score + (j["test_score"]/j["qnum"])*10
          
          i = i+1

     avg_score = avg_score / (i-1) if i > 1 else 0

     quiz_count = (len(student_details.quiz_scores)/10)*100

     content1 = {
          
          'no_courses': no_courses,
          'avg_score': avg_score,
          'quiz_count': quiz_count,
          'student_details': student_details,

     }



     
          

     return render(req, 'student/student-dashboard.html', context=content1)



def quizpage(req):
     
        return render(req, 'student/quiz.html') 


def chat_ai(req):
     
     return render(req, 'student/ai-tutor-chat.html')






# ai features for student






def quizAi(req):



    


    # message = [
    #     SystemMessage(content = "you are proffesional food cook"),
    #     HumanMessage(content = "can you give me a recipe for pasta ?"),
    # ]








    system_template = "you are a teacher, you need to give content in json format only, do not add any other text, you need to give {qnum} questions with 4 options and answer and quections level is {level}, the json format is like this (quiz:[(question:'', options:['','','',''], answer:'')....]) consider the json format which i given as curve bracked are replaced with flower brackets."
    user_message = "prepare a quiz on {topic}"

    prompt_template = ChatPromptTemplate.from_messages([

        ("system", system_template),
        ("user", user_message)

    ])

    prompt = prompt_template.invoke({"qnum":5, "level":"easy", "topic":"Newton's laws of motion"})

    



    responce = model.invoke(prompt)
    context1 = {
        'responce': json.dumps(responce.content[7:-4])
    }





    return render(req, 'teacher/quizAi.html',context=context1)








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
    








def quizGen(req):


     if req.method == "POST":
         
        topic = req.POST.get('topic')
        level = req.POST.get('level')
        qnum= req.POST.get('qnum')

        course = req.POST.get('course')

        doc = Document.objects.filter(course__name=course)

        doc_format = { }

        j = 0

        for i in doc:
              j = j + 1
              doc_format = doc_format | { str(j): {"name": i.title, "type": i.type, "description": i.description, "path": req.build_absolute_uri(i.file.url) } }

        docs_details = doc_format






    


        # docs_details = {

        #     "1": { "name": "","type": "", "description": "", "path": ""}, 
        #     "2": {"name": "","type": "", "description": "", "path": ""}

        #     }


        # stu_scores = {

        #             "1": { "test_score": "", "weak_topics": [], "test_topic": "","test_date": "" },


        # }


        stu = Student.objects.get(student_user=req.user)

        stu_scores = stu.quiz_scores


        class State(TypedDict):
            messages: Annotated[list, add_messages]

        
        graph_builder = StateGraph(State)

        def document_loader(state: State):


            system_template = "You are a knowledgeable and strict teacher. Your task is to select only the relevant documents needed to prepare a quiz on the given topic. The available documents are provided as a Python dictionary, and the quiz topic is {topic}. Each document includes a description. Carefully read the topic and the document descriptions, then select only the documents that are relevant for preparing a quiz on the given topic. Return your answer only as a Python dictionary in the exact same format as the input documents dictionary and in it must include path, title , name. but include only the selected documents. Do not add any explanations, comments, or text outside the dictionary. Do not mention that the output is in any format (such as Python dictionary or JSON). Output must strictly contain only the required documents in dictionary format and nothing else."
            user_message = "Available documents details {doc_details} "

            prompt_template = ChatPromptTemplate.from_messages([

                ("system", system_template),
                ("user", user_message)

            ])

            prompt = prompt_template.invoke({"doc_details": docs_details, "topic": topic})

            # topic name must need to mention

            responce = model.invoke(prompt)


            # print(responce.content)

            
    


            return {'messages': [responce.content]}
        

        def prev_analysis(state: State):

            system_template = "you are a good teacher, you need to give warning to the student of what topics student need to revise or imporve based on his previous tests performances and weak topics to attempt quiz on given topic: {topic}. these details are in python dictionary format and for each test we have test_score, topics in which student unable to answer in that test is mentioned in weak_topics list, if student did not attempt any quiz until now then metion topics he need to know before attempting quiz on this topic in output"

            user_message = "previous test details are {stu_scores}"


            prompt_template = ChatPromptTemplate.from_messages([

                ("system", system_template),
                ("user", user_message)

            ])


            prompt = prompt_template.invoke({"topic": topic,"stu_scores": stu_scores})

            # topic name must need to mention


            responce = model.invoke(prompt)




            return {'messages': [responce.content]}


        def quiz_generator(state: State):


            # we need to add below block in for loop




        


            docs = extract_dict_from_string(state['messages'][-2].content)


            con = []

            # print(docs)

            # print(state['messages'][-1].content)


            

            for i in docs.values():
                

                        # acess = i.keys()


                        pdf_url = i['path']

                        # print(pdf_url)

                        # with open(pdf_url, "rb") as f:
                        #     pdf_data = base64.b64encode(f.read()).decode("utf-8")

                        pdf_data = base64.b64encode(httpx.get(pdf_url).content).decode("utf-8")

                        data_docs = {

                                "type": "file",
                                "source_type": "base64",
                                "data": pdf_data,
                                "mime_type": "application/pdf",

                                }

                        

                        con = con + [data_docs]




        #           block ends


            

            #    qnum = 5

        #    dont forget to give topic

            #    topic = ""


        

            user_mess = f"prepare a quiz on {topic}"

            # print("upto here working fine")
            





            sys_mess = f"you are a teacher, you need to give content in json format only, do not add any other text, you need to give {qnum} questions with 4 options and answer and quections level is {level}. use documents attached below to know syllabus need to cover or for reference .the json format is like this ('quiz':[('question':'', 'options':['','','',''], 'correct':  ,'answer':'', 'explanantion':'')....]) in correct attribute mention index of correct answer in options list for each quesction and consider the json format which i given as curve bracked are replaced with flower brackets. if no documents provided then prepare quiz on your own knowledge"
            


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
            
            message['content'] = message['content'] + con

            



            responce = model.invoke([message])




            return {'messages': [responce.content]}



        graph_builder.add_node("document_loader",document_loader)

        graph_builder.add_node('prev_analysis', prev_analysis)

        graph_builder.add_node('quiz_generator', quiz_generator)

        graph_builder.add_edge(START, "document_loader")
        graph_builder.add_edge("document_loader", 'prev_analysis')
        graph_builder.add_edge('prev_analysis', 'quiz_generator')
        graph_builder.add_edge('quiz_generator', END)

        graph = graph_builder.compile()


        responce = graph.invoke({'messages': [{"role": "user","content": "complete the tasks"}]})



        context1 = {
            'resQuiz': extract_dict_from_string(responce['messages'][-1].content),
            'resPrev': responce['messages'][-2].content

        }
    



        return JsonResponse(context1,status=200)

     else:

          return JsonResponse({"error": "Sorry we are facing some problems in Backend"}, status=400)












def quiz_results(req):


     if req.method == "POST":

        student_user = req.user

        student = Student.objects.get(student_user = student_user)





        wrong_attempts = json.loads(req.POST.get('wrong_attempts'))
        # wrong_attempts = json.loads(req.body)

        syllabus = Document.objects.get(type="syllabus")

        # syllabus = json.loads(syllabus.description)
        syllabus = syllabus.description
        

     

     



        #  wrong_attempts = {
            
        #       "quiz_topic": "",
        #       "qnum": ,
        #       "total_score": "",
        #       "date": "",
        #       "student_id": "",
        #       "wrong_questions": {
        #             "1": {"question": "", "student_answer": "", "correct_answer": "", "explanation": ""},
        #             "2": {"question": "", "student_answer": "", "correct_answer": "", "explanation": ""},
        #             "3": {"question": "", "student_answer": "", "correct_answer": "", "explanation": ""},
        #             "4": {"question": "", "student_answer": "", "correct_answer": "", "explanation": ""},
        #             "5": {"question": "", "student_answer": "", "correct_answer": "", "explanation": ""}
        #          }
                        
            
        #  }

    

        

        #  syllabus = {

        #       "chapters": {

        #         "1": "newtons 1st law of motion",
        #         "2": "newtons 2nd law of motion",
        #         "3": "newtons 3rd law of motion",
        #         "4": "Rotational dynamics",
        #         "5": "Fluid dynamics"

        #         }

        #      }

        class State(TypedDict):
            messages: Annotated[list, add_messages]

        
        graph_builder = StateGraph(State)



        def quiz_analysis(state: State):
            
                system_template = "you are a good teacher, you need to give analysis of student performance in quiz on given topic: {topic}. these details are in python dictionary format and for each wrong question we have question, student_answer, correct_answer and explanation why that answer is correct. based on these details you need to give analysis of student performance in quiz and what topics student need to revise or imporve. if he is performed good in this quiz suggest next topic according to syllabus, syllabus is {syllabus} . output should be in json format only like this ('revision_reqired_topics': '','suggestions_to_improve': '','next_topics_to_study':'') consider the json format which i given as curve bracked are replaced with flower brackets."

                user_message = "quiz details are {wrong_attempts}"
        
                prompt_template = ChatPromptTemplate.from_messages([
        
                        ("system", system_template),
                        ("user", user_message)
        
                    ])
        
        
                prompt = prompt_template.invoke({"topic": wrong_attempts['quiz_topic'],"wrong_attempts": wrong_attempts,"syllabus": syllabus})

                responce = model.invoke(prompt)
        
        
        
        
        
                return {'messages': [responce.content]}
        


        def data_saver(state: State):


            


            system_template = "you are a good teacher, you need to mention the topic of each wrong question in quiz on given topic: {topic}. these details are in pyhton dictionary format and for each wrong question we have question, student_answer, correct_answer and explanation why that answer is correct. based on these details you need to give topic of each wrong question. output should be a python list format only like this ['topic1','topic2',....]."

            user_message = "quiz details are {wrong_attempts}"
        
            prompt_template = ChatPromptTemplate.from_messages([
        
                        ("system", system_template),
                        ("user", user_message)
        
                    ])
        
        
            prompt = prompt_template.invoke({"topic": wrong_attempts['quiz_topic'],"wrong_attempts": wrong_attempts})

            responce = model.invoke(prompt)

            responce1 = extract_list_from_string(responce.content)

            i = f"{len(student.quiz_scores) + 1}"


            # content need to save in database


            quiz_scores1 = { i: { "test_score": wrong_attempts['total_score'],"qnum": wrong_attempts['qnum'], "weak_topics": responce1, "test_topic": wrong_attempts['quiz_topic'],"test_date": wrong_attempts['date'] }}

            # "1": { "test_score": "", "weak_topics": [], "test_topic": "","test_date": "" },


            # student.quiz_scores = student.quiz_scores | quiz_scores1
            # student.quiz_scores = {**student.quiz_scores, **quiz_scores1}

            student.refresh_from_db()

            old_scores = student.quiz_scores or {}

# In some cases JSONField can return a string (if manually set before)
            if isinstance(old_scores, str):
                old_scores = json.loads(old_scores)

# Merge safely
            merged_scores = {**old_scores, **quiz_scores1}

            student.quiz_scores = merged_scores
            # print(merged_scores)
            # print(old_scores)
            # print(student.quiz_scores)

            student.save()




            






            
            
            return {'messages': [responce.content]}
        



        

        graph_builder.add_node("data_saver",data_saver)
        graph_builder.add_node('quiz_analysis', quiz_analysis)

        graph_builder.add_edge(START, "data_saver")

        graph_builder.add_edge("data_saver", 'quiz_analysis')

        graph_builder.add_edge('quiz_analysis', END)


        graph = graph_builder.compile()

        responce = graph.invoke({'messages': [{"role": "user","content": "complete the tasks"}]})

        #  print(extract_dict_from_string(responce['messages'][-1].content))

        context1 = {
            
            'analysis': extract_dict_from_string(responce['messages'][-1].content),
            'topics': extract_list_from_string(responce['messages'][-2].content)
            
        }



        
        


        return JsonResponse(context1,status=200)
     
     else:
          
          return JsonResponse({"error": "Sorry we are facing some problems in Backend"}, status=400)






def content_clarifier(req):


    if req.method == "POST":

        performance = Student.objects.get(student_user=req.user).quiz_scores

        # data = json.loads(req.body)
        data = req.POST.get('mess')

        user_message = data

        

       


        class State(TypedDict):

                messages: Annotated[list, add_messages]


        graph_builder = StateGraph(State)

        

        def chatbot(state: State):
                
                
                responce = model.invoke(state["messages"]) 

      
                return {"messages": [responce]}
        


        def dict_to_message(d):
            role = d["role"]
            content = d["content"]
            if role == "system" or role == "SystemMessage":
                return SystemMessage(content=content)
            elif role == "user" or role == "human":
                return HumanMessage(content=content)
            elif role == "assistant" or role == "ai":
                return AIMessage(content=content)
            else:
                raise ValueError(f"Unknown role: {role}")
        

        


        # del req.session["chat_history"]
        history_dicts = req.session.get("chat_history", [{"role": "system", "content": f"you are a good teacher, you need to clarify the content to the student in easy way to understand. student previous quiz performance and weak topics are {performance}. all this content is in json format. based on these details you need to clarify the content or doubts to student in easy way to understand. consider the student previous quiz performance and guide him to imporve in next quizes"}])

        


    # Convert to LangChain messages

        

        history_messages = [dict_to_message(m) for m in history_dicts]

        history_messages.append(HumanMessage(content=user_message))


        
        graph_builder.add_node("chatbot", chatbot)

        graph_builder.add_edge(START,"chatbot")



        # graph = graph_builder.compile(store=memory)
        graph = graph_builder.compile()

        user_mess = data

        

        

        # result = graph.invoke({"messages": [{"role": "user", "content": "user:" + user_mess}]})
        result = graph.invoke({"messages": history_messages})


        assistant_message = result["messages"][-1]
        history_messages.append(assistant_message)

        # Save back to session (convert messages to dicts for JSON)
        req.session["chat_history"] = [
            {"role": msg.type, "content": msg.content} for msg in history_messages
        ]
        req.session.modified = True


        return JsonResponse({"response": result['messages'][-1].content} , status=200)
    

     

    


    return JsonResponse({"error": "Sorry we are facing some problems with Backend"}, status=400)

