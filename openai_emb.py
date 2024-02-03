from openai.embeddings_utils import distances_from_embeddings

# Create example embeddings
embeddings = [
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6],
    [0.7, 0.8, 0.9]
]

# Calculate distances from embeddings
distances = distances_from_embeddings(embeddings)

print(distances)

### add open ai key

# %%
import os
from openai import OpenAI

client = OpenAI(api_key= os.environ.get("OPENAI_API_KEY"))


# %%
