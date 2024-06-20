import random
import cv2

def plot_one_box(x, img, color=None, label=None, line_thickness=3, label_position='top', label_offset=0):
    img_h, img_w = img.shape[0], img.shape[1]
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    x0, x1, x2, x3 = x
    if label and label_position == 'top' and label_offset != 0:
        x1 = max(0, x1 - label_offset)
    elif label and label_position == 'bottom' and label_offset != 0:
        x3 = min(img_h, x3 + label_offset)
    c1, c2 = (int(x0), int(x1)), (int(x2), int(x3))    
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        if label_position == 'top':
            c2 = min(img_w, c1[0] + t_size[0]), max(0, c1[1] - t_size[1] - 3)
        elif label_position == 'bottom':
            c1 = c1[0], min(img_h, c2[1] + t_size[1] + 3)
            c2 = min(img_w, c1[0] + t_size[0]), min(img_h, c2[1] + 3)
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [0,0,0], thickness=tf, lineType=cv2.LINE_AA)


def draw_confirmation_prompt(img, message, accept_button="Enter", reject_button="Escape"):
    # Calculate relative dimensions for centering the text and the box
    img_height, img_width = img.shape[:2]
    box_width, box_height = int(img_width * 0.5), int(img_height * 0.2)  # Box width and height as a fraction of image size
    top_left = ((img_width - box_width) // 2, (img_height - box_height) // 2)
    bottom_right = (top_left[0] + box_width, top_left[1] + box_height)

    # Draw a rectangle for the dialog box with a border
    cv2.rectangle(img, top_left, bottom_right, (200, 200, 200), -1)  # Dialog box
    cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 2)  # Border

    # Positioning and drawing the main message
    text_scale = 1
    textsize = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, text_scale, 2)[0]
    text_x = top_left[0] + (box_width - textsize[0]) // 2
    text_y = top_left[1] + round(box_height // 2 - (0.2 * box_height))
    cv2.putText(img, message, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 0, 0), 2)

    # Positioning and drawing the instruction text
    instruction_text = f"{accept_button} - ACCEPT"
    instruction_color = (0, 100, 0)
    instruction_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, text_scale - 0.2, 1)[0]
    instruction_x = top_left[0] + (box_width - instruction_size[0]) // 2
    instruction_y = text_y + round(0.2 * box_height)
    cv2.putText(img, instruction_text, (instruction_x, instruction_y), cv2.FONT_HERSHEY_SIMPLEX, text_scale - 0.2, instruction_color, 2)

    instruction_text = f"{reject_button} - REJECT"
    instruction_color = (0, 0, 100)
    instruction_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, text_scale - 0.2, 1)[0]
    instruction_x = top_left[0] + (box_width - instruction_size[0]) // 2
    instruction_y = instruction_y + round(0.2 * box_height)
    cv2.putText(img, instruction_text, (instruction_x, instruction_y), cv2.FONT_HERSHEY_SIMPLEX, text_scale - 0.2, instruction_color, 2)
