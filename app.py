import streamlit as st

st.title('Runebot')

prompt = st.chat_input("Ecrivez votre question...")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
    
message = st.chat_message("assistant")
message.write("Salut ! Posez n'importe quelle question sur l'univers du jeu, les patchs ou le vocabulaire.")


# with st.chat_message("user"):
#     st.write("Hello 👋")

