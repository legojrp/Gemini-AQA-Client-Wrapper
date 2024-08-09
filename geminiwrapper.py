from google.oauth2 import service_account
import google.ai.generativelanguage as glm

from google_labs_html_chunker.html_chunker import HtmlChunker
from urllib.request import urlopen

# stop the stupid logs
import os

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"



class GeminiAQA: 

    def __init__(self) -> None:

        service_account_file_name = 'programs/gemini/service_account_key.json'
        credentials = service_account.Credentials.from_service_account_file(service_account_file_name)
        scoped_credentials = credentials.with_scopes(
            ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])

        self.generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
        self.retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
        self.permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)


    def create_corpus(self, display_name, resource_name=None):
        """
        Creates a new corpus with the given display name.

        Parameters:
            display_name (str): The display name for the new corpus.

        Returns:
            str: The name of the created corpus resource.
        """
        example_corpus = glm.Corpus(display_name=display_name, name=resource_name if resource_name else None)
        create_corpus_request = glm.CreateCorpusRequest(corpus=example_corpus)

        # Make the request
        create_corpus_response = self.retriever_service_client.create_corpus(create_corpus_request)

        # Set the `corpus_resource_name` for subsequent sections.
        corpus_resource_name = create_corpus_response.name

        corpus = Corpus(corpus_resource_name, self)

        return corpus
    
    def list_corpora(self):
        """
        Fetches a list of corpora from the retriever service client.

        Returns:
            The response containing the list of corpora. -- Keep in mind it has more than just resource names!
        """
        list_corpus_request = glm.ListCorporaRequest()
        list_corpus_response = self.retriever_service_client.list_corpora(list_corpus_request)
        return list_corpus_response

    def delete_corpus(self, corpus_resource_name):
        """
        Deletes a corpus resource from the retriever service client.

        Args:
            corpus_resource_name (str): The name of the corpus resource to delete.

        Returns:
            google.longrunning.operations_pb2.Operation: The response from the deletion operation.
        """
        delete_corpus_request = glm.DeleteCorpusRequest(name=corpus_resource_name)
        delete_corpus_response = self.retriever_service_client.delete_corpus(delete_corpus_request)
        return delete_corpus_response

    def get_corpus(self, corpus_resource_name):
        """
        Retrieves a corpus resource from the retriever service client.

        Args:
            corpus_resource_name (str): The name of the corpus resource to retrieve.

        Returns:
            Corpus: The retrieved corpus resource.
        """
        return Corpus(corpus_resource_name, self)
    
    

    

class Corpus:

    def __init__(self, corpus_resource_name, GeminiAQA) -> None:
        self.corpus_resource_name = corpus_resource_name
        self.GeminiAQA = GeminiAQA
        # Print the response
        

    def get_display_name(self):
        """
        Retrieves the display name of a corpus.

        Returns:
            str: The display name of the corpus.
        """
        get_corpus_request = glm.GetCorpusRequest(name=self.corpus_resource_name)
        response = self.GeminiAQA.retriever_service_client.get_corpus(get_corpus_request)
        return response.display_name
    
    def list_documents(self):
        """
        Retrieves a list of documents in a corpus.

        Returns:
            list: A list of document names.
        """
        list_documents_request = glm.ListDocumentsRequest(parent=self.corpus_resource_name)
        response = self.GeminiAQA.retriever_service_client.list_documents(list_documents_request)
        return response
    
    def create_document(self, document_display_name, document_resource_name=None, metadata=None):
        """
        Creates a new document in a corpus.

        Args:
            document_display_name (str): The display name of the new document.
            document_resource_name (str, optional): The name of the document resource. Defaults to None.
            metadata (dict, optional): The metadata of the document. Defaults to None.

        Returns:
            Document: The created document.
        """
        if metadata is not None:
            document_metadata = []
            for key, value in metadata.items():
                document_metadata.append(glm.CustomMetadata(key=key, string_value=value))
            

        document = glm.Document(display_name=document_display_name, name=document_resource_name if document_resource_name else None)
        if metadata is not None:
            document.custom_metadata.extend(document_metadata)
        create_document_request = glm.CreateDocumentRequest(document=document, parent=self.corpus_resource_name)
        create_document_response = self.GeminiAQA.retriever_service_client.create_document(create_document_request)
        return Document(create_document_response.name, self)
    
    def generate_answer(self, user_query, mode="ABSTRACTIVE"): # or EXTRACTIVE or VERBOSE
        """
        Generates an answer to a given text.

        Args:
            user_query (str): The text to generate an answer for.
            mode (str, optional): The mode of the answer. Defaults to "ABSTRACTIVE".

        Returns:
            str: The generated answer.
        """

        model = "models/aqa"

        content = glm.Content(parts=[glm.Part(text=user_query)])
        retriever_config = glm.SemanticRetrieverConfig(source=self.corpus_resource_name, query=content)
        req = glm.GenerateAnswerRequest(model=model,
                                        contents=[content],
                                        semantic_retriever=retriever_config,
                                        answer_style=mode)
        aqa_response = self.GeminiAQA.generative_service_client.generate_answer(req)
        return aqa_response

    def delete_document(self, document_resource_name):
        """
        Deletes a document resource from the retriever service client.

        Args:
            document_resource_name (str): The name of the document resource to delete.

        Returns:
            google.longrunning.operations_pb2.Operation: The response from the deletion operation.
        """
        delete_document_request = glm.DeleteDocumentRequest(name=document_resource_name)
        delete_document_response = self.GeminiAQA.retriever_service_client.delete_document(delete_document_request)
        return delete_document_response
    

class Document:
    def __init__(self, document_resource_name, corpus) -> None:
        self.document_resource_name = document_resource_name
        self.corpus = corpus
    
    def list_chunks(self):

        list_chunks_request = glm.ListChunksRequest(parent=self.document_resource_name)
        response = self.corpus.GeminiAQA.retriever_service_client.list_chunks(list_chunks_request)
        return response
    
    def delete_chunk(self, chunk_resource_name):
        """
        Deletes a chunk resource from the retriever service client.

        Args:
            chunk_resource_name (str): The name of the chunk resource to delete.

        Returns:
            google.longrunning.operations_pb2.Operation: The response from the deletion operation.
        """
        delete_chunk_request = glm.DeleteChunkRequest(name=chunk_resource_name)
        delete_chunk_response = self.corpus.GeminiAQA.retriever_service_client.delete_chunk(delete_chunk_request)
        return delete_chunk_response

    def ingest_chunk(self, text):
        """
        Ingests a chunk of text into a document.

        Args:
            text (str): The text to ingest.

        Returns:
            google.longrunning.operations_pb2.Operation: The response from the ingestion operation.
        """
        if len(text) < 200:
            chunk = glm.Chunk(data={"string_value": text})

            create_chunk_request = glm.CreateChunkRequest(chunk=chunk, parent=self.document_resource_name)


            response = self.corpus.GeminiAQA.retriever_service_client.create_chunk(create_chunk_request)

        else:
            passages = [text[i:i+400] for i in range(0, len(text), 400)]
            chunks= []
            for passsage in passages:
                chunk = glm.Chunk(data={"string_value": passsage})
                chunks.append(chunk)


            create_chunk_requests = []
            for chunk in chunks:
                create_chunk_requests.append(glm.CreateChunkRequest(parent=self.document_resource_name, chunk=chunk))

        # Make the request
# Split create_chunk_requests into batches of 100
            batched_requests = [create_chunk_requests[i:i + 100] for i in range(0, len(create_chunk_requests), 100)]
            
            for batch in batched_requests:
                request = glm.BatchCreateChunksRequest(parent=self.document_resource_name, requests=batch)
                response = self.corpus.GeminiAQA.retriever_service_client.batch_create_chunks(request)


    
        return response
    
    def ingest_url(self, url):

        with(urlopen(url)) as f:
            html = f.read().decode("utf-8")
        chunker = HtmlChunker(
        max_words_per_aggregate_passage=200,
        greedily_aggregate_sibling_nodes=True,
        html_tags_to_exclude={"noscript", "script", "style"},
        )
        passages = chunker.chunk(html)
        print(passages)
        chunks = []
        for passage in passages:
            chunk = glm.Chunk(data={'string_value': passage})
            chunks.append(chunk)
        
        create_chunk_requests = []
        for chunk in chunks:
            create_chunk_requests.append(glm.CreateChunkRequest(parent=self.document_resource_name, chunk=chunk))

        # Make the request
# Split create_chunk_requests into batches of 100
        batched_requests = [create_chunk_requests[i:i + 100] for i in range(0, len(create_chunk_requests), 100)]
        
        for batch in batched_requests:
            request = glm.BatchCreateChunksRequest(parent=self.document_resource_name, requests=batch)
            response = self.corpus.GeminiAQA.retriever_service_client.batch_create_chunks(request)

        return response
    

    def ingest_wikipedia(self, wikipedia_url):
        """
        Ingests a Wikipedia article into a document.

        Args:
            wikipedia_url (str): The URL of the Wikipedia article.

        Returns:
            google.longrunning.operations_pb2.Operation: The response from the ingestion operation.
        """
        import wikipedia

        article = wikipedia.page(wikipedia_url)
        text = article.content
        # return text
        return self.ingest_chunk(text)
    