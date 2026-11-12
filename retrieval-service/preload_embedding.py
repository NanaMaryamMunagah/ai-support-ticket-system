from huggingface_hub import snapshot_download
from VectorStore import MODEL_REPOSITORY, MODEL_REVISION, MODEL_FILES
path = snapshot_download(repo_id=MODEL_REPOSITORY, revision=MODEL_REVISION, allow_patterns=MODEL_FILES)
print('Pinned embedding model cached:', path)
