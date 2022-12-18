import os
import glob
import yaml
from tqdm import tqdm
import argparse
import torch
import nibabel as nib
import numpy as np

from monai.networks.nets import UNet
from monai.data import DataLoader, Dataset
from monai.networks.layers import Norm
from monai.utils import set_determinism
from monai.inferers import sliding_window_inference
from monai.transforms import (
	Compose,
	AsDiscrete,
	EnsureType,
	AsDiscrete,
	Spacing,
	Resize,
	Orientation,
	AddChannel,
	LoadImaged,
	AddChanneld,
	Spacingd,
	Orientationd,
	ScaleIntensityRanged,
	EnsureTyped
)
from EmphysemaSeg.utils import clip_mask_overlay, nearest_label_filling, get_largest_cc, BodyMaskd

import resource
rlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (4096, rlimit[1]))


def infer(config, emp_seg=False, vis=False):
	print(emp_seg, vis)
	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

	# Data
	data_dir = config['data_dir']
	images = glob.glob(os.path.join(data_dir, "*.nii.gz"))
	infer_loader = infer_dataloader(config, images)

	model = UNet(
		spatial_dims=3,
		in_channels=1,
		out_channels=6,
		channels=(32, 64, 128, 256, 512),
		strides=(2, 2, 2, 2),
		num_res_units=2,
		norm=Norm.BATCH,
	).to(device)
	model.load_state_dict(torch.load(config['model_path']))

	model.eval()
	with torch.no_grad():
		for batch in tqdm(infer_loader):
			data, image_path = batch["image"].to(
				device), batch["image_path"][0]
			fname = os.path.basename(image_path).split(".nii.gz")[0]

			resample_label_map_file_path = os.path.join(config["seg_dir"], f"{fname}.nii.gz")
			if os.path.exists(resample_label_map_file_path):
				print(f'Skip {fname} - already processed')
				continue

			try:
				raw_nii = nib.load(image_path)
				axcodes = nib.orientations.aff2axcodes(raw_nii.affine)
				axcodes = ''.join(axcodes)
				pixdim = raw_nii.header.get_zooms()
				spatial_size = raw_nii.shape

				post_pred_transforms = Compose([
					EnsureType(),
					AsDiscrete(argmax=True),
					Orientation(axcodes=axcodes),
					Spacing(pixdim=pixdim, mode="nearest"),
					Resize(spatial_size=spatial_size, mode="nearest"),
				])
				pred = sliding_window_inference(data, (96, 96, 96), 4, model)
				pred = post_pred_transforms(pred[0].detach().cpu().numpy())
				lobe_map = nearest_label_filling(pred[0], get_largest_cc(pred[0]))

				if emp_seg:
					# emp class encoded in second channel
					lung_mask = np.where(lobe_map, 1, 0)
					img = raw_nii.get_fdata()
					emp = np.where(img < -950, 1, 0)
					emp = np.multiply(lung_mask, emp)
					label_map = np.array([lobe_map, emp])
				else:
					label_map = lobe_map.copy()

				label_map_nii = nib.Nifti1Image(label_map, header=raw_nii.header, affine=raw_nii.affine)
				label_map_file_path = os.path.join(config["seg_dir"], f"{fname}_lobe.nii.gz")
				nib.save(label_map_nii, label_map_file_path)

				if vis:
					if emp_seg:
						# labal map encodes emphysema as 7
						label_map = np.where(emp, 7, lobe_map)
					for plane in ["coronal", "axial", "sagittal"]:
						clip_mask_overlay(raw_nii.get_fdata(), label_map,
										  os.path.join(config["clip_dir"], f"{fname}_{plane}.png"),
										  clip_plane=plane,
										  img_vrange=(-1000, 0))

				# Resample to the original data space using niftyreg
				reg_resample_path = config['reg_resample']
				# resample_label_map_file_path = os.path.join(config["seg_dir"], f"{fname}.nii.gz")
				resample_cmd = f'{reg_resample_path} ' \
							   f'-ref {image_path} ' \
							   f'-flo {label_map_file_path} ' \
							   f'-res {resample_label_map_file_path} -inter 0'
				os.system(resample_cmd)
				remove_cmd = f'rm {label_map_file_path}'
				os.system(remove_cmd)
			except:
				print(f'Cannot process {fname}')


def infer_dataloader(config, val_images):
	test_transforms = Compose([
		LoadImaged(keys=["image"]),
		AddChanneld(keys=["image"]),
		Spacingd(keys=["image"], pixdim=config["pix_dim"], mode=("bilinear")),
		Orientationd(keys=["image"], axcodes="RAS"),
		BodyMaskd(keys=["image"]),
		ScaleIntensityRanged(keys=["image"], a_min=config["window"][0], a_max=config["window"][1], b_min=0.0, b_max=1.0,
							 clip=True),
		EnsureTyped(keys=["image"]),
	])
	val_files = [
		{"image": image_name, "image_path": image_name}
		for image_name in val_images
	]
	infer_ds = Dataset(data=val_files, transform=test_transforms)
	infer_loader = DataLoader(infer_ds, batch_size=1,
							  num_workers=config["num_workers"], shuffle=False)
	return infer_loader


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', type=str, default='config.YAML')
	parser.add_argument('--emp', action="store_true", default=False)
	parser.add_argument('--vis', action="store_true", default=False)
	args = parser.parse_args()

	with open(args.config) as f:
		config = yaml.load(f, Loader=yaml.FullLoader)

	os.makedirs(config["seg_dir"], exist_ok=True)

	infer(config, emp_seg=args.emp, vis=args.vis)


if __name__ == '__main__':
	main()
