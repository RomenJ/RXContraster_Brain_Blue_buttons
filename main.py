import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pydicom
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt  # Importamos pyplot de matplotlib

class RXContrasterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RX Contraster")
        self.configure(bg="lightblue")

        # Title label
        self.title_label = tk.Label(self, text="XRay Contraster", font=("Helvetica", 20), bg="lightblue")
        self.title_label.pack(pady=10)

        # Frame for image and controls
        self.frame = tk.Frame(self, bg="lightblue")
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Original Image
        self.original_image_canvas = tk.Canvas(self.frame, width=300, height=300, bg="white")
        self.original_image_canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Contrast Image
        self.contrast_image_canvas = tk.Canvas(self.frame, width=375, height=375, bg="white")
        self.contrast_image_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # Sliders
        self.slider_frame = tk.Frame(self.frame, bg="lightblue")
        self.slider_frame.grid(row=1, column=1, pady=10, sticky="nw")

        self.high_contrast_slider = ttk.Scale(self.slider_frame, from_=0, to=255, orient="horizontal", command=self.update_contrast_image)
        self.high_contrast_slider.set(200)
        self.high_contrast_slider.pack(pady=5)

        self.low_contrast_slider = ttk.Scale(self.slider_frame, from_=0, to=255, orient="horizontal", command=self.update_contrast_image)
        self.low_contrast_slider.set(-200)
        self.low_contrast_slider.pack(pady=5)

        # Buttons
        self.button_frame = tk.Frame(self.frame, bg="lightblue")
        self.button_frame.grid(row=2, column=1, pady=10, sticky="nw")

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.brian_button = tk.Button(self.button_frame, text="Brain TAG/RX image", command=self.generate_image)
        self.brian_button.pack(side=tk.LEFT, padx=5)

        self.blue_button = tk.Button(self.button_frame, text="Blue Contrast", command=self.generate_imageBlue)
        self.blue_button.pack(side=tk.LEFT, padx=5)

        # Plot area
        self.plot_frame = tk.Frame(self.frame, bg="lightblue")
        self.plot_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="ns")

        self.original_image = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("DICOM files", "*.dcm")])
        if file_path:
            try:
                self.original_image = read_dicom_file(file_path)
                self.display_image(self.original_image, self.original_image_canvas, scale=1)
                self.update_contrast_image()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load DICOM file:\n{str(e)}")

    def save_image(self):
        if self.original_image is not None:
            try:
                messagebox.showinfo("Saved", "Use a snapshot, or contact the author, if you want to save the image: rmartin4all@gmail.com")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
        else:
            messagebox.showerror("Error", "No image loaded.")

    def generate_image(self):
        if self.original_image is not None:
            try:
                print("****VISUALIZACIÓN DEL CONTENIDO")
                plt.imshow(self.original_image, cmap='gray', vmin=-200, vmax=200)
                plt.savefig("Contraste====.jpg")
                plt.show()
                plt.axis('off')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate image:\n{str(e)}")
        else:
            messagebox.showerror("Error", "No image loaded.")

    def generate_imageBlue(self):
        if self.original_image is not None:
            try:
                print("****VISUALIZACIÓN DEL CONTENIDO AZUL")
                high_contrast = self.high_contrast_slider.get()
                low_contrast = self.low_contrast_slider.get()

                contrast_image = np.clip(self.original_image, low_contrast, high_contrast)
                contrast_image_blue = np.zeros_like(contrast_image, dtype=np.float)
                contrast_image_blue[contrast_image >= high_contrast] = 1.0  # Marcamos áreas de alto contraste como azul

                plt.imshow(contrast_image_blue, cmap='Blues')
                plt.axis('off')
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate blue contrast image:\n{str(e)}")
        else:
            messagebox.showerror("Error", "No image loaded.")

    def display_image(self, image, canvas, scale=1):
        aspect_ratio = image.shape[1] / image.shape[0]
        new_width = int(300 * scale)
        new_height = int(new_width / aspect_ratio)
        resized_image = np.array(Image.fromarray(image).resize((new_width, new_height)))
        image_tk = ImageTk.PhotoImage(image=Image.fromarray(resized_image))

        canvas.image_tk = image_tk  # Prevent garbage collection
        canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        canvas.config(width=new_width, height=new_height)

    def update_contrast_image(self, *args):
        if self.original_image is not None:
            high_contrast = self.high_contrast_slider.get()
            low_contrast = self.low_contrast_slider.get()

            contrast_image = np.clip(self.original_image, low_contrast, high_contrast)
            self.display_image(contrast_image, self.contrast_image_canvas, scale=1.25)
            self.plot_histogram(contrast_image)

    def plot_histogram(self, image):
        hist = calculate_histogram(image)
        cdf = calculate_cdf(hist)

        fig = Figure(figsize=(3.375, 4.5))  # Reduced size by 25%
        ax1 = fig.add_subplot(211)
        ax1.plot(hist, label='Histogram')
        ax1.legend()
        ax1.set_ylabel("Number of pixels")

        ax2 = fig.add_subplot(212)
        ax2.plot(cdf, label='CDF', color='orange')
        ax2.legend()
        ax2.set_xlabel('Pixel value')

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def read_dicom_file(file_path):
    try:
        dicom_file = pydicom.dcmread(file_path)
        im = dicom_file.pixel_array
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except Exception as e:
        raise ValueError(f"Could not read DICOM file: {e}")
    return im

def calculate_histogram(image):
    hist, bin_edges = np.histogram(image.flatten(), bins=256, range=(0, 255))
    return hist

def calculate_cdf(hist):
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf[-1]  # Normalize to get the CDF in range [0, 1]
    return cdf_normalized

if __name__ == "__main__":
    app = RXContrasterApp()
    app.mainloop()
