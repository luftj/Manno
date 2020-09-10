# Manno, the map annotator

this tool is for quickly annotating ground-truth labels for OCR on maps. 

---

![preview image of ui](images/preview.jpg)

## Installation

Requires
* Python3

```$ python3 -m pip install -r requirements.txt ```

## Usage

Set the desired buffer, output path and json keys in main.py
Then run `$ python3 main.py [-h] [--inplace] json image ` with the path to your geojson file with text detections bounding boxes (see sample in `test_data`) and the path to the corresponding map image.
Setting `--inplace` leads to no separate output file being generated, instead, the annotations will be added to the input json file.
