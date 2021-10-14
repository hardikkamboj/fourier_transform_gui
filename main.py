from typing import final
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
bg_color = st.sidebar.color_picker("Background color hex: ", "#FFFFFF")
drawing_mode = st.sidebar.selectbox(
"Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
)
realtime_update = st.sidebar.checkbox("Update in realtime", True)

def get_masked_image(image, canvas_image):
    mask = canvas_image[:,:,3]
    mask_inv = cv2.bitwise_not(mask)
    mask_inv3 = cv2.merge((mask_inv,mask_inv,mask_inv))
    return cv2.bitwise_and(image, mask_inv3)


def inverse_furiour(image):
    final_image = []
    for c in image:
        channel = abs(np.fft.ifft2(c))
#         plt.imshow(channel)
#         plt.show()
        final_image.append(channel)
    final_image_assebled = np.dstack([final_image[0].astype('int'),
                                     final_image[1].astype('int'),
                                     final_image[2].astype('int')])
    return final_image_assebled

def create_canvas_draw_instance(background_image, key, height, width): 

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0)",  
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(background_image),
        update_streamlit=realtime_update,
        drawing_mode=drawing_mode,
        height = height, 
        width = width,
        key=key,
    )

    return canvas_result

def get_mask_from_canvas(canvas_images):
    list_mask = []
    for image in canvas_images:
        list_mask.append(image[:,:,3])
        
    return list_mask

def normalize_image(img):
    img = img / np.max(img)
    return (img*255).astype('uint8')

def write_background_images(images, names): 
    for image, name in zip(images, names):
        image3 = cv2.merge((image,image,image))
        image_3_nor = normalize_image(image3)
        cv2.imwrite(name, image_3_nor)

def write_canvas_images(images, names): 
    for image, name in zip(images, names): 
        cv2.imwrite(name, image) 

def rgb_fft(image):
    f_size = 25
    fft_images=[]
    fft_images_log = []
    for i in range(3):
        rgb_fft = np.fft.fftshift(np.fft.fft2((image[:, :, i])))
        fft_images.append(rgb_fft)
        fft_images_log.append(np.log(abs(rgb_fft)))
    
    return fft_images, fft_images_log


def apply_mask(input_image, mask): 
    _, mask_thresh = cv2.threshold(mask, 120, 255, cv2.THRESH_BINARY)
    mask_bool = mask_thresh.astype('bool')
    input_image[mask_bool] = 1
    
    return input_image 


def apply_mask_all(list_images, list_mask): 
    final_result = []
    
    for (i,mask) in zip(list_images, list_mask):
        result = apply_mask(i,mask)
        final_result.append(result)
    return final_result

def main():

    st.header("Fourier Transformation - ")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpeg","png","jpg"])

    if uploaded_file is not None: 
        
        original = Image.open(uploaded_file)
        img = np.array(original)
        st.image(img, use_column_width=True)
    
        fft_images, fft_images_log = rgb_fft(img)

        for temp in fft_images_log:
            st.text(temp.shape)

        names = ["bg_image_r.png", "bg_image_g.png", "bg_image_b.png"]

        write_background_images(fft_images_log, names)

        st.text("Red Channel in frequency domain - ")
        canvas_r = create_canvas_draw_instance(names[0], key="red", height=img.shape[0], width=img.shape[1])
        st.text("Green Channel in frequency domain - ")
        canvas_g = create_canvas_draw_instance(names[1], key="green",height=img.shape[0], width=img.shape[1])
        st.text("Blue channel in frequency domain - ")
        canvas_b = create_canvas_draw_instance(names[2], key="blue", height=img.shape[0], width=img.shape[1])
        
        # st.text(type(canvas_r.image_data))
        # st.text(img.shape)
        # st.text(canvas_r.image_data.shape)
        # st.text(transformed_frequencies_3dim[0].shape)


        if st.button('Get Result: - '):
            
            canvas_image_data = [canvas_r.image_data, canvas_g.image_data, canvas_b.image_data]
            
            names_canvas_images = ["canvas_image_r.png","canvas_image_g.png","canvas_image_b.png"]
            write_canvas_images(canvas_image_data, names_canvas_images)

            # appending the images which are saved earlier
            canvas_images = []

            for name in names_canvas_images: 
                canvas_images.append(cv2.imread(name,-1))

            list_mask = get_mask_from_canvas(canvas_images)

            # reading canvas images 
            result = apply_mask_all(fft_images, list_mask)

            transformed = inverse_furiour(result)

            # result_clipped = np.clip(result, 0 ,255)

            # result_formatted = np.dstack([result_clipped[0],
            #                             result_clipped[1],
            #                             result_clipped[2]])

            transformed_clipped = np.clip(transformed, 0, 255)
            st.text("Image Returned by Inverse Fourier Transform - ")
            st.image(transformed_clipped, use_column_width=True)



if __name__ == "__main__":
     main()