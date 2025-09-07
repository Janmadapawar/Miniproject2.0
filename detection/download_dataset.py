

from roboflow import Roboflow
rf = Roboflow(api_key="yzX1eRf3QPxAosZrcfkb")
project = rf.workspace("yashashree").project("helmet-detection-zktr7-p6k4t")
version = project.version(1)
dataset = version.download("yolov8")
                