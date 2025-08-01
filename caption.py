# -*- coding: utf-8 -*-
"""caption.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KGeyfetOaXLkK52ZmHydzzbtdnjvxLew
"""

import pickle
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image



class ImageCaptionModel(nn.Module):
    def __init__(self, vocab_size, embed_size=256, hidden_size=256):
        super(ImageCaptionModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(2048, embed_size),
            nn.ReLU()
        )
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.decoder = nn.Sequential(
            nn.Linear(hidden_size, embed_size),
            nn.ReLU(),
            nn.Linear(embed_size, vocab_size)
        )

    def forward(self, features, captions):
        features = self.encoder(features).unsqueeze(1)  # (batch, 1, embed_size)
        embeddings = self.embedding(captions)  # (batch, seq_len, embed_size)
        inputs = torch.cat((features, embeddings), dim=1)  # (batch, seq_len+1, embed_size)
        lstm_out, _ = self.lstm(inputs)  # (batch, seq_len+1, hidden_size)
        outputs = self.decoder(lstm_out)  # (batch, seq_len+1, vocab_size)
        outputs = outputs[:, 1:, :]  # (batch, seq_len, vocab_size)
        return outputs

# Step 3: Define the beam_search function (fixed to avoid IndexError)
def beam_search(model, feature, word_to_idx, idx_to_word, max_length, k=5):
    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    feature = torch.tensor(feature).float().to(device).unsqueeze(0)
    sequences = [[['<start>'], 0.0]]  # [[list of words, log_prob]]

    for _ in range(max_length):
        all_candidates = []
        for seq, score in sequences:
            if seq[-1] == '<end>':
                all_candidates.append([seq, score])
                continue

            caption = [word_to_idx.get(word, 0) for word in seq]
            # Ensure caption length doesn't exceed max_length - 1
            caption = caption[:max_length-1] + [0] * (max_length - 1 - len(caption))
            caption = torch.tensor(caption).long().to(device).unsqueeze(0)

            with torch.no_grad():
                output = model(feature, caption)
                # Use the last valid timestep (min of len(seq) and output size)
                timestep = min(len(seq), output.size(1) - 1)
                probs = torch.softmax(output[0, timestep], dim=-1)

            top_k_probs, top_k_idx = probs.topk(k)

            for i in range(k):
                word = idx_to_word.get(top_k_idx[i].item(), '<unk>')
                new_score = score + torch.log(top_k_probs[i]).item()
                all_candidates.append([seq + [word], new_score])

        sequences = sorted(all_candidates, key=lambda x: x[1], reverse=True)[:k]

        if all(seq[-1] == '<end>' for seq, _ in sequences):
            break

    best_seq = sequences[0][0]
    return [word for word in best_seq[1:] if word != '<end>']

def load_model_and_predict(image_path):
    try:
        # Load model info
        with open('static/weight/model_info.pkl', 'rb') as f:
            model_info = pickle.load(f)

        # Verify required keys
        required_keys = ['word_to_idx', 'idx_to_word', 'vocab_size', 'max_length']
        missing_keys = [key for key in required_keys if key not in model_info]
        if missing_keys:
            raise KeyError(f"Missing keys in model_info: {missing_keys}")

        # Use defaults if embed_size or hidden_size are missing
        embed_size = model_info.get('embed_size', 256)
        hidden_size = model_info.get('hidden_size', 256)

        # Recreate transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Initialize device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Create and load model
        model = ImageCaptionModel(
            vocab_size=model_info['vocab_size'],
            embed_size=embed_size,
            hidden_size=hidden_size
        ).to(device)
        model.load_state_dict(torch.load('models/best_model.pth', map_location=device, weights_only=True))
        model.eval()

        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        img = transform(img).unsqueeze(0)

        # Extract features using ResNet50
        resnet = models.resnet50(weights='IMAGENET1K_V1')
        resnet = nn.Sequential(*list(resnet.children())[:-1])
        resnet.eval()
        resnet = resnet.to(device)

        with torch.no_grad():
            features = resnet(img.to(device)).squeeze().cpu().numpy()

        # Generate caption
        caption = beam_search(
            model,
            features,
            model_info['word_to_idx'],
            model_info['idx_to_word'],
            max_length=model_info['max_length'],
            k=2
        )

        return ' '.join(caption)

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        return None
    except KeyError as e:
        print(f"Error: Key error in model_info - {e}")
        return None
    except Exception as e:
        print(f"Error during inference: {e}")
        return None
    
    
    
def load_model_and_predict_2(image_pi):
    try:
        # Load model info
        with open('static/weight/model_info.pkl', 'rb') as f:
            model_info = pickle.load(f)

        # Verify required keys
        required_keys = ['word_to_idx', 'idx_to_word', 'vocab_size', 'max_length']
        missing_keys = [key for key in required_keys if key not in model_info]
        if missing_keys:
            raise KeyError(f"Missing keys in model_info: {missing_keys}")

        # Use defaults if embed_size or hidden_size are missing
        embed_size = model_info.get('embed_size', 256)
        hidden_size = model_info.get('hidden_size', 256)

        # Recreate transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Initialize device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Create and load model
        model = ImageCaptionModel(
            vocab_size=model_info['vocab_size'],
            embed_size=embed_size,
            hidden_size=hidden_size
        ).to(device)
        model.load_state_dict(torch.load('models/best_model.pth', map_location=device, weights_only=True))
        model.eval()

        # Load and preprocess image

        img = transform(image_pi).unsqueeze(0)

        # Extract features using ResNet50
        resnet = models.resnet50(weights='IMAGENET1K_V1')
        resnet = nn.Sequential(*list(resnet.children())[:-1])
        resnet.eval()
        resnet = resnet.to(device)

        with torch.no_grad():
            features = resnet(img.to(device)).squeeze().cpu().numpy()

        # Generate caption
        caption = beam_search(
            model,
            features,
            model_info['word_to_idx'],
            model_info['idx_to_word'],
            max_length=model_info['max_length'],
            k=2
        )

        return ' '.join(caption)

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        return None
    except KeyError as e:
        print(f"Error: Key error in model_info - {e}")
        return None
    except Exception as e:
        print(f"Error during inference: {e}")
        return None