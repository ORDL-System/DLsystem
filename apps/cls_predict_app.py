from typing import OrderedDict
import sys
sys.path.append("utils")
from networks import *
import torch
import streamlit as st
import pathlib
import collections
import torchinfo
import torchvision


def get_streamlit_params():

    # return Dict
    params = collections.defaultdict(int)

    # Choose the DL Library
    library = st.sidebar.selectbox(label="深度学习框架", options=["PyTorch", "TensorFlow"])
    params["library"] = library

    # Choose the Device 
    if library == "PyTorch":
        available_gpus = ["cpu"] + ["cuda:" + str(i) for i in range(torch.cuda.device_count())]
        device = st.sidebar.selectbox(label="设备", options=available_gpus)
        params["device"] = device

        # Choose the dataset
        datasets_name = pathlib.Path(f"./user_data/test/cls_datasets/image").iterdir()
        dataset = st.sidebar.selectbox(label="数据集", options=[n.stem for n in datasets_name if n.is_dir()])
        params["dataset"] = dataset
        
        # Choose the model
        models_path = pathlib.Path("")
        models_name = pathlib.Path(f"./user_data/test/cls_models").rglob("*.pth")  # list models
        model = st.sidebar.selectbox(label="模型", options=['_'.join(n.stem.split('_')[0:-1]) for n in models_name if n.stem.split('_')[-1] == dataset.lower()])
        params["model"] = f"{model}_{dataset.lower()}"

        # Choose the View Structure
        view_structure = st.sidebar.checkbox(label="网络结构可视化", value=False)
        params["view_structure"] = view_structure

        # Choose the image_size
        img_resize = int(st.sidebar.number_input(label="图像尺寸", min_value=0, max_value=256, step=1, value=224))
        params["img_resize"] = img_resize

        # Choose the batch_size
        batch_size = st.sidebar.slider(label="批量大小", min_value=1, max_value=256, value=4, step=1)
        params["bs"] = batch_size

    if library == "TensorFlow":
        pass

    return params


def predict_pytorch(params, predict_button):
    # ------------------------
    # Title
    # ------------------------
    user_name = "test"
    st.title("缺陷分类")

    # ------------------------
    # get params config
    # ------------------------
    model = params["model"]
    device = params["device"]
    img_resize = params["img_resize"]
    batch_size = params["bs"]
    dataset_name = params["dataset"]
    view_structure = params["view_structure"]

    # ------------------------
    # load model
    # ------------------------
    # TODO 区分tensorflow和PyTorch
    # TODO 加入username变量
    checkpoint = torch.load(f"./user_data/test/cls_models/{model}.pth")
    # print(type(checkpoint), isinstance(checkpoint, torch.nn.Module))

    if isinstance(checkpoint, torch.nn.Module):
        model = checkpoint.to(device)
        default_cfg = {}
    # Adapt Lizhaofu model
    elif isinstance(checkpoint, OrderedDict):
        # if "resnet18" in model and 'pcb' in model:
        #     model = ResNets(model_name='resnet18')
        # elif "resnet50" in model and 'pcb' in model:
        #     model = ResNets(model_name='resnet50')
        # elif "vit" in model and 'pcb' in model:
        #     model = VITs()
        # elif "resnet50_eca_wm811k" in model:
        #     model = eca_resnet50()
        # elif "resnet50_simam_wm811k" in model:
        #     model = sim_resnet50()
        model_name = '_'.join(model.split('_')[:-1])
        model = ModelRegistry[model_name]()
        model.load_state_dict(checkpoint)
        model = model.to(device)
        default_cfg = {}
    else:
        if "mean" in checkpoint and "std" in checkpoint and "model" in checkpoint:
            model = checkpoint["model"].to(device)
            default_cfg = dict([(key, checkpoint[key]) for key in ['input_size', 'mean', 'std']])
        else:
            raise "mean or std or model has not been saved in `xxx.pth`!"

    # ------------------------
    # visualize model
    # ------------------------
    if view_structure:
        # TODO 通道数自适应, 有一些channel=1, 显示不了
        st.text(f"Input Shape \t\t\t\t ({batch_size}, {3}, {img_resize}, {img_resize})")
        st.text(torchinfo.summary(model, input_size=(batch_size, 3, img_resize, img_resize)))

    # ------------------------
    # Predict
    # ------------------------
    from predict_util import PredictDataset, Predicter

    if predict_button:
        # 1. create predict dataset
        PD = PredictDataset(user_name=user_name, dataset_name=dataset_name, model=model, default_cfg=default_cfg)
        transform = PD.tranforms() # data process
        predict_dataset, predict_iter = PD.create_dataloader_iterator(mode="test", batch_size=batch_size, trans=transform, shuffle=False, drop_last=False)
        st.subheader("数据集加载完毕!!!")

        # 2.predict
        loss_fn = torch.nn.CrossEntropyLoss()
        demo = Predicter(model, dataset_name, predict_dataset, predict_iter, device, loss_fn)
        st.subheader("预测开始")
        demo.predict()


def predict_tensorflow():
    pass


def main():
    params = get_streamlit_params()
    library = params["library"]

    predict_button = st.sidebar.button(label="开始预测")

    if library == "PyTorch":
        predict_pytorch(params, predict_button)
    elif library == "TensorFlow":
        predict_tensorflow()


if __name__ == '__main__':
    main()

