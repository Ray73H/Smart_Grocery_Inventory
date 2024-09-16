from detection import load_coco_labels, run_detection
from database import MongoDBConnection
import tensorflow as tf

def image_process(db, image_path, detection_model):
    coco_labels = load_coco_labels('coco_labels.txt')
    detection_result = run_detection(image_path, coco_labels, detection_model)

    if(detection_result):
        for item_name, quantity in detection_result.items():
            db.insert_item(item_name, quantity)

def show_inventory(db):
    items = db.get_all_items()

    if items:
        for item in items:
            print(f"{item['item_name']}: {item['quantity']}")
    else:
        print("No items in inventory.")

def main():
    db = MongoDBConnection()
    db.connect()
    print("\nGrocery Inventory CLI")
    print("Commands:")
    print("  image <image_path> - Use image to add to inventory")
    print("  add <item_name> <quantity> - Add an item to inventory")
    print("  remove <item_name> <quantity> - Remove an item from inventory")
    print("  show - Show all items in inventory")
    print("  exit - Exit the application")
    modelLoaded = False

    try:
        while True:
            # Read user input
            user_input = input("Enter command: ").strip()

            if user_input == 'exit':
                print("Exiting the application.")
                break

            # Parse the user input
            args = user_input.split()
            if not args:
                print("No command provided. Please try again.")
                continue

            command = args[0]
            if command == 'image' and len(args) == 2:
                try:
                    if(not modelLoaded):
                        # Load the EfficientDet D7 model from the SavedModel directory
                        model_dir = '../models/efficientdet_d7_coco17_tpu-32/saved_model'
                        detection_model = tf.saved_model.load(model_dir)
                        modelLoaded = True

                    image_path = args[1]
                    image_process(db, image_path, detection_model)
                except:
                    print("Invalid image path")
            elif command == 'add' and len(args) == 3:
                try:
                    item_name = args[1]
                    quantity = int(args[2])
                    db.insert_item(item_name, quantity)
                except ValueError:
                    print("Invalid quantity. Please enter an integer.")
            elif command == 'remove' and len(args) == 3:
                try:
                    item_name = args[1]
                    quantity = int(args[2])
                    db.remove_item(item_name, quantity)
                except ValueError:
                    print("Invalid quantity. Please enter an integer.")
            elif command == 'show':
                show_inventory(db)
            else:
                print("Unknown command or invalid arguments. Please try again.")
    finally:
        db.close()

if __name__ == "__main__":
    main()