import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

import dotenv
dotenv.load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
doc_file = os.path.join(current_dir, 'documents', 'hongloumeng.pdf')
db_path = os.path.join(current_dir, 'db', 'chromadb')

# Create ChromaDB
# embeddings = OpenAIEmbeddings(model='text-embedding-3-small', api_key=os.environ['OPENAI_API_KEY'])
embeddings = HuggingFaceEmbeddings(
    model_name="shibing624/text2vec-base-chinese"
)

if not os.path.exists(db_path):
    print("Creating ChromaDB...")

    if not os.path.exists(doc_file):
        raise FileNotFoundError(f"Document file {doc_file} does not exist.")

    loader = PyMuPDFLoader(doc_file)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    # can add metadata for each chunk
    # for i, doc in enumerate(docs):
    #     doc.metadata = {"chunk_id": i}

    print(f"Splitting {len(documents)} documents into {len(docs)} chunks...")
    print(f"chunks[100]: {docs[100]}")

    Chroma.from_documents(docs, embeddings, persist_directory=db_path)

db = Chroma(persist_directory=db_path, embedding_function=embeddings)
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)
