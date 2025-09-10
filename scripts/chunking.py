"""
This script chunk the dataframes lore and patchs and saves it into csv  
NB : we don't actualy chunk the lexic.csv because it's already a dict so not very long information,
so chunking this one is not necessary
 """

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
import pandas as pd
import json
import os

def convert_csv_to_dataframe(filepath: os.PathLike, dataset_type: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    if dataset_type == "lore":
        df.fillna("L'éditeur Riot Games n'a pas encore fourni l'histoire de ce champion", inplace = True) ##fill the empty stories
        return df
    
    elif dataset_type == "lexic":
        df["page_content"] = df["Word"] + " : " + df["Definition"]
        return df 
    
    elif dataset_type == "patch":
        df["page_content"] = (
        "Patch " + df["Number"].astype(str) + " : " +
        df["Sum_up"] + "\n\n" +
        "Skins : " + df["Skins"] + "\n\n" +
        "Changements : " + df["Content"]
    )
        return df



def chuncking_page_content(dataframe : pd.DataFrame, data_type : str) -> List[Document]:
    """Chuncking the Biography and then the story with langchain document"""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        length_function=len,
        is_separator_regex=False,
    )

    documents = []
    if data_type == "lore":
        for index, row in dataframe.iterrows():
            text_biography = row['Biography']
            text_story = row['Story']
            texts_bio = text_splitter.create_documents([text_biography],[{"Source": "Biography", "Name": row['Name'], "Region": row['Region'], "Sum_up": row['SumUp']}])
            text_story = text_splitter.create_documents([text_story], [{"Source": "Story", "Name": row['Name'], "Region": row['Region'], "Sum_up": row['SumUp']}])
            documents.extend(texts_bio)
            documents.extend(text_story)
        return documents
    
    elif data_type == "patch":
        for index, row in dataframe.iterrows():
            text_patch = row['page_content']
            text_patch_chunked = text_splitter.create_documents([text_patch],[{"Number": row['Number'], "Sum_up": row['Sum_up'], "Skins": row['Skins'], "Content": row['Content']}])
            documents.extend(text_patch_chunked)
        return documents 


def save_dataframe_lore_to_csv(file_path: os.PathLike, liste_documents: List[Document]) -> None:
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
    

import json
import pandas as pd

def save_patch_chunks_to_csv(file_path, liste_documents):
    """Save the chunking and serialise the key 'Content' en JSON in oder to be stockable in a CSV. """
    rows = []
    for doc in liste_documents:
        meta = doc.metadata.copy()
        content = meta.get("Content")

        if isinstance(content, dict):
            meta["Content"] = json.dumps(content, ensure_ascii=False)

        rows.append({
            "page_content": doc.page_content,
            "Number": meta.get("Number"),
            "Sum_up": meta.get("Sum_up"),
            "Skins": meta.get("Skins"),
            "Content": meta.get("Content")
        })

    df = pd.DataFrame(rows)
    df.to_csv(file_path, sep="\t", index=False)


def dataframe_lexic_to_csv(file_path: os.PathLike, df: pd.DataFrame) -> None:
    df.to_csv(file_path, sep="\t", index=False)


def main():

    dataframe_lore = convert_csv_to_dataframe("../data/raw/lore.csv", "lore")
    list_lore_chunked = chuncking_page_content(dataframe_lore, "lore")
    save_dataframe_lore_to_csv("../data/processed/lore_chunked.csv", list_lore_chunked)

    dataframe_lexicon = convert_csv_to_dataframe("../data/raw/lexic.csv", "lexic")
    dataframe_lexic_to_csv("../data/processed/lexic_processed.csv", dataframe_lexicon)
    
    dataframe_patch = convert_csv_to_dataframe("../data/raw/patchs.csv", "patch")
    list_patch_chunk = chuncking_page_content(dataframe_patch, "patch")
    save_patch_chunks_to_csv("../data/processed/patchs.csv", list_patch_chunk)


if __name__ == "__main__":
    main()