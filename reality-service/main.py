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
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

origins = [
    "*",  # Allow requests from this origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows access from specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

class Request(BaseModel):
    product_id: str
    front_image: str
    back_image: str
    

# 2. API to return 3D Model
@app.get("/reality/{product_id}")
def get_model(product_id: str):
    data = supabase.table("Reality").select("*").eq("product_id", product_id).execute()
    return data

# 3. API to delete 3D Model
@app.delete("/reality/delete/{product_id}")
def delete_model(product_id: str):
    storage_path = f"{product_id}.glb"
    supabase.table("Reality").delete().eq("product_id", product_id).execute()
    supabase.storage.from_("Products").remove([storage_path])

# 4. API to generate and store 3D Model
@app.post("/reality/generate")
def generate_model(request: Request):
    generate_mesh(request.product_id, request.front_image, request.back_image)
    file_path = f"./assets/{request.product_id}.glb"
    storage_path = f"{request.product_id}.glb"
    with open(file_path, "rb") as file:
        resp = supabase.storage.from_("Products").upload(storage_path, file, {"content-type": "model/gltf-binary"})
        print(resp)
        
        resp = supabase.storage.from_("Products").get_public_url(storage_path)
        print(resp)
    
        supabase.table("Reality").insert({"product_id": request.product_id, "asset_url": resp}).execute()
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted local file: {file_path}")
    else:
        print("File not found for deletion.")

# 5. Function to generate mesh
def generate_mesh(product_id: str, front_image: str, back_image: str):
    # 4.1. Getting Model
    
    feature_extractor = GLPNImageProcessor.from_pretrained("vinvino02/glpn-nyu")
    model = GLPNForDepthEstimation.from_pretrained("vinvino02/glpn-nyu")
    device = "mps"
    model.to(device)
    
    # 4.2. Loading and resizing the Image
    
    front_side = Image.open(requests.get(front_image, stream=True).raw)  
    back_side = Image.open(requests.get(back_image, stream=True).raw)
    
    front_side = remove_background(front_side)
    back_side = remove_background(back_side)

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
    
    # 4.3. Preparing the Image for the Model
    
    # 4.3.1. Front Side
    front_inputs = feature_extractor(images=front_side, return_tensors="pt").to(device)
    
    # 4.3.2. Back Side
    back_inputs = feature_extractor(images=back_side, return_tensors="pt").to(device)
    
    
    # 4.4. Getting prediction from the Model
    
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

    # 4.5. Set depth to zero where the original image is black
    
    front_predicted_depth[front_gray == 0] = 0
    back_predicted_depth[back_gray == 0] = 0
        
    # 4.6. Post-Processing
        
    pad = 16
    
    # 4.6.1. Front Side
    front_output = front_predicted_depth.squeeze().cpu().numpy() * 1000.0
    front_output = front_output[pad:-pad, pad:-pad]
    front_side = front_side.crop((pad, pad, front_side.width - pad, front_side.height - pad))
    
    # 4.6.2. Back Side
    back_output = back_predicted_depth.squeeze().cpu().numpy() * 1000.0
    back_output = back_output[pad:-pad, pad:-pad]
    back_side = back_side.crop((pad, pad, back_side.width - pad, back_side.height - pad))
    
    # 4.7. Preparing depth image for Open3D
    
    # 4.7.1. Front Side
    front_width, front_height = front_side.size
    front_depth_image = (front_output * 255 / np.max(front_output)).astype('uint8')
    front_array = np.array(front_side)
    
    front_depth_o3d = o3d.geometry.Image(front_depth_image)
    front_o3d = o3d.geometry.Image(front_array)
    front_rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        front_o3d, front_depth_o3d, convert_rgb_to_intensity=False)
    
    # 4.7.2. Back Side
    back_width, back_height = back_side.size
    back_depth_image = (back_output * 255 / np.max(back_output)).astype('uint8')
    back_array = np.array(back_side)

    back_depth_o3d = o3d.geometry.Image(back_depth_image)
    back_o3d = o3d.geometry.Image(back_array)
    back_rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        back_o3d, back_depth_o3d, convert_rgb_to_intensity=False)
    
    # 4.8. Creating a Camera
    
    # 4.8.1. Front Side
    front_camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    front_camera_intrinsic.set_intrinsics(
        front_width, front_height, 500, 500, front_width/2, front_height/2)
    
    # 4.8.2. Back Side
    back_camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    back_camera_intrinsic.set_intrinsics(
        back_width, back_height, 500, 500, back_width/2, back_height/2)
    
    # 4.9. Creating Open3D Point Cloud
    
    # 4.9.1. Front Side
    front_pcd_raw = o3d.geometry.PointCloud.create_from_rgbd_image(
        front_rgbd_image, front_camera_intrinsic)
    
    # 4.9.2. Back Side
    back_pcd_raw = o3d.geometry.PointCloud.create_from_rgbd_image(
        back_rgbd_image, back_camera_intrinsic)
    
    # 4.10. Post-Processing the 3D Point Cloud
    
    # 4.10.1. Outliers removal
    # 4.10.1.1. Front Side
    _, ind = front_pcd_raw.remove_statistical_outlier(
        nb_neighbors=20, std_ratio=6.0)
    front_pcd = front_pcd_raw.select_by_index(ind)
    
    # 4.10.1.2. Back Side
    _, ind = back_pcd_raw.remove_statistical_outlier(
        nb_neighbors=20, std_ratio=6.0)
    back_pcd = back_pcd_raw.select_by_index(ind)
    
    # 4.10.2. Estimate normals
    # 4.10.2.1. Front Side
    front_pcd.estimate_normals()
    front_pcd.orient_normals_to_align_with_direction()
    front_pcd.normalize_normals()
    
    # 4.10.2.2. Back Side
    back_pcd.estimate_normals()
    back_pcd.orient_normals_to_align_with_direction()
    back_pcd.normalize_normals() 
    
    # 4.11. Surface Reconstruction
    
    # 4.11.1. Front Side
    front_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        front_pcd, depth=12, n_threads=1)[0]
    bbox = back_pcd.get_axis_aligned_bounding_box()
    front_mesh = front_mesh.crop(bbox)
    front_rotation = front_mesh.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    front_mesh.rotate(front_rotation, center=(0,0,0))
    front_mesh.triangles = o3d.utility.Vector3iVector(
        np.asarray(front_mesh.triangles)[:, ::-1]
    )
    front_mesh.remove_unreferenced_vertices()
    
    # 4.11.2. Back Side
    back_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        back_pcd, depth=12, n_threads=1)[0]
    bbox = back_pcd.get_axis_aligned_bounding_box()
    back_mesh = back_mesh.crop(bbox)
    back_mesh.transform(np.array([[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, -1, 0],
                              [0, 0, 0, 1]]))
    back_rotation = back_mesh.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    back_mesh.rotate(back_rotation, center=(0,0,0))
    bbox = front_mesh.get_axis_aligned_bounding_box()
    size = bbox.get_max_bound() - bbox.get_min_bound()
    depth_extent = size[2]
    back_mesh.translate((0, 0, -4*depth_extent))
    back_mesh.remove_unreferenced_vertices()
    
    full_mesh = front_mesh + back_mesh
    full_mesh.compute_vertex_normals()
    full_mesh = full_mesh.remove_duplicated_triangles()
    full_mesh = full_mesh.remove_non_manifold_edges()
    full_mesh = full_mesh.remove_duplicated_vertices()
    full_mesh = full_mesh.simplify_quadric_decimation(target_number_of_triangles=200000)
    # o3d.visualization.draw_geometries([full_mesh])
    scale_factor = 1000

    full_mesh.scale(scale_factor, center=full_mesh.get_center())
    MESH_PATH = f"./assets/{product_id}.glb"
    o3d.io.write_triangle_mesh(MESH_PATH, full_mesh, write_ascii=False, compressed=True)

def remove_background(image):
    image_np = np.array(image)

    # Create a mask
    mask = np.zeros(image_np.shape[:2], np.uint8)

    # Define background/foreground models
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Define a rectangle around the object
    height, width = image_np.shape[:2]
    rect = (10, 10, width - 20, height - 20)

    # Apply GrabCut
    cv2.grabCut(image_np, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    # Set all background pixels to black
    mask_2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    result = image_np * mask_2[:, :, np.newaxis]

    # Convert back to PIL
    return Image.fromarray(result)

