

# GeminiAQA
GeminiAQA is a Python module that interacts with Google’s AI Generative Language Model. It allows you to create and manage corpora, documents, and their respective chunks. The module also provides functionalities to generate answers based on user queries and manage different Google Cloud resources.

I have not seen any other support outside of this. If there is, tell me.

## Features

- **Create, List, and Delete Corpora**: Easily manage corpora resources.
- **Create, List, and Delete Documents**: Manage documents within a corpus.
- **Chunk Management**: Ingest, list, and delete chunks within a document.
- **Text Generation**: Generate answers based on user queries.
- **HTML & Wikipedia Ingestion**: Ingest content from URLs and Wikipedia articles.

## Installation

To use GeminiAQA, you must first install the necessary dependencies:

```bash
pip install google-auth google-cloud google-labs-html-chunker wikipedia
```

Make sure to set up a Google Cloud service account and save the service account key in `programs/gemini/service_account_key.json`. You can find detailed instructions and documentation on how to set up a Google Cloud service account [here](https://ai.google.dev/gemini-api/docs/semantic_retrieval).
## Usage

### Initialization


```python
from gemini_aqa import GeminiAQA

# Initialize the GeminiAQA client
gemini = GeminiAQA()
```

### Create a Corpus

```python
corpus = gemini.create_corpus(display_name="MyCorpus")
```

### List Corpora

```python
corpora = gemini.list_corpora()
```

### Delete a Corpus

```python
gemini.delete_corpus(corpus_resource_name="corpus_resource_name")
```

### Create a Document

```python
document = corpus.create_document(document_display_name="MyDocument")
```

### List Documents in a Corpus

```python
documents = corpus.list_documents()
```

### Generate an Answer

```python
answer = corpus.generate_answer(user_query="What is the capital of France?")
```

### Ingest Text as a Chunk

```python
response = document.ingest_chunk(text="This is a sample text to ingest.")
```

### Ingest Content from a URL

```python
response = document.ingest_url(url="https://example.com")
```

### Ingest a Wikipedia Article

```python
response = document.ingest_wikipedia(wikipedia_url="https://en.wikipedia.org/wiki/Python_(programming_language)")
```

## Suppressing Logs

To suppress unnecessary logs, the environment variables are set as follows:

```python
import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
```

If you dont want to deal with these envs, just delete them in the code.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Contact

Just use [Github Issues](issues) to contact me honestly. If its private, use legojrp@gmail.com
