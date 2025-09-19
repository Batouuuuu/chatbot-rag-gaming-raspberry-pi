import streamlit as st
from langchain.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from mistralai import Mistral
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
from langchain.schema import Document
import os
import pandas as pd


load_dotenv()
api_key = os.environ.get("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


df = pd.read_csv("../data/processed/lore_chunked.csv", sep="\t")


def get_user_query() -> str:
    user_query = st.chat_input("Ecrivez votre question sur League of Legends...")
    return user_query


def matching_querry(query: str)-> pd.DataFrame:
    """Using rapid fuzz"""
    splitted_input = query.split()
    all_names = df["Name"].unique()

    for element in splitted_input:
        best_match_name, score, _ = process.extractOne(element.upper(), all_names, scorer=fuzz.token_ratio)
        if score > 90:
            champion_detected = best_match_name

    chunks_for_champion = df[df["Name"] == champion_detected]
    return chunks_for_champion



# Créer un vectorstore temporaire pour ce champion
def retrieval_faiss_filtering(embedding_model, dataframe: pd.DataFrame, query) -> str:
    vectorstore_filtered = FAISS.from_documents(
        [Document(page_content=row["page_content"], metadata=row.to_dict())
        for _, row in dataframe.iterrows()],
        embedding_model
    )
    results = vectorstore_filtered.similarity_search(query, k=10)
    retrieved_chunk = "\n".join([r.page_content for r in results])
    return retrieved_chunk



def prompt(user_query: str, retrieved_chunk: str) -> str:
    prompt = f"""
    Le contexte de la question est en dessous.
    ---------------------
    {retrieved_chunk}
    ---------------------
    Tu es un expert geek et connais tout l'histoire du jeu League of Legends. En t'appuyant sur le contexte la question et de la question posée, peux tu répondres de façon claire et concise. Si le contexte n'est pas pertinent ou n'est pas en rapport avec le jeu dis que tu ne peux pas répondre
    Query: {user_query}
    Answer:
    """
    return prompt



def run_mistral(user_message, model="mistral-large-latest"):

    messages = [
        {
            "role": "user", "content": user_message
        }
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    
    return (chat_response.choices[0].message.content)



def main():
    embedding_model = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    FAISS.load_local("../data/vectorstores/faiss_index", embedding_model, allow_dangerous_deserialization=True)

    st.title('Runebot')

    if "messages" not in st.session_state:
        st.session_state.messages = []


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    with st.chat_message("assistant"):
        st.write("Salut ! Posez n'importe quelle question sur l'univers de League of Legends, les patchs ou le vocabulaire.")
   
   
    user_query = get_user_query()
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Wait for it...", show_time=True):
                chunks = matching_querry(user_query)
                context = retrieval_faiss_filtering(embedding_model, chunks, user_query)
                final_prompt = prompt(user_query, context)
                response = run_mistral(final_prompt)
                st.write(response)
        

if __name__ == "__main__":
    main()

