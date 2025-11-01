import torch
import torch.nn.functional as F
import numpy as np
import os
from .ocr_model import SimpleCNN, get_character_from_label

class EMNISTPredictor:
    """
    Predictor class for EMNIST character recognition.
    Handles model loading and inference on 28x28 numpy arrays.
    """

    def __init__(self, model_path=None, device=None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to the saved model weights
            device: torch device (cuda/cpu). If None, automatically selects.
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device

        # Set default model path relative to project root
        if model_path is None:
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )
            model_path = os.path.join(project_root, "emnist_model.pth")

        # Load model (36 classes: 0-9, A-Z)
        self.model = SimpleCNN(num_classes=36).to(self.device)
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device, weights_only=True)
        )
        self.model.eval()

        print(f"Model loaded from {model_path}")
        print(f"Using device: {self.device}")

    def predict_probabilities(self, image_array):
        """
        Predict probability distribution over all 36 characters (0-9, A-Z).

        Args:
            image_array: numpy array of shape (28, 28) with pixel values in [0, 255] or [0, 1]

        Returns:
            dict: {character: probability} for all 36 characters
        """
        # Validate input shape
        if image_array.shape != (28, 28):
            raise ValueError(f"Input must be 28x28, got {image_array.shape}")

        # Normalize to [0, 1] if not already
        if image_array.max() > 1.0:
            image_array = image_array.astype(np.float32) / 255.0

        # Apply the same transform as in training: Normalize with mean=0.5, std=0.5
        # This converts [0, 1] to [-1, 1]
        image_array = (image_array - 0.5) / 0.5

        # Convert to tensor and add batch and channel dimensions
        # Shape: (28, 28) -> (1, 1, 28, 28)
        image_tensor = torch.from_numpy(image_array).float().unsqueeze(0).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)

        # Run inference
        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = F.softmax(output, dim=1)

        # Convert to dictionary mapping characters to probabilities
        prob_dict = {}
        for idx in range(36):
            char = get_character_from_label(idx)
            prob = probabilities[0, idx].item()
            prob_dict[char] = prob

        return prob_dict


# Global predictor instance for convenience
_global_predictor = None


def predict_letter_from_image(image_array, model_path=None) -> dict[str, float]:
    """
    Convenience function to get probability distribution.
    Loads model on first call and reuses it.

    Args:
        image_array: numpy array of shape (28, 28)
        model_path: path to model weights (only used on first call)

    Returns:
        dict: {character: probability} for all 36 characters (0-9, A-Z)
    """
    global _global_predictor

    if _global_predictor is None:
        _global_predictor = EMNISTPredictor(model_path)

    return _global_predictor.predict_probabilities(image_array)


