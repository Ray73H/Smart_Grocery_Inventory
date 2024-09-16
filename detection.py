import numpy as np
import cv2
from collections import defaultdict

# Function to load coco labels from text file
def load_coco_labels(file_path):
    coco_labels = {}
    with open(file_path, 'r') as f:
        for line in f:
            class_id, label = line.strip().split(maxsplit=1)
            coco_labels[int(class_id)] = label
    return coco_labels

def run_detection(image_path, coco_labels, detection_model):
    # Load an image and preprocess it
    image_np = cv2.imread(image_path)
    input_tensor = np.expand_dims(image_np, axis=0)  # Add batch dimension

    # Perform object detection
    detections = detection_model(input_tensor)

    # Extract detection results
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}

    # Bounding boxes, class labels, and confidence scores
    boxes = detections['detection_boxes']
    scores = detections['detection_scores']
    classes = detections['detection_classes'].astype(np.int64)

    detection_result = defaultdict(int)
    # Draw bounding boxes on the image
    for i in range(num_detections):
        if scores[i] > 0.5:
            box = boxes[i] * np.array([image_np.shape[0], image_np.shape[1], image_np.shape[0], image_np.shape[1]])
            (startY, startX, endY, endX) = box.astype("int")
            label = coco_labels.get(classes[i], "Unknown")

            cv2.rectangle(image_np, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(image_np, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            detection_result[label] = detection_result[label] + 1


    # Display the image with bounding boxes
    cv2.imshow(image_path, image_np)
    print("Confirm to add all the boxes into your inventory")
    print("Confirm: (ENTER), Cancel: (ESC)")
    while True:
        key = cv2.waitKey(0)
        if key == 27: # ESC key
            cv2.destroyAllWindows()
            return False
        elif key == 13:
            cv2.destroyAllWindows()
            return detection_result

