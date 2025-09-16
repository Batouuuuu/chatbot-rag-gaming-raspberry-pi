""" This script will create embeddings from the chunking, the 3 chunked_data_csv 
will merge to create only one index vectorebase
=================
N.B : Time process is very long approximative -25min
"""

from langchain.schema import Document
from langchain_community.vectorstores import FAISS  ## used faiss cpu for my setup
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
import pandas as pd
import os


def convert_csv_to_dataframe(file_csv : os.PathLike) -> pd.DataFrame:
    df = pd.read_csv(file_csv, sep="\t")
    return df


def build_document(row : pd.Series) -> Document:
    metadata = {col: row[col] for col in row.index if col != "page_content"}
    return Document(page_content=row["page_content"], metadata=metadata)


def embedding(dataframe: pd.DataFrame, vectorebase_file: os.PathLike) -> None:

    documents = [build_document(row) for _, row in dataframe.iterrows()]

    embedding_model = SentenceTransformerEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
 
    vectorstore = FAISS.from_documents(documents, embedding_model)
    vectorstore.save_local(vectorebase_file)


def main():
    
    lore_df = convert_csv_to_dataframe("../data/processed/lore_chunked.csv")
    lore_df["Type"] = "Lore"

    lexique_df = convert_csv_to_dataframe("../data/processed/lexic_processed.csv")
    lexique_df["Type"] = "Lexique"

    patch_df = convert_csv_to_dataframe("../data/processed/patchs.csv")
    patch_df["Type"] = "Patch"

    merged_df = pd.concat([lore_df, lexique_df, patch_df], ignore_index=True)
    merged_df = merged_df.dropna(subset=["page_content"]) ##delete the 2 empty lines

    embedding(merged_df, "../data/vectorstores/faiss_index")


if __name__ == "__main__":
    main()