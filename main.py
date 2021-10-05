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

    canvas_result_r = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(background_image),
        update_streamlit=realtime_update,
        drawing_mode=drawing_mode,
        key=key,
    )

def normalize_image(img):
    img = img / np.max(img)
    return (img*255).astype('uint')

def main():

    st.header("Thresholding, Edge Detection and Contours")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpeg","png","jpg"])

    if uploaded_file is not None: 
        
        original = Image.open(uploaded_file)
        img = np.array(original)
        st.image(img, use_column_width=True)
    
        fft_images=[]

        for i in range(3):
            rgb_fft = np.fft.fftshift(np.fft.fft2((img[:, :, i])))
            # print(type(rgb_fft))
            fft_images.append(normalize_image(np.log(abs(rgb_fft)).astype(int)))

        

        cv2.imwrite("bg_image_r.png", cv2.merge((fft_images[0],fft_images[0],fft_images[0])))
        cv2.imwrite("bg_image_g.png", cv2.merge((fft_images[1],fft_images[1],fft_images[1])))
        cv2.imwrite("bg_image_b.png", cv2.merge((fft_images[2],fft_images[2],fft_images[2])))

        canvas_r = create_canvas_draw_instance("bg_image_r.png", key="red")
        canvas_g = create_canvas_draw_instance("bg_image_g.png", key="green")
        canvas_b = create_canvas_draw_instance("bg_image_b.png", key="blue")

if __name__ == "__main__":
     main()