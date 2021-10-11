import streamlit as st
import cv2
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Specify canvas parameters in application
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
drawing_mode = st.sidebar.selectbox(
"Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
)
realtime_update = st.sidebar.checkbox("Update in realtime", True)

def create_canvas_draw_instance(background_image, key): 

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(background_image),
        update_streamlit=realtime_update,
        drawing_mode=drawing_mode,
        width = 275, 
        height = 184,
        key=key,
    )
    return canvas_result

def main():

    canvas_r = create_canvas_draw_instance("bg_image_r.png", key="red")

    if st.button('save_image'):
        cv2.imwrite("test_image.png", canvas_r.image_data)


if __name__ == "__main__":
    main()