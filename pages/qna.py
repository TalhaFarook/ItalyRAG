import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
import os

st.set_page_config(page_title="QnA", page_icon="🤖")

st.title('🤖⚙️ Bot italiano')

os.environ['OPENAI_API_KEY'] = st.secrets["openai_key"]
embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small')

vectorstore  = FAISS.load_local("italian_db_1", embeddings, allow_dangerous_deserialization = True)
retriever = vectorstore.as_retriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Prompt
from langchain import hub
prompt = hub.pull("pondretti/rag-prompt-it")

# LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

def get_response(question):

    # Chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
        
    return chain.stream(
        question
    )

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Ciao, sono un bot. Come posso aiutarla?"),
    ]

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
question = st.chat_input("Type your message here...")

if question is not None and question != "":
    st.session_state.chat_history.append(HumanMessage(content=question))

    with st.chat_message("Human"):
        st.markdown(question)

    with st.chat_message("AI"):
        response = st.write_stream(get_response(question))  

    st.session_state.chat_history.append(AIMessage(content=response))  