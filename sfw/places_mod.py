# modified from Bolei Zhou, sep 2, 2017

import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
from tqdm import tqdm
import os
import numpy as np
import cv2
from PIL import Image
import pickle
from rich import print
import requests

MODEL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'places')

def get_path(filename):
    return os.path.join(MODEL_DIR, filename)

def cap(s, n):
    return s[:n] + (s[n:] and '..')

def download_file(url, path):
    """download file from url to path with wget, create directories if needed"""
    if os.path.exists(path):
        return
    os.system(f'mkdir -p {os.path.dirname(path)}')
    os.system(f'wget -O {path} {url}')

# hacky way to deal with the Pytorch 1.0 update
def recursion_change_bn(module):
    if isinstance(module, torch.nn.BatchNorm2d):
        module.track_running_stats = 1
    else:
        for i, (name, module1) in enumerate(module._modules.items()):
            module1 = recursion_change_bn(module1)
    return module


def load_labels():
    # prepare all the labels
    # scene category relevant
    file_name_category = 'categories_places365.txt'
    if not os.access(file_name_category, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
        # os.system('wget ' + synset_url)
        download_file(synset_url, get_path(file_name_category))
    classes = list()
    with open(get_path(file_name_category)) as class_file:
        for line in class_file:
            classes.append(line.strip().split(' ')[0][3:])
    classes = tuple(classes)

    # indoor and outdoor relevant
    file_name_IO = 'IO_places365.txt'
    if not os.access(file_name_IO, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/IO_places365.txt'
        # os.system('wget ' + synset_url)
        download_file(synset_url, get_path(file_name_IO))
    with open(get_path(file_name_IO)) as f:
        lines = f.readlines()
        labels_IO = []
        for line in lines:
            items = line.rstrip().split()
            labels_IO.append(int(items[-1]) - 1)  # 0 is indoor, 1 is outdoor
    labels_IO = np.array(labels_IO)

    # scene attribute relevant
    file_name_attribute = 'labels_sunattribute.txt'
    if not os.access(file_name_attribute, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/labels_sunattribute.txt'
        # os.system('wget ' + synset_url)
        download_file(synset_url, get_path(file_name_attribute))
    with open(get_path(file_name_attribute)) as f:
        lines = f.readlines()
        labels_attribute = [item.rstrip() for item in lines]
    file_name_W = 'W_sceneattribute_wideresnet18.npy'
    if not os.access(file_name_W, os.W_OK):
        synset_url = 'http://places2.csail.mit.edu/models_places365/W_sceneattribute_wideresnet18.npy'
        # os.system('wget ' + synset_url)
        download_file(synset_url, get_path(file_name_W))
    W_attribute = np.load(get_path(file_name_W))

    return classes, labels_IO, labels_attribute, W_attribute


def returnCAM(feature_conv, weight_softmax, class_idx):
    # generate the class activation maps upsample to 256x256
    size_upsample = (256, 256)
    nc, h, w = feature_conv.shape
    output_cam = []
    for idx in class_idx:
        cam = weight_softmax[class_idx].dot(feature_conv.reshape((nc, h * w)))
        cam = cam.reshape(h, w)
        cam = cam - np.min(cam)
        cam_img = cam / np.max(cam)
        cam_img = np.uint8(255 * cam_img)
        output_cam.append(cv2.resize(cam_img, size_upsample))
    return output_cam


def returnTF():
    # load the image transformer
    tf = trn.Compose([
        trn.Resize((224, 224)),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return tf



def load_model(hook_feature):
    # this model has a last conv feature map as 14x14

    model_file = 'wideresnet18_places365.pth.tar'
    model_path = os.path.join(MODEL_DIR, model_file)
    if not os.access(model_path, os.W_OK):
        download_file("http://places2.csail.mit.edu/models_places364/" + model_file, model_path)
        download_file("https://raw.githubusercontent.com/csailvision/places365/master/wideresnet.py", os.path.join(MODEL_DIR, "wideresnet.py"))

    # import wideresnet
    from places import wideresnet
    model = wideresnet.resnet18(num_classes=365)
    checkpoint = torch.load(get_path(model_file), map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)

    # hacky way to deal with the upgraded batchnorm2D and avgpool layers...
    for i, (name, module) in enumerate(model._modules.items()):
        module = recursion_change_bn(model)
    model.avgpool = torch.nn.AvgPool2d(kernel_size=14, stride=1, padding=0)
    model.eval()
    # hook the feature extractor
    features_names = ['layer4', 'avgpool']  # this is the last conv layer of the resnet
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_feature)
    return model

class Places:
    def __init__(self):
        # load the labels
        self.classes, self.labels_IO, self.labels_attribute, self.W_attribute = load_labels()

        # load the model
        self.features_blobs = []
        self.model = load_model(lambda module,input,output: self.hook_feature(module,input,output))

        # load the transformer
        self.tf = returnTF()  # image transformer

        # get the softmax weight
        self.params = list(self.model.parameters())
        self.weight_softmax = self.params[-2].data.numpy()
        self.weight_softmax[self.weight_softmax < 0] = 0

    def hook_feature(self, module, input, output):
        self.features_blobs.append(np.squeeze(output.data.cpu().numpy()))

    def extract(self, img_path):
        img = Image.open(img_path)
        # if image contains less than 3 channels, transform it to 3 channels
        if len(img.split()) < 3:
            img = img.convert('RGB')
        input_img = V(self.tf(img).unsqueeze(0))

        # forward pass
        logit = self.model.forward(input_img)
        h_x = F.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)
        probs = probs.numpy()
        idx = idx.numpy()

        responses_attribute = self.W_attribute.dot(self.features_blobs[1])
        self.features_blobs.clear()
        return probs, responses_attribute, idx

    def output(self, img_path):
        probs, responses_attribute, idx = self.extract(img_path)
        io_image = np.mean(self.labels_IO[idx[:10]])  # vote for the indoor or outdoor
        io_typ = "indoor" if io_image < 0.5 else "outdoor"
        categories = [self.classes[idx[i]] for i in range(0, 5)]
        # scene attributes
        idx_a =  np.argsort(responses_attribute)
        attributes = [self.labels_attribute[idx_a[i]] for i in range(-1, -10, -1)]
        # compile results in to a string
        def wrap(s): return f"[blue]{s}[/blue]"
        def wrap_list(l): return ', '.join([wrap(s) for s in l])
        result = f"""{wrap(io_typ)}
Categories:{wrap_list(categories)}
Attributes:{wrap_list(attributes)}"""
        return result