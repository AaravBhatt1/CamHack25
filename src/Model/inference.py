import torch
import torch.nn.functional as F
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from model import SimpleCNN, get_character_from_label

# Add parent directory to path to import from other modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from CharMapper.charMapper import CharMapper
from imagereading.vectorconvert import get_image_for_ocr


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


def get_probabilities(image_array, model_path=None):
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


if __name__ == "__main__":
    # Example usage
    print("Initializing predictor...")
    predictor = EMNISTPredictor()

    # Get test input from user - they "draw" a character by typing keys on keyboard
    print("\nDraw a character by typing keys on your keyboard (the shape they make).")
    print("For example, to draw 'C', you might type: edc  or  edsxz")
    print("When done, press Enter.\n")

    test_string = input("Type keys to draw a character: ").strip().lower()

    if not test_string:
        test_string = "edc"  # Default draws a C-ish shape
        print(f"Using default test string: '{test_string}'")

    print(f"\nKeys typed: '{test_string}'")

    # Use charMapper to get coordinates for each character
    mapper = CharMapper()

    # Get list of coordinates for each key pressed
    points = []
    for char in test_string:
        try:
            coords = mapper.charMap(char)
            if coords:
                points.append(coords)
        except (KeyError, TypeError):
            print(f"Character '{char}' not found in keyboard map, skipping")
            continue

    if not points:
        print("No valid characters to process. Using random image.")
        test_image = np.random.rand(28, 28)
        expected_char = None
    else:
        print(f"Mapped {len(points)} keys to coordinates: {points}")

        # Visualize the raw keyboard coordinates
        plt.figure(figsize=(12, 5))

        # First subplot: raw keyboard points
        plt.subplot(1, 3, 1)
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        plt.scatter(x_coords, y_coords, s=100, c="blue", alpha=0.6)
        for i, (x, y) in enumerate(points):
            plt.annotate(test_string[i], (x, y), fontsize=12, ha="center", va="bottom")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Raw Keyboard Coordinates")
        plt.grid(True, alpha=0.3)
        plt.axis("equal")

        # Use movePoints to adjust location (shift to start at x=0)
        adjusted_points = mapper.movePoints(points)
        print(f"Adjusted coordinates: {adjusted_points}")

        # Second subplot: adjusted points
        plt.subplot(1, 3, 2)
        adj_x = [p[0] for p in adjusted_points]
        adj_y = [p[1] for p in adjusted_points]
        plt.scatter(adj_x, adj_y, s=100, c="green", alpha=0.6)
        for i, (x, y) in enumerate(adjusted_points):
            plt.annotate(test_string[i], (x, y), fontsize=12, ha="center", va="bottom")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Adjusted Coordinates")
        plt.grid(True, alpha=0.3)
        plt.axis("equal")

        # Build data with timestamps for vectorconvert
        # Format: [(x, y, timestamp), ...]
        data = [(x, y, i) for i, (x, y) in enumerate(adjusted_points)]

        # Convert to 28x28 image using vectorconvert
        test_image = get_image_for_ocr(data)
        print(f"Generated 28x28 image, shape: {test_image.shape}")

        # Third subplot: 28x28 image as model sees it
        plt.subplot(1, 3, 3)
        plt.imshow(test_image, cmap="gray")
        plt.title("28x28 Image for Model")
        plt.axis("off")

        plt.tight_layout()
        plt.show()

    # Get probabilities
    probabilities = predictor.predict_probabilities(test_image)

    # Show top 5 predictions
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 predictions:")
    for i, (char, prob) in enumerate(sorted_probs[:5], 1):
        print(f"  {i}. '{char}': {prob:.4f}")
