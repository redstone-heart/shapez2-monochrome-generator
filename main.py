import base64
import gzip
import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image



def load_grayscale_image(image_path: str) -> np.ndarray | None:
	try:
		image = Image.open(image_path).convert("L")
		return np.array(image) / 255
	except:
		return None

def show_image(image: np.ndarray) -> None:
	plt.imshow(image, cmap = "gray", vmin = 0, vmax = 1)
	plt.show()

def mean_pool(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
	width, height = size
	thumbnail = np.zeros(size)
	block_height = image.shape[0] / height
	block_width = image.shape[1] / width
	if block_height < 1 or block_width < 1:
		raise ValueError(f"Blueprint's size can not be larger than original image.")
	for block_y in range(height):
		for block_x in range(width):
			block = image[
				int(block_y * block_height) : int((block_y + 1) * block_height),
				int(block_x * block_width) : int((block_x + 1) * block_width)
			]
			thumbnail[block_y, block_x] = np.mean(block)
	return thumbnail

def brightness_remap(image: np.ndarray, min_lightness: float, max_lightness: float) -> np.ndarray:
	normalized_image =  (image - image.min()) / (image.max() - image.min())
	return normalized_image * (max_lightness - min_lightness) + min_lightness

def posterize(image: np.ndarray, palette: list[float]) -> np.ndarray:
	palette = np.array(palette)
	posterized = image.copy()
	height, width = posterized.shape
	for y in range(height):
		for x in range(width):
			real_grayscale = posterized[y, x]
			posterized_grayscale = palette[np.argmin(np.abs(palette - real_grayscale))]
			posterized[y, x] = posterized_grayscale
	return posterized

def dither(image: np.ndarray, palette: list[float]) -> np.ndarray:
	palette = np.array(palette)
	dithered = image.copy()
	height, width = dithered.shape
	for y in range(height):
		for x in range(width):
			real_grayscale = dithered[y, x]
			posterized_grayscale = palette[np.argmin(np.abs(palette - real_grayscale))]
			dithered[y, x] = posterized_grayscale
			if y == height - 1 or x == 0 or x == width - 1:
				continue
			error = real_grayscale - posterized_grayscale
			dithered[y,     x + 1] += error * 7 / 16
			dithered[y + 1, x - 1] += error * 3 / 16
			dithered[y + 1, x    ] += error * 5 / 16
			dithered[y + 1, x + 1] += error * 1 / 16
	return dithered

def parse_blueprint(blueprint: str) -> dict:
	prefix = "SHAPEZ2-3-"
	blueprint_base64 = blueprint[len(prefix):]
	blueprint_compressed = base64.b64decode(blueprint_base64)
	blueprint_json = json.loads(gzip.decompress(blueprint_compressed).decode("UTF-8"))
	return blueprint_json

def extract_palette(blueprint: str, grayscales: list[int]) -> dict[float, str]:
	buildings: list[dict[str]] = parse_blueprint(blueprint)["BP"]["Entries"]
	grouped_buildings: defaultdict[int, list[dict]] = defaultdict(list)
	for building in buildings:
		if "X" not in building:
			building["X"] = 0
		building_offset = building["X"]
		building["X"] = "#X"
		building["Y"] = "#Y"
		grouped_buildings[building_offset].append(building)

	palette: dict[float, str] = {}
	building_offsets = list(grouped_buildings.keys())
	min_building_offset = min(building_offsets)
	max_building_offset = max(building_offsets)
	if len(grayscales) != max_building_offset - min_building_offset - 1:
		raise ValueError(f"Length of grayscales ({len(grayscales)}) doesn't match the length of building array ({max_building_offset - min_building_offset - 1}).")
	for palette_index, building_offset in enumerate(range(min_building_offset + 1, max_building_offset)):
		grayscale = grayscales[palette_index] / 255
		if building_offset not in grouped_buildings:
			palette[grayscale] = ""
			continue
		palette_buildings = json.dumps(grouped_buildings[building_offset], separators = (",", ":"))[1:-1]
		palette_buildings = palette_buildings.replace("{", "{{").replace("}", "}}")
		palette_buildings = palette_buildings.replace("#X", "{0}").replace("#Y", "{1}")
		palette[grayscale] = palette_buildings
	return palette

def build_blueprint(image: np.ndarray, palette_mapping: dict[float, str]) -> str:
	blueprint_template = '{{"V":1122,"BP":{{"$type":"Building","Icon":{{"Data":[null,null,null,null]}},"Entries":[{}],"BinaryVersion":1122}}}}'
	buildings: list[str] = []
	height, width = image.shape
	for y in range(height):
		for x in range(width):
			grayscale = image[y, x]
			building_template = palette_mapping[grayscale]
			building = building_template.format(x, y)
			if building != "":
				buildings.append(building)
	blueprint_json = blueprint_template.format(",".join(buildings))
	blueprint_compressed = gzip.compress(blueprint_json.encode("UTF-8"))
	blueprint_base64 = base64.b64encode(blueprint_compressed).decode("ASCII")
	return "SHAPEZ2-3-" + blueprint_base64 + "$"

def generate(
	grayscale_image: np.ndarray,
	size: tuple[int, int] = (54, 54),
	palette_mapping: dict[float, str] | None = None,
	brightness_correction: tuple[float, float] | None = None,
	dithering: bool = True,
	plot_image: bool = False
) -> str:
	if palette_mapping is None:
		palette_mapping = extract_palette(
			"SHAPEZ2-3-H4sIAFc7m2gA/5yUX2uDMBTFv8tlj+7BP2u7PLZuUNiDTOkGow+h3rUXQpQkDkT87tPZgoVJryUQCPmdmxNychvYgfD9IPBgnYBo4MHVJYKAdUUqJ30ED7aHQvdbsXQSxBdQtxaXfQuerpQaJrAnWaLYVMOAfevBi3aG0HbCBj5BPC49yLr6mZH2FOO3rJTbaodGS7WThqR20HoDupiFvnUXGQQfZPDMrw3lR5xSPd2liv5UwaBKqMSNKaydosPxGUyaWzuYVXteVS7t8zmmV/7h/tgp9/2ujLyqivKkMO4dD0g/aKZFHEPh/AD2fEy2VLK+kfFoDnx2kpaKXEf4WRFOoFchuvBZ2v/kCUU075ar8SsxDIX3/EpuXFfsnrIY2+bmZPmvKEWdT0qeGY72XXsmLU29Q2Opb8d9z27bXwEGAKfFB+6/BQAA$",
			[12, 24, 32, 42, 50, 64, 72, 82, 88, 94, 106, 120, 135, 160, 170, 180]
		)
	palette = list(palette_mapping.keys())
	thumbnail = mean_pool(grayscale_image, size)
	brightness_range = (palette[0], palette[-1]) if brightness_correction is None else brightness_correction
	corrected_thumbnail = brightness_remap(thumbnail, *brightness_range)
	posterized_thumbnail = (dither if dithering else posterize)(corrected_thumbnail, palette)
	if plot_image:
		show_image(posterized_thumbnail)
	blueprint = build_blueprint(posterized_thumbnail, palette_mapping)
	return blueprint



if __name__ == "__main__":
	image_path = ...  # Path to the image file.

	grayscale_image = load_grayscale_image(image_path)
	blueprint = generate(grayscale_image)
	print(blueprint)
