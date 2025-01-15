import collections
import pathlib
import streamlit as st
import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

import torch

import sys
sys.path.append("user_data/test/da_models")
from get_model import ConGAN_Generator, DCGAN_Generator, SAGAN_Generator, WGAN_GP_Generator

def get_streamlit_params():
    params = collections.defaultdict(int)
    
    library = st.sidebar.selectbox(label="框架", options=["PyTorch", "TensorFLow"], help="choose your library")
    params["library"] = library

    if library == "PyTorch":
        available_gpus = ["cpu"] + ["cuda:" + str(i) for i in range(torch.cuda.device_count())]
        device = st.sidebar.selectbox(label="设备", options=available_gpus)
        params["device"] = device
        
        # Choose the model
        models_names = os.listdir(pathlib.Path(f"./user_data/test/da_models/pretrained"))
        model = st.sidebar.selectbox(label="模型", options=models_names)
        params["model"] = model
        
        # Choose the View Structure
        view_structure = st.sidebar.checkbox(label="网络结构可视化", value=False)
        params["view_structure"] = view_structure
        
        # Choose the dataset
        datasets_names = os.listdir(pathlib.Path(f"./user_data/test/da_datasets"))
        dataset = st.sidebar.selectbox(label="数据集", options=datasets_names)
        params["dataset"] = dataset.replace("-", "_")
        
        datasets_names = ["鼠咬", "开路", "短路", "毛刺", "残铜"]
        dataset = st.sidebar.selectbox(label="缺陷类别", options=datasets_names)
        params["category"] = str(datasets_names.index(dataset))
        
        # Choose the train_scale
        num_samples = st.sidebar.slider(label="生成样本数量", min_value=1, max_value=50, value=12, step=1)
        params["num_samples"] = num_samples

        
    
    elif library == "TensorFlow":
        pass

    return params
    
def train_pytorch(params, start_button, stop_button):
    st.title("数据增强")
    
    G_path = "./user_data/test/da_models/pretrained/" + params["model"] + "/models/" + params["dataset"] + " " + params["category"] + ".pth"
    checkpoint = torch.load(G_path)
    
    G = get_G(params["model"])
    if params["view_structure"]:
        # st.text(f"Input Shape \t\t\t\t ({params["num_samples"]}, {3}, {img_resize}, {img_resize})")
        # st.text(torchinfo.summary(model, input_size=(batch_size, 3, img_resize, img_resize)))
        pass
    G.eval()
    
    if start_button:
        G.load_state_dict(checkpoint["model_state_dict"])
        st.subheader(f"模型加载")
        st.text(f"模型参数加载成功！")
        st.text(f"模型参数路径为：{G_path}")
        st.subheader(f"开始增强")
        
        # ConGAN
        if params["model"] == "ConGAN":
            z = torch.randn(params["num_samples"], 128)
        elif params["model"] == "SAGAN":
            z = torch.randn(params["num_samples"], 100)
        else:    
            z = torch.randn(params["num_samples"], 100, 1, 1)
        
        imgs = G(z)
        
        num_rows = 3
        figs, axes = plt.subplots(num_rows, int(len(imgs)/num_rows))
        axes = axes.flatten()
        for i, (ax, img) in enumerate(zip(axes, imgs)):
            img = img.detach().numpy()
            img = ((img + 1) / 2 * 255).astype(np.uint8)
            img = Image.fromarray(img.transpose(1, 2, 0))
            ax.imshow(img)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
        st.pyplot(figs)
        st.subheader(f"完成增强")

def get_G(name):
    if name == "DCGAN":
        return DCGAN_Generator()
    elif name == "ConGAN":
        return ConGAN_Generator()
    elif name == "SAGAN":
        return SAGAN_Generator()
    elif name == "WGAN_GP":
        return WGAN_GP_Generator()

def train_tensorflow():
    pass


def main():
    params = get_streamlit_params()
    library = params["library"]
    
    start_button = st.sidebar.button(label="开始生成")
    stop_button = st.sidebar.button(label="停止生成")
    
    if library == "PyTorch":
        train_pytorch(params, start_button, stop_button)
    elif library == "TensorFlow":
        train_tensorflow()
    
if __name__ == "__main__":
    main()