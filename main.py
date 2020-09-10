import argparse
import tkinter
import json
from PIL import Image, ImageTk, ImageDraw


step = -1
truth_text_list = []

img_buffer_percent = 50
outpath = "annotated_result.json"
key_ocr_text = "NameBeforeDictionary"
key_annotation_result = "truth"

def finish_cb(e):
    finish()

def finish():
    main_win.destroy()

    # save annotated json to disk
    if len(truth_text_list) != len(json_data["features"]):
        print("Warning! text list wrong size!", len(truth_text_list), len(json_data["features"]))
        # raise Exception("text list wrong size!",len(truth_text_list),len(json_data["features"]))

    for idx, entry in enumerate(truth_text_list):
        json_data["features"][idx]["properties"][key_annotation_result] = entry

    print("Saving to disk at %s ..." % outpath)
    with open(outpath,"w",encoding="utf-8") as file:
        json.dump(json_data,file)

def label_step_cb(e):
    label_step()

def label_step():
    global step
    step += 1

    if step >= len(json_data["features"]):
        print("no more features, exiting")
        finish()

    if step > 0:
        # store user entered ground truth value
        truth_text = entry_truth.get()
        truth_text_list.append(truth_text)

    # load text detection bbox from json
    coords = json_data["features"][step]["geometry"]["coordinates"][0]
    x_coords = [p[0] for p in coords]
    y_coords = [-p[1] for p in coords]
    w_buf = (max(x_coords) - min(x_coords)) / 100 * img_buffer_percent
    h_buf = (max(y_coords) - min(y_coords)) / 100 * img_buffer_percent

    # define cutout window from detection bbox
    l,t,r,b = min(x_coords) - w_buf, min(y_coords) - h_buf, max(x_coords) + w_buf, max(y_coords) + h_buf
    detail_img = map_img.crop((l,t,r,b))

    # draw bbox rect
    draw = ImageDraw.Draw(detail_img)
    draw.rectangle(((w_buf,h_buf), (max(x_coords) - min(x_coords) + w_buf, max(y_coords) - min(y_coords) + h_buf)), outline="red", width=2)

    # update image label
    photo = ImageTk.PhotoImage(detail_img)
    label_img["image"] = photo
    label_img.configure(image=photo)
    label_img.image = photo

    # update detection label
    ocr_text = json_data["features"][step]["properties"][key_ocr_text]
    label_detection["text"] = "Detection:  " + ocr_text # show OCR result
    entry_truth.delete(0, tkinter.END) # clear input field
    if key_annotation_result in  json_data["features"][step]["properties"]:
        entry_truth.insert(0, json_data["features"][step]["properties"][key_annotation_result]) # insert existing annotation
    entry_truth.focus_set()

    label_progress["text"] = "%d/%d" % (step, len(json_data["features"]))

    print(step,ocr_text,(l,t,r,b))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json",help="filepath to json of text detection")
    parser.add_argument("image",help="filepath to corresponding map image")
    parser.add_argument("--inplace",help="set to change truth annotations inplace in input json",action="store_true")
    args = parser.parse_args()

    if args.inplace:
        outpath = args.json

    # load json detections
    with open(args.json,encoding="utf-8") as file:
        json_data = json.load(file)
    if len(json_data["features"]) == 0:
        print("no features! exiting...")
        exit()

    # load map image
    map_img  = Image.open(args.image) 

    main_win = tkinter.Tk()
    main_win.title("Manno -- Annotating: %s" % args.image)
    main_win.iconphoto(False, tkinter.PhotoImage(file='images/icon.png'))
    
    label_img = tkinter.Label(main_win)
    label_img.pack()
    label_detection = tkinter.Label(main_win, text="Detection")
    label_detection.pack()
    entry_truth = tkinter.Entry(main_win)
    entry_truth.pack()
    b1 = tkinter.Button(main_win, text="Next [RETURN]", command=label_step)
    b1.pack()
    b2 = tkinter.Button(main_win, text="Save & Quit [ESCAPE]", command=finish)
    b2.pack()
    label_progress = tkinter.Label(main_win,text="0/0")
    label_progress.pack()
    main_win.bind("<Return>", label_step_cb)
    main_win.bind("<Escape>", finish_cb)
    label_step() # start with first image immediately
    main_win.mainloop()