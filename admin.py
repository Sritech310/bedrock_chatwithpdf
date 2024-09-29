import boto3
import streamlit as st
import os
import uuid
import langchain
import pypdf



## S3 client

s3_client = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = os.getenv("BUCKET_NAME")

#Bedrock
from langchain_community.embeddings import BedrockEmbeddings

# Text splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# pdf loader
from langchain_community.document_loaders import PyPDFLoader

# import FAISS
from langchain_community.vectorstores import FAISS

bedrock_client = boto3.client(service_name="bedrock-runtime")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client = bedrock_client)



def get_unique_id():
      return str(uuid.uuid4())

## Split the pages / text into chunks
def split_text(pages, chunk_size, chunk_overlap):
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
      docs = text_splitter.split_documents(pages)
      return docs

## Create vector store
def create_vector_store(request_id, documents):
      vectorestore_faiss = FAISS.from_documents(documents, bedrock_embeddings)
      file_name=f"{request_id}.bin"
      folder_path="/temp/"
      vectorestore_faiss.save_local(index_name=file_name, folder_path=folder_path)


      ## upload to S3
      s3_client.upload_file(Filename=folder_path + "/" + file_name + ".faiss", Bucket=BUCKET_NAME, Key="my_faiss.faiss")
      s3_client.upload_file(Filename=folder_path + "/" + file_name + ".pkl", Bucket=BUCKET_NAME, Key="my_faiss.pkl")

      return True


## Main Method
def main():
    st.write("This is Admin site page for chat with PDF Bedrock")
    uploaded_file = st.file_uploader("Choose your file," "pdf")
    if uploaded_file is not None:
          request_id = get_unique_id()
          st.write(f"Reqiest ID", {request_id})
          saved_file_name = f"{request_id}.pfd"
          with open(saved_file_name, mode="wb") as w:
                w.write(uploaded_file.getvalue())
                
                loader = PyPDFLoader(saved_file_name)
                pages = loader.load_and_split()

                st.write(f"Total Pages : {len(pages)}")

    

    ## split text
    splitted_docs = split_text(pages, 1000, 200)
    st.write(f"Splitted Docs length: {len(splitted_docs)}")
    st.write("================================")
    st.write(splitted_docs[0])
    st.write("================================")
    st.write(splitted_docs[1])
    
    st.write("Crearing the vector store")
    result = create_vector_store(request_id, splitted_docs)

    if result:
          st.write("Hurrey................. PDF Stored succesfully ")
    else:
            st.write("Error, Please check logs")





if __name__ == "__main__":
        main()

        
