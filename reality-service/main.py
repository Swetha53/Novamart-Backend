# 1. Libraries import
import torch
import requests
import numpy as np
import open3d as o3d
import cv2
import os
from transformers import GLPNImageProcessor, GLPNForDepthEstimation
from supabase import create_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from dotenv import load_dotenv
import json
import logging
from aiokafka import AIOKafkaConsumer
import asyncio
import subprocess
import pycolmap
from matplotlib import pyplot as plt
import time
import bpy
import math
import shutil
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENABLE_ADVANCED_MESH_GENERATION = True

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)
global start_time

# 1. Kafka event consumer
@app.on_event("startup")
async def startup():
    logger.info("Startup...")
    await initialize()
    await consume()

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutdown")
    consumer_task.cancel()
    await consumer.stop()

async def initialize():
    logger.info("Initializing kafka consumer...")
    loop = asyncio.get_event_loop()
    global consumer
    consumer = AIOKafkaConsumer(
            "reality",
            loop=loop,
            bootstrap_servers='localhost:9092',
            group_id="reality",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    await consumer.start()

async def consume():
    logger.info("Starting kafka consumer...")
    global consumer_task
    consumer_task = asyncio.create_task(send_consumer_message(consumer))

async def send_consumer_message(consumer):
    logger.info("Consuming message...")
    try:
        async for msg in consumer:
            logger.info(f"Consumed msg: {msg.value}")
            await generate_model(msg.value)
    except Exception as e:
        logger.warn(f"Error while consuming messages: {e}")

async def generate_model(product):
    global start_time
    start_time = time.time()
    logger.info("Async 3D model generation started...")
    try:
        logger.info("Generating mesh...")
        logger.info(product)
        product_id = product.get("productId")
        images = product.get("images")
        if (len(images) > 2 and ENABLE_ADVANCED_MESH_GENERATION):
            advanced_generate_mesh(product_id, images)
        else:
            generate_mesh(product_id, images[0], images[1])
            
    except Exception as e:
        logger.info(f"Error in async 3D model generation: {e}")

def advanced_generate_mesh(product_id: str, images):
    IMAGE_PATH = "./assets/images"
    DATABASE_PATH = "./assets/database.db"
    SPARSE_MODEL_PATH = "./assets/sparse_model"
    DENSE_MODEL_PATH = "./assets/dense_model"
    MVS_PATH = "./openMVS/build/bin"
    
    os.makedirs(IMAGE_PATH, exist_ok=True)
    os.makedirs(SPARSE_MODEL_PATH, exist_ok=True)
    os.makedirs(DENSE_MODEL_PATH, exist_ok=True)
    
    # for index, image in enumerate(images):
    #     img = Image.open(requests.get(image, stream=True, timeout=10).raw)
    #     new_height = 480 if img.height > 480 else img.height
    #     new_height -= (new_height % 32)
        
    #     new_width = int(new_height * img.width / img.height)
    #     difference = new_width % 32
        
    #     if difference < 16:
    #         new_width = new_width - difference
    #     else:
    #         new_width = new_width + 32 - difference
        
    #     new_size = (new_width, new_height)
    #     img = img.resize(new_size)
    #     img.save(f"{IMAGE_PATH}/{index}.jpg")
    
    
    pycolmap.extract_features(
        DATABASE_PATH,
        IMAGE_PATH,
        sift_options={
            "max_num_features": 20000,
            "num_threads": 2
        }
    )
    logger.info("DONE: Extracting features")
    
    pycolmap.match_exhaustive(DATABASE_PATH)
    logger.info("DONE: Matching features")
    
    maps = pycolmap.incremental_mapping(
        DATABASE_PATH,
        IMAGE_PATH,
        SPARSE_MODEL_PATH
    )
    maps[0].write(SPARSE_MODEL_PATH)
    logger.info("DONE: Incremental mapping")
    
    pycolmap.undistort_images(
        image_path=IMAGE_PATH,
        input_path=f"{SPARSE_MODEL_PATH}/0",
        output_path=DENSE_MODEL_PATH,
        output_type="COLMAP"
    )
    logger.info("DONE: Undistort images")
    
    subprocess.run([
        "colmap", "model_converter",
        "--input_path", f"{DENSE_MODEL_PATH}/sparse",
        "--output_path", f"{DENSE_MODEL_PATH}/sparse",
        "--output_type", "TXT"
    ])
    logger.info("DONE: Model conversion")
    
    subprocess.run([
        f"{MVS_PATH}/InterfaceCOLMAP",
        "--working-folder", "",
        "--input-file", f"{DENSE_MODEL_PATH}",
        "--output-file", f"{DENSE_MODEL_PATH}/model.mvs"
    ], check=True)
    logger.info("DONE: Colmap Interface")
    
    subprocess.run([
        f"{MVS_PATH}/DensifyPointCloud",
        "--working-folder", "",
        "--input-file", f"{DENSE_MODEL_PATH}/model.mvs",
        "--output-file", f"{DENSE_MODEL_PATH}/model_dense.mvs",
        "--archive-type", "-1"
    ], check=True)
    logger.info("DONE: Densify Point Cloud")
    
    subprocess.run([
        f"{MVS_PATH}/ReconstructMesh",
        f"{DENSE_MODEL_PATH}/model_dense.mvs",
        "-p", f"{DENSE_MODEL_PATH}/model_dense.ply"
    ], check=True)
    logger.info("DONE: Renconstruct Mesh")
    
    subprocess.run([
        f"{MVS_PATH}/RefineMesh",
        f"{DENSE_MODEL_PATH}/model.mvs",
        "-m", f"{DENSE_MODEL_PATH}/model_dense_mesh.ply",
        "-o", f"{DENSE_MODEL_PATH}/model_dense_mesh_refine.mvs"
    ], check=True)
    logger.info("DONE: Refine Mesh")
    
    subprocess.run([
        f"{MVS_PATH}/TextureMesh",
        f"{DENSE_MODEL_PATH}/model_dense.mvs",
        "-m", f"{DENSE_MODEL_PATH}/model_dense_mesh_refine.ply",
        "-o", f"{DENSE_MODEL_PATH}/model.obj", "--export-type", "obj"
    ], check=True)
    logger.info("DONE: Texture Mesh")
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=f"{DENSE_MODEL_PATH}/model.obj")
    
    imported_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    for obj in imported_objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        obj.rotation_euler[0] = -math.pi / 2
        bpy.ops.object.transform_apply(rotation=True)
    
    bpy.ops.export_scene.gltf(
            filepath=f"{DENSE_MODEL_PATH}/{product_id}.glb",
            export_format='GLB'
        )
    
    generate_record(product_id, f"{DENSE_MODEL_PATH}/{product_id}.glb", True)

def generate_mesh(product_id: str, front_image: str, back_image: str):
    logger.info("Getting model")
    logger.info("Loading feature...")
    feature_extractor = GLPNImageProcessor.from_pretrained(
            "vinvino02/glpn-nyu"
        )
    logger.info("Feature loaded")
    
    logger.info("Loading model...")
    model = GLPNForDepthEstimation.from_pretrained("vinvino02/glpn-nyu")
    logger.info("Model loaded")
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    logger.info(f"Setting model for Device: ${device}")
    model.to(device)
    logger.info("Model converted")
    logger.info("Generate mesh started")
    logger.info("Loading images...")
    try:
        front_side = Image.open(
                requests.get(front_image, stream=True, timeout=10).raw
            )
        back_side = Image.open(
                requests.get(back_image, stream=True, timeout=10).raw
            )
    except requests.exceptions.RequestException as e:
        logger.info(f"Image download failed: {e}")
        return
    logger.info("Images loaded")

    logger.info("Removing background of images...")
    front_side = remove_background(front_side)
    back_side = remove_background(back_side)
    logger.info("Background of images removed")

    logger.info("Resizing images...")
    new_height = 480 if front_side.height > 480 else front_side.height
    new_height -= (new_height % 32)
    
    new_width = int(new_height * front_side.width / front_side.height)
    difference = new_width % 32
    
    if difference < 16:
        new_width = new_width - difference
    else:
        new_width = new_width + 32 - difference
    
    new_size = (new_width, new_height)
    front_side = front_side.resize(new_size)
    back_side = back_side.resize(new_size)
    logger.info("Images resized")
    
    logger.info("Preparing images for the model...")
    # 4.3.1. Front Side
    front_inputs = feature_extractor(
            images=front_side,
            return_tensors="pt"
        ).to(device)
    
    # 4.3.2. Back Side
    back_inputs = feature_extractor(
            images=back_side,
            return_tensors="pt"
        ).to(device)
    logger.info("Images prepared for the model")

    logger.info("Getting prediction from the model...")
    with torch.no_grad():
        
        # 4.4.1. Front Side
        front_outputs = model(**front_inputs)
        front_predicted_depth = front_outputs.predicted_depth
        
        # 4.4.2. Back Side
        back_outputs = model(**back_inputs)
        back_predicted_depth = back_outputs.predicted_depth
        
    front_gray = np.array(front_side.convert("L"))
    back_gray = np.array(back_side.convert("L"))
    front_predicted_depth = front_predicted_depth.squeeze(0)
    back_predicted_depth = back_predicted_depth.squeeze(0)
    logger.info("Model prediction received")

    logger.info("Set depth to zero where the original images are black...")
    front_predicted_depth[front_gray == 0] = 0
    back_predicted_depth[back_gray == 0] = 0
    logger.info("Depth set for the images")
    
    logger.info("Post Processing started...")
    pad = 16
    
    # 4.6.1. Front Side
    front_output = front_predicted_depth.squeeze().cpu().numpy() * 1000.0
    front_output = front_output[pad:-pad, pad:-pad]
    front_side = front_side.crop((
            pad,
            pad,
            front_side.width - pad,
            front_side.height - pad
        ))
    
    # 4.6.2. Back Side
    back_output = back_predicted_depth.squeeze().cpu().numpy() * 1000.0
    back_output = back_output[pad:-pad, pad:-pad]
    back_side = back_side.crop((
            pad,
            pad,
            back_side.width - pad,
            back_side.height - pad
        ))
    logger.info("Post processing completed")
    
    # logger.info("Visualizing the predictions...")
    # Front Side
    # fig, ax = plt.subplots(1, 2)
    # ax[0].imshow(front_side)
    # ax[0].tick_params(
    #         left=False, 
    #         bottom=False, 
    #         labelleft=False, 
    #         labelbottom=False
    #     )
    # ax[1].imshow(front_output, cmap="plasma")
    # ax[1].tick_params(
    #         left=False, 
    #         bottom=False, 
    #         labelleft=False, 
    #         labelbottom=False
    #     )
    # plt.tight_layout()
    # plt.pause(5)
    
    # Back Side
    # fig, ax = plt.subplots(1, 2)
    # ax[0].imshow(back_side)
    # ax[0].tick_params(
    #         left=False, 
    #         bottom=False, 
    #         labelleft=False, 
    #         labelbottom=False
    #     )
    # ax[1].imshow(back_output, cmap="plasma")
    # ax[1].tick_params(
    #         left=False, 
    #         bottom=False, 
    #         labelleft=False, 
    #         labelbottom=False
    #     )
    # plt.tight_layout()
    # plt.pause(5)
    # logger.info("Done visualizing the predictions")
    
    logger.info("Preparing depth images for Open3D")
    # 4.7.1. Front Side
    front_width, front_height = front_side.size
    front_depth_image = (
            front_output * 255 / np.max(front_output)
        ).astype('uint8')
    front_array = np.array(front_side)
    
    front_depth_o3d = o3d.geometry.Image(front_depth_image)
    front_o3d = o3d.geometry.Image(front_array)
    front_rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            front_o3d,
            front_depth_o3d,
            convert_rgb_to_intensity=False
        )
    
    # 4.7.2. Back Side
    back_width, back_height = back_side.size
    back_depth_image = (
            back_output * 255 / np.max(back_output)
        ).astype('uint8')
    back_array = np.array(back_side)

    back_depth_o3d = o3d.geometry.Image(back_depth_image)
    back_o3d = o3d.geometry.Image(back_array)
    back_rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            back_o3d,
            back_depth_o3d,
            convert_rgb_to_intensity=False
        )
    logger.info("Depth images prepared for Open3D")
    
    logger.info("Creating camera for the images...")
    logger.info(
            f"Front Intrinsics: width={front_width}, height={front_height}"
        )
    logger.info(f"Back Intrinsics: width={back_width}, height={back_height}")
    # 4.8.1. Front Side
    front_camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    front_camera_intrinsic.set_intrinsics(
            front_width,
            front_height,
            500,
            500,
            front_width/2,
            front_height/2
        )
    
    # 4.8.2. Back Side
    back_camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    back_camera_intrinsic.set_intrinsics(
            back_width, 
            back_height, 
            500, 
            500, 
            back_width/2, 
            back_height/2
        )
    logger.info("Camera created for the images")
    
    logger.info("Creating Open3D Point Cloud...")
    generate_point_cloud(
            product_id,
            front_rgbd_image, 
            front_camera_intrinsic, 
            back_rgbd_image, 
            back_camera_intrinsic
        )

def remove_background(image):
    logger.info("Remove background started")
    image_np = np.array(image)
    
    mask = np.zeros(image_np.shape[:2], np.uint8)
    
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    height, width = image_np.shape[:2]
    rect = (10, 10, width - 20, height - 20)
    
    cv2.grabCut(
            image_np,
            mask, 
            rect, 
            bgd_model, 
            fgd_model, 
            5, 
            cv2.GC_INIT_WITH_RECT
        )
    
    mask_2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    result = image_np * mask_2[:, :, np.newaxis]
    
    return Image.fromarray(result)

def generate_point_cloud(product_id, front_rgbd_image, front_camera_intrinsic, back_rgbd_image, back_camera_intrinsic):
    # 4.9.1. Front Side
    front_pcd_raw = o3d.geometry.PointCloud.create_from_rgbd_image(
        front_rgbd_image,
        front_camera_intrinsic
    )
    logger.info("Front Open3D Point Cloud created")

    # 4.9.2. Back Side
    back_pcd_raw = o3d.geometry.PointCloud.create_from_rgbd_image(
        back_rgbd_image,
        back_camera_intrinsic
    )
    
    # o3d.visualization.draw_geometries([front_pcd_raw])
    # o3d.visualization.draw_geometries([back_pcd_raw])

    logger.info("Back Open3D Point Cloud created")

    logger.info("Post Processing the 3D Point Cloud...")
    logger.info("Removing outliers...")
    # 4.10.1.1. Front Side
    _, ind = front_pcd_raw.remove_statistical_outlier(
            nb_neighbors=20, 
            std_ratio=6.0
        )
    front_pcd = front_pcd_raw.select_by_index(ind)

    # 4.10.1.2. Back Side
    _, ind = back_pcd_raw.remove_statistical_outlier(
            nb_neighbors=20, 
            std_ratio=6.0
        )
    back_pcd = back_pcd_raw.select_by_index(ind)
    logger.info("Outliers removed")

    logger.info("Estimating normals...")
    # 4.10.2.1. Front Side
    front_pcd.estimate_normals()
    front_pcd.orient_normals_to_align_with_direction()
    front_pcd.normalize_normals()

    # 4.10.2.2. Back Side
    back_pcd.estimate_normals()
    back_pcd.orient_normals_to_align_with_direction()
    back_pcd.normalize_normals()
    logger.info("Normals estimated")
    
    # o3d.visualization.draw_geometries([front_pcd])
    # o3d.visualization.draw_geometries([back_pcd])
    logger.info("Post Processing the 3D Point Cloud completed")
    
    logger.info("Surface reconstructing...")
    # 4.11.1. Front Side
    front_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            front_pcd, 
            depth=12, 
            n_threads=1
        )[0]
    bbox = back_pcd.get_axis_aligned_bounding_box()
    front_mesh = front_mesh.crop(bbox)
    front_rotation = front_mesh.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    front_mesh.rotate(front_rotation, center=(0, 0, 0))
    front_mesh.triangles = o3d.utility.Vector3iVector(
        np.asarray(front_mesh.triangles)[:, ::-1]
    )
    front_mesh.remove_unreferenced_vertices()

    # 4.11.2. Back Side
    back_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            back_pcd, 
            depth=12, 
            n_threads=1
        )[0]
    bbox = back_pcd.get_axis_aligned_bounding_box()
    back_mesh = back_mesh.crop(bbox)
    back_mesh.transform(np.array([[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, -1, 0],
                                  [0, 0, 0, 1]]))
    back_rotation = back_mesh.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    back_mesh.rotate(back_rotation, center=(0, 0, 0))
    bbox = front_mesh.get_axis_aligned_bounding_box()
    size = bbox.get_max_bound() - bbox.get_min_bound()
    depth_extent = size[2]
    translation_factor = -(size[2] * 10000 + 1)
    back_mesh.translate((0, 0, translation_factor * depth_extent))
    back_mesh.remove_unreferenced_vertices()
    logger.info("Surface reconstructed")

    logger.info("Merging meshes...")
    full_mesh = front_mesh + back_mesh
    full_mesh.compute_vertex_normals()
    full_mesh = full_mesh.remove_duplicated_triangles()
    full_mesh = full_mesh.remove_non_manifold_edges()
    full_mesh = full_mesh.remove_duplicated_vertices()
    full_mesh = full_mesh.simplify_quadric_decimation(
            target_number_of_triangles=200000
        )
    scale_factor = 1000

    full_mesh.scale(scale_factor, center=full_mesh.get_center())
    logger.info("Meshes merged")
    logger.info("Saving mesh in local...")
    MESH_PATH = f"./assets/{product_id}.glb"
    o3d.io.write_triangle_mesh(
            MESH_PATH, 
            full_mesh, 
            write_ascii=False, 
            compressed=True
        )
    # o3d.visualization.draw_geometries([full_mesh], mesh_show_back_face=True)
    logger.info("Mesh saved in local")

    logger.info("Mesh generation completed")

    generate_record(product_id, f"./assets/{product_id}.glb")

def generate_record(product_id, file_path, advanced=False):
    global start_time
    storage_path = f"{product_id}.glb"
    with open(file_path, "rb") as file:
        logger.info("Saving 3D model in database...")
        resp = supabase.storage.from_("Products").upload(
                storage_path, 
                file, 
                {"content-type": "model/gltf-binary"}
            )
        logger.info(resp)

        resp = supabase.storage.from_("Products").get_public_url(storage_path)
        logger.info(resp)

        supabase.table("Reality").insert(
                {"product_id": product_id, "asset_url": resp}
            ).execute()
        logger.info("3D model saved in database")
        
        logger.info("Deleting 3D model from local...")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted local 3D model: {file_path}")
        else:
            logger.info("File not found for deletion.")
        
        if advanced:
            logger.info("Deleting sparse model from local...")
            if os.path.exists("./assets/sparse_model") and os.path.isdir("./assets/sparse_model"):
                shutil.rmtree("./assets/sparse_model")
                logger.info(
                        "Deleted Sparse Model Directory: ./assets/sparse_model"
                    )
            else:
                logger.info("File not found for deletion.")
            
            logger.info("Deleting dense model from local...")
            if os.path.exists("./assets/dense_model") and os.path.isdir("./assets/dense_model"):
                shutil.rmtree("./assets/dense_model")
                logger.info(
                        "Deleted Dense Model Directory: ./assets/dense_model"
                    )
            else:
                logger.info("File not found for deletion.")
            
            logger.info("Deleting database from local...")
            if os.path.exists("./assets/database.db"):
                os.remove("./assets/database.db")
                logger.info("Deleted Database: ./assets/database.db")
            else:
                logger.info("File not found for deletion.")
                
            logger.info("Deleting product images from local...")
            if os.path.exists("./assets/images") and os.path.isdir("./assets/dense_model"):
                shutil.rmtree("./assets/images")
                logger.info("Deleted Images: ./assets/images")
            else:
                logger.info("File not found for deletion.")
        
    logger.info("Async 3D model generation ended successfully")
    logger.info(time.time() - start_time)

# 2. API to return 3D Model
@app.get("/reality/{product_id}")
def get_model(product_id: str):
    data = supabase.table("Reality").select("*").eq(
            "product_id", 
            product_id
        ).execute()
    return data

# 3. API to delete 3D Model
@app.delete("/reality/delete/{product_id}")
def delete_model(product_id: str):
    storage_path = f"{product_id}.glb"
    supabase.table("Reality").delete().eq("product_id", product_id).execute()
    supabase.storage.from_("Products").remove([storage_path])
