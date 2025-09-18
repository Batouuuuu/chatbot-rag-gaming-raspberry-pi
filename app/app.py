import streamlit as st
from langchain.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings


def load_vectorbase():
    embedding_model = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    FAISS.load_local("../data/vectorstores/faiss_index", embedding_model, allow_dangerous_deserialization=True)



def main():
    st.title('Runebot')

    prompt = st.chat_input("Ecrivez votre question...")
    if prompt:
        st.write(f"User has sent the following prompt: {prompt}")
        
    message = st.chat_message("assistant")
    message.write("Salut ! Posez n'importe quelle question sur l'univers du jeu, les patchs ou le vocabulaire.")


if __name__ == "__main__":
    main()

