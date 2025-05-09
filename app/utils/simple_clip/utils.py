import torch
from transformers import AutoTokenizer
# import datasets
# import webdataset as wds

from app.utils.simple_clip.encoders import ImageEncoder, TextEncoder
# from simple_clip.custom_datasets.clip_datasets import KTVICDataset


# def get_dataset(text_encoder_name,
#                 dataset_name,
#                 dataset_path,
#                 transforms,
#                 split="train",
#                 shuffle_captions=True):

#     if text_encoder_name == "phobert-base":
#         tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
#         return KTVICDataset(tokenizer, transforms, split=split)
#     else:
#         return KTVICDataset(text_encoder_name, transforms, split=split)

#     raise Exception(f"Invalid dataset name {dataset_name} - options are [coco, sbucaptions, combined, yfcc7m]")


def get_image_encoder(model_name):
    return ImageEncoder(model_name)
       
def get_text_encoder(model_name):
    return TextEncoder(model_name)


def accuracy(output, target, topk=(1, )):
    with torch.no_grad():
        maxk = max(topk)
        batch_size = target.size(0)

        _, pred = output.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target.view(1, -1).expand_as(pred))

        res = []
        for k in topk:
            correct_k = correct[:k].reshape(-1).float().sum(0, keepdim=True)
            res.append(correct_k.mul_(100.0 / batch_size))
        return res


@torch.inference_mode
def get_feature_size(encoder):
    """Get the feature size from the encoder using a dummy input."""
    encoder.eval()
    # Use 224x224 input size which is standard for most vision models
    dummy_input = torch.randn(1, 3, 224, 224)
    output = encoder(dummy_input)
    
    # Ensure we return an integer, not a tensor or tuple
    if isinstance(output, torch.Tensor):
        return output.shape[1]
    else:
        # Handle case where output might be a tuple or other structure
        return output[0].shape[1] if isinstance(output, tuple) else 576  # Fallback value