# RAG Project - Embedding Model

This project uses sentence-transformers to generate embeddings from JSON files using the `paraphrase-multilingual-MiniLM-L12-v2` model.

## Installation

### Using Virtual Environment (Recommended)

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. When done, deactivate the virtual environment:
```bash
deactivate
```

**Note:** Remember to activate the virtual environment (`source venv/bin/activate`) each time you work on this project.

## Troubleshooting

### Segmentation Fault / OpenMP Errors on macOS

If you encounter errors like:
```
OMP: Error #179: Function pthread_mutex_init failed
Segmentation fault
```

This is a known issue with OpenMP threading on macOS. The project automatically sets environment variables to prevent this:

- `OMP_NUM_THREADS=1` - Disables OpenMP threading
- `MKL_NUM_THREADS=1` - Disables MKL threading  
- `NUMEXPR_NUM_THREADS=1` - Disables NumExpr threading
- `TOKENIZERS_PARALLELISM=false` - Disables tokenizer multiprocessing

These are set automatically in the example scripts. If you're running scripts directly, make sure to set these before importing libraries.

### Semaphore Leak Warnings

Warnings about leaked semaphores are harmless and are automatically suppressed. They occur due to multiprocessing resources not being cleaned up immediately, but don't affect functionality.

## Debugging

### Quick Start (VS Code)

1. **Set a breakpoint**: Click in the left margin next to a line number (or press `F9`)
2. **Start debugging**: Press `F5` and select a configuration
3. **Step through code**: Use `F10` (step over), `F11` (step into), `Shift+F11` (step out)
4. **Inspect variables**: Hover over variables or check the "Variables" panel

### Available Debug Configurations

- **Python: Current File** - Debug the currently open file
- **Example: Embedding Model** - Debug the embedding model example
- **Example: FAISS Indexer** - Debug the FAISS indexer example
- **Example: Semantic Retrieval** - Debug the semantic retrieval example
- **Embedding Model CLI** - Debug the embedding model CLI with arguments
- **FAISS Indexer CLI** - Debug the FAISS indexer CLI with arguments
- **Semantic Retrieval CLI** - Debug the semantic retrieval CLI with arguments

### Other Debugging Methods

- **Debug Helper Script**: `python debug.py --component all`
- **Python Debugger (pdb)**: Add `import pdb; pdb.set_trace()` in your code
- **IPython Debugger**: Add `import ipdb; ipdb.set_trace()` (install with `pip install ipdb`)

For detailed debugging instructions, see [DEBUG_GUIDE.md](DEBUG_GUIDE.md).

### PyCharm

PyCharm run configurations are available in `.idea/runConfigurations/`:
- Embedding Model
- Semantic Retrieval

To use:
1. Open the project in PyCharm
2. Go to Run → Edit Configurations
3. Import the configurations from `.idea/runConfigurations/`

## Running Scripts

All scripts should be run from the project root directory (`/Users/wangxiaoliang/dev/rag-project`):

```bash
# Run example scripts
python examples/example_usage.py
python examples/faiss_example.py
python examples/semantic_retrieval_example.py

# Run main scripts
python src/embedding_model.py --input data/sample_data.json --output data/embeddings.json
python src/faiss_indexer.py --embeddings data/embeddings.json --index data/faiss_index.index --build
python src/semantic_retrieval.py --index data/faiss_index.index --query "machine learning" --top-k 5
```

The example scripts automatically add the project root to the Python path, so imports will work correctly.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

Generate embeddings from a JSON file:

```bash
python src/embedding_model.py --input data/sample_data.json --output data/embeddings.json
```

Options:
- `--input, -i`: Path to input JSON file (required)
- `--output, -o`: Path to save embeddings (optional)
- `--text-key, -k`: Key to extract text from JSON (auto-detects if not provided)
- `--batch-size, -b`: Batch size for encoding (default: 32)
- `--model, -m`: Model name (default: paraphrase-multilingual-MiniLM-L12-v2)

### Python API

```python
from src.embedding_model import EmbeddingModel

# Initialize the model
embedding_model = EmbeddingModel()

# Process a JSON file
results = embedding_model.process_json_file(
    json_path='data/sample_data.json',
    text_key='content',  # Optional: specify which key contains text
    output_path='data/embeddings.json'  # Optional: save embeddings
)

# Access results
texts = results['texts']
embeddings = results['embeddings']
print(f"Generated {len(texts)} embeddings with dimension {embeddings.shape[1]}")
```

## File Format Support

The project supports both JSON and CSV file formats.

### JSON File Format

The script supports various JSON structures:

1. **List of objects** (recommended):
```json
[
  {"text": "First sentence", "id": 1},
  {"text": "Second sentence", "id": 2}
]
```

2. **List of strings**:
```json
["First sentence", "Second sentence"]
```

3. **Single object**:
```json
{"content": "Some text", "title": "Title"}
```

The script auto-detects common text fields like: `text`, `content`, `description`, `title`, `body`, `message`.

### CSV File Format

CSV files should have a header row with column names. The script will:
- Use the specified column (default: `content`) for embedding generation
- Store all columns as metadata

Example CSV:
```csv
id,title,content,category
1,Introduction to ML,Machine learning is...,AI
2,NLP Basics,Natural Language Processing...,AI
```

Usage:
```python
# Process CSV file
results = embedding_model.process_csv_file(
    csv_path='data/sample_data.csv',
    text_key='content',  # Column name to use for embeddings
    output_path='data/embeddings.json'
)

# Or use the unified method (auto-detects file type)
results = embedding_model.process_file('data/sample_data.csv')
```

## Output Format

The embeddings are saved as JSON with the following structure:

```json
{
  "texts": ["text1", "text2", ...],
  "embeddings": [[...], [...], ...],
  "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
  "num_texts": 2,
  "embedding_dim": 384
}
```

## FAISS Indexing

After generating embeddings, you can build a FAISS index for efficient similarity search.

### Command Line

Build a FAISS index from embeddings:

```bash
python src/faiss_indexer.py --embeddings data/embeddings.json --index data/faiss_index.index --build
```

Search using a query text:

```bash
python src/faiss_indexer.py --index data/faiss_index.index --query "machine learning" --k 5
```

Options:
- `--embeddings, -e`: Path to embeddings JSON file (required for --build)
- `--index, -i`: Path to save/load FAISS index (default: data/faiss_index.index)
- `--metric, -m`: Distance metric - "cosine" or "l2" (default: cosine)
- `--build`: Build index from embeddings
- `--query, -q`: Query text for search
- `--k`: Number of results to return (default: 5)
- `--model`: Model name for query encoding (default: paraphrase-multilingual-MiniLM-L12-v2)

### Python API

```python
from src.faiss_indexer import FAISSIndexer
from src.embedding_model import EmbeddingModel

# Build index from embeddings file
indexer = FAISSIndexer(metric='cosine')
indexer.build_index('data/embeddings.json')

# Save index for later use
indexer.save_index('data/faiss_index.index')

# Load index
indexer = FAISSIndexer()
indexer.load_index('data/faiss_index.index')

# Search by text (requires embedding model)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

results = indexer.search_by_text("machine learning", model, k=5)
for result in results:
    print(f"Similarity: {result['similarity']:.4f}")
    print(f"Text: {result['text']}\n")

# Search by embedding vector
query_embedding = model.encode(["your query text"], convert_to_numpy=True)
distances, indices = indexer.search(query_embedding, k=5)
```

### Index Features

- **Metrics**: Supports cosine similarity and L2 distance
- **Efficient Search**: Fast approximate nearest neighbor search
- **Persistent Storage**: Save and load indices from disk
- **Metadata Support**: Attach metadata to each indexed item
- **Batch Search**: Search multiple queries at once

## Semantic Retrieval

The semantic retrieval model provides a high-level interface for searching terms and sentences using SentenceTransformer embeddings and FAISS indexing.

### Command Line

Build and search in one step:

```bash
python src/semantic_retrieval.py --json data/sample_data.json --query "machine learning" --top-k 5 --build
```

Or use an existing index:

```bash
python src/semantic_retrieval.py --index data/faiss_index.index --query "neural networks" --top-k 5
```

Options:
- `--json, -j`: Path to input JSON file (for building index)
- `--index, -i`: Path to FAISS index file
- `--embeddings, -e`: Path to embeddings JSON file
- `--query, -q`: Query term or sentence (required)
- `--top-k, -k`: Number of results to return (default: 5)
- `--min-similarity, -m`: Minimum similarity threshold (optional)
- `--model`: Model name (default: paraphrase-multilingual-MiniLM-L12-v2)
- `--build`: Build index from JSON file
- `--text-key`: Key to extract text from JSON

### Python API

```python
from src.semantic_retrieval import SemanticRetrieval

# Option 1: Build from JSON or CSV file (auto-detects file type)
retrieval = SemanticRetrieval()
retrieval.build_index_from_file(
    file_path='data/sample_data.json',  # or 'data/sample_data.csv'
    text_key='content',
    index_output='data/faiss_index.index'
)

# The build_index_from_file() method automatically detects JSON or CSV based on file extension

# Option 2: Load existing index
retrieval = SemanticRetrieval(index_path='data/faiss_index.index')

# Search for a term
results = retrieval.find_similar_terms("machine learning", top_k=5, min_similarity=0.5)
for result in results:
    print(f"Similarity: {result['similarity']:.4f}")
    print(f"Text: {result['text']}\n")

# Search for a sentence
results = retrieval.find_similar_sentences(
    "How do neural networks work?",
    top_k=3,
    min_similarity=0.6
)

# General search
results = retrieval.search("vector embeddings", top_k=5, min_similarity=0.4)

# Batch search (multiple queries)
queries = ["AI", "deep learning", "NLP"]
batch_results = retrieval.batch_search(queries, top_k=3)
```

### Retrieval Features

- **Unified Interface**: Simple API for semantic search
- **Term & Sentence Search**: Optimized methods for both short terms and long sentences
- **Similarity Thresholding**: Filter results by minimum similarity score
- **Batch Processing**: Search multiple queries efficiently
- **Metadata Support**: Access original document metadata
- **Flexible Initialization**: Build from JSON or load existing index

## Model Information

- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Embedding Dimension**: 384
- **Languages**: Supports multiple languages
- **Use Case**: Semantic similarity, clustering, retrieval
