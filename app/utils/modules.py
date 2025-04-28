import torch
from torch import nn
import timm
from transformers import AutoModel, AutoTokenizer, AutoConfig
from app.core.config import configs as CFG

class ImageEncoder(nn.Module):
    """
    Encode images to a fixed size vector
    """

    def __init__(
        self, model_name=CFG.IMAGE_ENCODER, pretrained=True, trainable=False
    ):
        super().__init__()
        # print(f"Using image encoder: {model_name}") 
        self.model = timm.create_model(
            model_name, pretrained, num_classes=0, global_pool="avg"
        )
        for p in self.model.parameters():
            p.requires_grad = trainable

    def forward(self, x):
        return self.model(x)


class TextEncoder(nn.Module):
    def __init__(self, model_name=CFG.TEXT_ENCODER, pretrained=True, trainable=False):
        super().__init__()
        if pretrained:
            self.model = AutoModel.from_pretrained(model_name)
        else:
            self.model = AutoModel(config=AutoConfig.from_pretrained(model_name))
            
        for p in self.model.parameters():
            p.requires_grad = trainable

        # we are using the CLS token hidden representation as the sentence's embedding
        self.target_token_idx = 0

    def forward(self, input_ids, attention_mask):
        output = self.model(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = output.last_hidden_state
        return last_hidden_state[:, self.target_token_idx, :]



class ProjectionHead(nn.Module):
    def __init__(
        self,
        embedding_dim,
        projection_dim=CFG.PROJECTION_DIM,
        dropout=0.1
    ):
        super().__init__()
        self.projection = nn.Linear(embedding_dim, projection_dim)
        self.gelu = nn.GELU()
        self.fc = nn.Linear(projection_dim, projection_dim)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(projection_dim)
    
    def forward(self, x):
        projected = self.projection(x)
        x = self.layer_norm(projected)
        x = self.gelu(x)
        x = self.dropout(x)
        x = self.fc(x)
        x = x + projected
        return x
    
# image_encoder = ImageEncoder()
# text_encoder = TextEncoder()
# projection_head = ProjectionHead(512, 512, 0.1)