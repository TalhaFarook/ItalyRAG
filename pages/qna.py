import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
import os
from navigation import make_sidebar

make_sidebar()

st.title('🤖⚙️ Bot italiano')

os.environ['OPENAI_API_KEY'] = st.secrets["openai_key"]
embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small')

vectorstore  = FAISS.load_local("documenti_italiani", embeddings, allow_dangerous_deserialization = True)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Prompt
from langchain import hub
prompt_template = hub.pull("pondretti/rag-prompt-it")

# LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

def get_response(results):

    context_text = "\n\n".join([doc.page_content for doc, _score in results])

    prompt = prompt_template.format(context=context_text, question=question)

    return llm.stream(
        prompt
    )

def get_sources(question, k = 2):

    results = vectorstore.similarity_search_with_score(question, k = k)

    return results

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
        sources = get_sources(question)
        response = st.write_stream(get_response(sources))  

    st.session_state.chat_history.append(AIMessage(content=response))  

    with st.chat_message("AI"):
        sources_list = [doc.metadata.get("source", None).split('/')[-1] + ': P# ' + str(doc.metadata.get("page", None)+1) for doc, _score in sources]
        formatted_sources = f"Fonti: {sources_list}"
        st.markdown(formatted_sources)