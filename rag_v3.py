from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_text_splitters import CharacterTextSplitter

llm = Ollama(model="mistral")

loader = PyPDFLoader("interview.pdf")
splited_docs = loader.load_and_split()

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_db = Chroma.from_documents(
    documents=splited_docs,
    embedding=embeddings,
    persist_directory="db",
    collection_name="interview",
)

retriever = vector_db.as_retriever(search_kwargs={"k": 3})

system_prompt = "現在開始使用我提供的情境來回答，只能使用繁體中文，不要有簡體中文字。如果你不確定答案，就說不知道。情境如下:\n\n{context}"
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "問題: {input}"),
    ]
)

document_chain = create_stuff_documents_chain(llm, prompt_template)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

context = []
input_text = input("您想問什麼問題？\n>>> ")

while input_text.lower() != "bye":
    response = retrieval_chain.invoke({"input": input_text, "context": context})
    context = response["context"]

    print(response["answer"])

    input_text = input(">>> ")


text_splitter = CharacterTextSplitter(chunk_size=20, chunk_overlap=5)
documents = text_splitter.split_documents(splited_docs)

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_db = Chroma.from_documents(
    documents=splited_docs,
    embedding=embeddings,
    persist_directory="db",
    collection_name="interview",
)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

system_prompt = "現在開始使用我提供的情境來回答，只能使用繁體中文，不要有簡體中文字。如果你不確定答案，就說不知道。情境如下:\n\n{context}"
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "問題: {input}"),
    ]
)

chain_document = create_stuff_documents_chain(llm, prompt)
chain_retrieval = create_retrieval_chain(retriever, chain_document)

context = []
input_prompt = input("您想問什麼問題？\n>>> ")

while input_prompt.lower() != "bye":
    response = chain_retrieval.invoke({"input": input_prompt, "context": context})
    context = response["context"]

    print(response["answer"])

    input_prompt = input(">>> ")