import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms


# Define the transform used for training and inference
def get_transform():
    """
    Returns the transform pipeline used for both training and inference.
    Converts images to tensors and normalizes them.
    """
    return transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
    )


class SimpleCNN(nn.Module):
    """
    Simple CNN for EMNIST character recognition.

    Input: 28x28 grayscale images (1 channel)
    Output: 47 class logits (EMNIST Balanced classes)

    Architecture:
    - Conv1: 1 -> 32 channels (3x3 kernel, padding=1)
    - MaxPool: 28x28 -> 14x14
    - Conv2: 32 -> 64 channels (3x3 kernel, padding=1)
    - MaxPool: 14x14 -> 7x7
    - Flatten: 64 * 7 * 7 = 3136
    - FC1: 3136 -> 128
    - FC2: 128 -> num_classes
    """

    def __init__(self, num_classes=36):
        super(SimpleCNN, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)

        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        # Conv layer 1 + ReLU + Pool
        x = self.conv1(x)
        x = F.relu(x)
        x = self.pool(x)  # 28x28 -> 14x14

        # Conv layer 2 + ReLU + Pool
        x = self.conv2(x)
        x = F.relu(x)
        x = self.pool(x)  # 14x14 -> 7x7

        # Flatten
        x = x.view(-1, 64 * 7 * 7)

        # Fully connected layers
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)

        return x


def get_character_from_label(label):
    """
    Convert class label to character (uppercase letters and digits only).

    36 classes:
    - 0-9: digits '0'-'9'
    - 10-35: uppercase 'A'-'Z'

    Args:
        label: int, class index (0-35)

    Returns:
        str: corresponding character
    """
    if label < 10:
        # Digits 0-9
        return str(label)
    elif label < 36:
        # Uppercase A-Z
        return chr(ord("A") + label - 10)
    else:
        return "?"


def get_label_from_character(char):
    """
    Convert character to class label (uppercase letters and digits only).

    Args:
        char: str, single character

    Returns:
        int: class index (0-35), or None if character not in dataset
    """
    if char.isdigit():
        return int(char)
    elif char.isupper() and "A" <= char <= "Z":
        return ord(char) - ord("A") + 10
    else:
        return None


def count_parameters(model):
    """
    Count the number of trainable parameters in a model.

    Args:
        model: PyTorch model

    Returns:
        int: number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    import torch.optim as optim
    from torchvision import datasets
    from torch.utils.data import DataLoader
    import os

    # Device configuration - use MPS (Apple Silicon) if available, otherwise CUDA or CPU
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    # Get the transform
    transform = get_transform()

    # Get data path (works whether running from Model/ or project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data")

    # Load EMNIST ByClass dataset (we'll filter to only use uppercase + digits)
    print("Loading EMNIST ByClass dataset...")
    train_dataset_full = datasets.EMNIST(
        root=data_path, split="byclass", train=True, download=True, transform=transform
    )

    test_dataset_full = datasets.EMNIST(
        root=data_path,
        split="byclass",
        train=False,
        download=True,
        transform=transform,
    )

    # Filter to only include digits (0-9) and uppercase letters (A-Z)
    # ByClass labels: 0-9 (digits), 10-35 (uppercase A-Z), 36-61 (lowercase a-z)
    def filter_dataset(dataset):
        indices = [i for i, (_, label) in enumerate(dataset) if label < 36]
        return torch.utils.data.Subset(dataset, indices)

    train_dataset = filter_dataset(train_dataset_full)
    test_dataset = filter_dataset(test_dataset_full)

    print(
        f"Training samples: {len(train_dataset)} (filtered from {len(train_dataset_full)})"
    )
    print(f"Test samples: {len(test_dataset)} (filtered from {len(test_dataset_full)})")
    print(f"Number of classes: 36 (0-9, A-Z)")

    # Create data loaders (larger batch size for faster training on GPU)
    batch_size = 256
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Initialize model, loss, and optimizer
    model = SimpleCNN(num_classes=36).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"Model parameters: {count_parameters(model):,}")
    print(f"Architecture:\n{model}")
    print("-" * 80)

    def train_epoch(model, train_loader, criterion, optimizer, epoch):
        """Train the model for one epoch."""
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            # Zero gradients
            optimizer.zero_grad()

            # Forward pass
            output = model(data)

            # Calculate loss
            loss = criterion(output, target)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()

            # Print progress
            if batch_idx % 100 == 0:
                print(
                    f"Epoch {epoch}, Batch {batch_idx}/{len(train_loader)}, "
                    f"Loss: {loss.item():.4f}, Acc: {100 * correct / total:.2f}%"
                )

        avg_loss = running_loss / len(train_loader)
        accuracy = 100 * correct / total

        return avg_loss, accuracy

    def evaluate(model, test_loader, criterion):
        """Evaluate the model on test data."""
        model.eval()
        test_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)

                # Forward pass
                output = model(data)

                # Calculate loss
                test_loss += criterion(output, target).item()

                # Get predictions
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        avg_loss = test_loss / len(test_loader)
        accuracy = 100 * correct / total

        print(f"Test Loss: {avg_loss:.4f}, Test Acc: {accuracy:.2f}%")

        return avg_loss, accuracy

    # Training loop (reduced for faster training)
    num_epochs = 2

    print("Starting training...")
    print("=" * 80)

    best_test_acc = 0.0

    for epoch in range(1, num_epochs + 1):
        print(f"\nEpoch {epoch}/{num_epochs}")
        print("-" * 80)

        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, epoch
        )
        test_loss, test_acc = evaluate(model, test_loader, criterion)

        print(
            f"Epoch {epoch} Summary: "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
            f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.2f}%"
        )

        # Save best model
        if test_acc > best_test_acc:
            best_test_acc = test_acc
            model_path_best = os.path.join(script_dir, "..", "emnist_model_best.pth")
            torch.save(model.state_dict(), model_path_best)
            print(f"✓ Saved best model with test accuracy: {best_test_acc:.2f}%")

        print("=" * 80)

    # Save final model
    model_path_final = os.path.join(script_dir, "..", "emnist_model.pth")
    torch.save(model.state_dict(), model_path_final)
    print(f"\n✓ Training complete! Final model saved to {model_path_final}")
    print(
        f"✓ Best model saved to emnist_model_best.pth (Test Acc: {best_test_acc:.2f}%)"
    )
