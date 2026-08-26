"""Image encoding (ResNet50) and cosine similarity matching."""

from __future__ import annotations

import base64
from io import BytesIO

import numpy as np
import requests
import torch
import torchvision.transforms as transforms
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from torchvision.models import ResNet50_Weights, resnet50


class ImageProcessor:
    def __init__(
        self,
        image_size=(224, 224),
        norm_mean=None,
        norm_std=None,
    ):
        norm_mean = norm_mean or [0.485, 0.456, 0.406]
        norm_std = norm_std or [0.229, 0.224, 0.225]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights = ResNet50_Weights.DEFAULT
        self.model = resnet50(weights=weights).to(self.device)
        self.model.eval()
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=norm_mean, std=norm_std),
            ]
        )

    def encode_image(self, image_input, is_url: bool = True):
        """
        Encode an image → base64 + feature vector.

        Note: matches the course pipeline (full ResNet50 forward output) so
        vectors align with the provided embeddings pickle.
        """
        try:
            if isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            elif is_url:
                response = requests.get(image_input, timeout=60)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                image = Image.open(image_input).convert("RGB")

            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

            input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.model(input_tensor)
            feature_vector = features.cpu().numpy().flatten()
            return {"base64": base64_string, "vector": feature_vector, "pil": image}
        except Exception as e:
            print(f"Error encoding image: {e}")
            return {"base64": None, "vector": None, "pil": None}

    def find_closest_match(self, user_vector, dataset):
        try:
            dataset_vectors = np.vstack(dataset["Embedding"].dropna().values)
            similarities = cosine_similarity(
                user_vector.reshape(1, -1), dataset_vectors
            )
            closest_index = int(np.argmax(similarities))
            similarity_score = float(similarities[0][closest_index])
            closest_row = dataset.iloc[closest_index]
            return closest_row, similarity_score
        except Exception as e:
            print(f"Error finding closest match: {e}")
            return None, None
