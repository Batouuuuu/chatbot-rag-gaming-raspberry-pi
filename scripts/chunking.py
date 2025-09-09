from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
import pandas as pd
import os 

def convert_csv_to_dataframe(filepath: os.Pathlike) -> pd.Dataframe:
    
    df = pd.read_csv(filepath)
    df.fillna("L'éditeur Riot Games n'a pas encore fourni l'histoire de ce champion", inplace = True) ##fill the empty stories
    return df


def chuncking_page_content(dataframe : pd.DataFrame) -> List[Document]:
    """Chuncking the Biography and then the story with langchain document"""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        length_function=len,
        is_separator_regex=False,
    )

    documents = []

    for index, row in dataframe.iterrows():
        text_biography = row['Biography']
        text_story = row['Story']
        texts_bio = text_splitter.create_documents([text_biography],[{"Source": "Biography", "Name": row['Name'], "Region": row['Region'], "Sum_up": row['SumUp']}])
        text_story = text_splitter.create_documents([text_story], [{"Source": "Story", "Name": row['Name'], "Region": row['Region'], "Sum_up": row['SumUp']}])
        documents.extend(texts_bio)
        documents.extend(text_story)

    return documents


def dataframe_to_csv(file_path: os.PathLike,liste_documents: List) -> None:
    liste = []
    for doc in liste_documents:
        row = {
    "page_content": doc.page_content,
    "Source": doc.metadata["Source"],
    "Name": doc.metadata["Name"],
    "Region": doc.metadata["Region"],
    "Sum_up": doc.metadata["Sum_up"]
        }
        liste.append(row)

    df_lore = pd.DataFrame(liste)
    df_lore.to_csv(file_path, sep='\t')


def main():

    dataframe_lore = convert_csv_to_dataframe("../data/raw/lore.csv")
    liste_lore_chunked = chuncking_page_content(dataframe_lore)
    dataframe_to_csv("../data/processed/lore_chunked.csv", liste_lore_chunked)


if __name__ == "__main__":
    main()