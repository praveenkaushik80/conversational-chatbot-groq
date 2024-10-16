import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Get Groq API key
    # groq_api_key = os.environ['GROQ_API_KEY']

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # st.sidebar.title('Customization')
    model = st.sidebar.selectbox(
        'Choose a model',
        # ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
        [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-11b-text-preview",
            "llama-3.2-90b-text-preview",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it"
        ]
    )
    groq_api_key = st.text_input("Groq API Key", type="password")
    if not groq_api_key:
        st.info("Please add your Groq API key to continue.", icon="🗝️")
    else:
        system_prompt = st.sidebar.text_input("System prompt:")
        if system_prompt:
            pass
        else:
            prompt = ChatPromptTemplate.from_template(
            """
            Answer the questions based on the provided context only.
            Please provide the most accurate response based on the question.
            <context>
            {context}
            <context>
            Questions: {input}
            """,
            MessagesPlaceholder(
                variable_name="chat_history"
            ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

            HumanMessagePromptTemplate.from_template(
                "{human_input}"
            ),  # This template is where the user's current input will be injected into the prompt.
            )
        conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)
    
        memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
    
        user_question = st.text_input("Ask a question:")
    
        # session state variable
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history=[]
        else:
            for message in st.session_state.chat_history:
                memory.save_context(
                    {'input':message['human']},
                    {'output':message['AI']}
                    )
    
    
        # Initialize Groq Langchain chat object and conversation
        groq_chat = ChatGroq(
                groq_api_key=groq_api_key, 
                model_name=model
        )
    
        # If the user has asked a question,
        if user_question:
        
            # Construct a chat prompt template using various components
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=system_prompt
                    ),  # This is the persistent system prompt that is always included at the start of the chat.
        
                    MessagesPlaceholder(
                        variable_name="chat_history"
                    ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.
        
                    HumanMessagePromptTemplate.from_template(
                        "{human_input}"
                    ),  # This template is where the user's current input will be injected into the prompt.
                ]
            )
        
            # Create a conversation chain using the LangChain LLM (Language Learning Model)
            conversation = LLMChain(
                llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
                prompt=prompt,  # The constructed prompt template.
                verbose=True,   # Enables verbose output, which can be useful for debugging.
                memory=memory,  # The conversational memory object that stores and manages the conversation history.
            )
            
            # The chatbot's answer is generated by sending the full prompt to the Groq API.
            response = conversation.predict(human_input=user_question)
            message = {'human':user_question,'AI':response}
            st.session_state.chat_history.append(message)
            st.write("Chatbot:", response)

if __name__ == "__main__":
    main()





