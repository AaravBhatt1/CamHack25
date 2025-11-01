import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import os


<<<<<<< HEAD:src/prediction/ocr_model.py
# Define the transform used for training and inference
def get_transform() -> transforms.Compose:
    """
    Returns the transform pipeline used for both training and inference.
    Converts images to tensors and normalizes them.
    """
=======
def get_transform():
    """Standard EMNIST transform: ToTensor + Normalize"""
>>>>>>> 5d21c41 (THE ANSWER):src/Model/model.py
    return transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                (0.1307,), (0.3081,)
            ),  # MNIST/EMNIST standard normalization
        ]
    )


class EMNISTNet(nn.Module):
    """
    Standard CNN architecture for EMNIST.
    Proven to achieve 85-90% accuracy on EMNIST Letters.
    """

    def __init__(self, num_classes=26):
        super(EMNISTNet, self).__init__()

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(2, 2)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)

        # After 3 conv+pool layers: 28 -> 14 -> 7 -> 3
        # But we only do 2 pools, so: 28 -> 14 -> 7
        self.fc1 = nn.Linear(128 * 7 * 7, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        # Block 1
        x = F.relu(self.conv1(x))
        x = self.pool(x)  # 28 -> 14

        # Block 2
        x = F.relu(self.conv2(x))
        x = self.pool(x)  # 14 -> 7
        x = self.dropout1(x)

        # Block 3
        x = F.relu(self.conv3(x))
        x = self.dropout1(x)

        # Flatten
        x = x.view(-1, 128 * 7 * 7)

        # FC layers
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)

        return x


<<<<<<< HEAD:src/prediction/ocr_model.py
def get_character_from_label(label: int) -> str:
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


def get_label_from_character(char: str) -> int:
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


def count_parameters(model: SimpleCNN) -> int:
    """
    Count the number of trainable parameters in a model.

    Args:
        model: PyTorch model

    Returns:
        int: number of trainable parameters
    """
=======
def get_character_from_label(label):
    """Convert label 0-25 to character A-Z"""
    if 0 <= label < 26:
        return chr(ord("A") + label)
    return "?"


def get_label_from_character(char):
    """Convert character A-Z to label 0-25"""
    if char.isupper() and "A" <= char <= "Z":
        return ord(char) - ord("A")
    return None


def count_parameters(model):
    """Count trainable parameters"""
>>>>>>> 5d21c41 (THE ANSWER):src/Model/model.py
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Configuration
    BATCH_SIZE = 128
    EPOCHS = 3
    LEARNING_RATE = 0.001

    # Device setup
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")
    print("=" * 80)

    # Data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data")

    # Load EMNIST ByClass dataset
    print("Loading EMNIST ByClass dataset...")
    transform = get_transform()

    full_train = datasets.EMNIST(
        root=data_path, split="byclass", train=True, download=True, transform=transform
    )

    full_test = datasets.EMNIST(
        root=data_path, split="byclass", train=False, download=True, transform=transform
    )

    # Filter for uppercase letters only (labels 10-35 in ByClass)
    # ByClass: 0-9 (digits), 10-35 (uppercase A-Z), 36-61 (lowercase a-z)
    print("Filtering for uppercase letters (A-Z)...")

    train_indices = [i for i, (_, label) in enumerate(full_train) if 10 <= label < 36]
    test_indices = [i for i, (_, label) in enumerate(full_test) if 10 <= label < 36]

    # Create subsets
    train_subset = Subset(full_train, train_indices)
    test_subset = Subset(full_test, test_indices)

    # Custom wrapper to remap labels from 10-35 to 0-25
    class RemappedDataset(torch.utils.data.Dataset):
        def __init__(self, subset):
            self.subset = subset

        def __getitem__(self, idx):
            img, label = self.subset[idx]
            return img, label - 10  # Remap 10-35 to 0-25

        def __len__(self):
            return len(self.subset)

    train_dataset = RemappedDataset(train_subset)
    test_dataset = RemappedDataset(test_subset)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print(f"Classes: 26 (A-Z)")
    print("=" * 80)

    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0
    )

    test_loader = DataLoader(
        test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0
    )

    # Initialize model
    model = EMNISTNet(num_classes=26).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    print(f"Model parameters: {count_parameters(model):,}")
    print(f"Architecture:\n{model}")
    print("=" * 80)

    # Training function
    def train_epoch(epoch):
        model.train()
        train_loss = 0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

            if batch_idx % 50 == 0:
                print(
                    f"Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} ",
                    f"({100.0 * batch_idx / len(train_loader):.0f}%)]  ",
                    f"Loss: {loss.item():.4f}  Acc: {100.0 * correct / total:.2f}%",
                )

        return train_loss / len(train_loader), 100.0 * correct / total

    # Test function
    def test_epoch():
        model.eval()
        test_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                test_loss += criterion(output, target).item()

                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()

        test_loss /= len(test_loader)
        accuracy = 100.0 * correct / total

        print(
            f"\nTest set: Average loss: {test_loss:.4f}, "
            f"Accuracy: {correct}/{total} ({accuracy:.2f}%)\n"
        )

        return test_loss, accuracy

    # Training loop
    print("Starting training...")
    print("=" * 80)

    best_acc = 0

    for epoch in range(1, EPOCHS + 1):
        print(f"\nEPOCH {epoch}/{EPOCHS}")
        print("-" * 80)

        train_loss, train_acc = train_epoch(epoch)
        test_loss, test_acc = test_epoch()
        scheduler.step()

        print(f"Epoch {epoch} Summary:")
        print(f"  Train Loss: {train_loss:.4f}  Train Acc: {train_acc:.2f}%")
        print(f"  Test Loss:  {test_loss:.4f}  Test Acc:  {test_acc:.2f}%")
        print(f"  Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")

        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            model_path = os.path.join(script_dir, "..", "..", "emnist_model_best.pth")
            torch.save(model.state_dict(), model_path)
            print(f"  ✓ New best model saved! (Accuracy: {best_acc:.2f}%)")

        print("=" * 80)

    # Save final model
    final_model_path = os.path.join(script_dir, "..", "..", "emnist_model.pth")
    torch.save(model.state_dict(), final_model_path)

    print(f"\n✓ Training complete!")
    print(f"✓ Best accuracy: {best_acc:.2f}%")
    print(f"✓ Final model saved to: {final_model_path}")
    print(f"✓ Best model saved to: emnist_model_best.pth")
