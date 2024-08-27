import tkinter as tk
from tkinter import filedialog
import imageio
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip
import threading
import pathlib
import os


####################################
#### Video Conversion Functions ####
####################################

selected_mov_file = ""

# Select video file and show preview
def select_mov_file():
    global selected_mov_file
    selected_mov_file = filedialog.askopenfilename(
        title="Select .mov or .mp4 file",
        filetypes=(("Video files", "*.mov *.mp4"), ("All files", "*.*"))
    )
    if selected_mov_file:
        preview_image = generate_video_preview(selected_mov_file)
        display_preview(preview_image)

# Generate video preview (image) from video file
def generate_video_preview(video_file):
    video = VideoFileClip(video_file)
    preview_frame = video.get_frame(0)
    preview_image = Image.fromarray(preview_frame)
    preview_image = preview_image.resize((320, 180))
    return preview_image

# Show preview (image) in GUI
def display_preview(image):
    photo = ImageTk.PhotoImage(image)
    preview_label.configure(image=photo)
    preview_label.image = photo

# Update text labels (status and size estimate)
def update_status_label(text):
    status_label.configure(text=text)
    if text == 'Processing... This may take a while.':
        status_label.configure(fg='salmon')
    elif text == 'Conversion Complete':
        status_label.configure(fg='green')
    else:
        status_label.configure(fg='red')
def update_size_label(text):
    size_label.configure(text=text)

# Calculate the estimated file size based on frame rate, desired width, desired height, and video duration
def estimate_file_size(frame_rate, desired_width, desired_height, video):
    total_frames = int(video.duration * frame_rate)
    compression_factor = 0.164162  # Adjust this value as needed for the desired compression level
    estimated_file_size = (total_frames * desired_width * desired_height * 3 * compression_factor) / (1024 * 1024)
    return estimated_file_size

# Update estimated file size in GUI
def estimate_file_size_and_update(event=None):
    global selected_mov_file
    frame_rate_text = fps_entry.get()
    desired_width_text = width_entry.get()

    # Calculate only if parameters are there
    if not selected_mov_file or not desired_width_text or frame_rate_text == '10 (Recommended)':
        update_size_label("Estimated Size: N/A")
        return

    # Check if valid numbers are entered
    try:
        fps = float(frame_rate_text)
        width = int(desired_width_text)
    except ValueError:
        return
        
    if frame_rate_text and desired_width_text:
        frame_rate = float(frame_rate_text)
        desired_width = int(desired_width_text)
        video = VideoFileClip(selected_mov_file)

        # Calculate the proportional height based on the aspect ratio of the video
        aspect_ratio = video.size[0] / video.size[1]
        desired_height = int(desired_width / aspect_ratio)

        # Estimate the file size
        estimated_size = estimate_file_size(frame_rate, desired_width, desired_height, video)
        size_label_text = f"Estimated Size: {estimated_size:.2f} MB"
        update_size_label(size_label_text)
    else:
        update_size_label("Estimated Size: N/A")

# Convert video to gif
def convert_mov_to_gif():
    global selected_mov_file
    global output_file

    # Check if selected MOV file is missing
    if not selected_mov_file:
        update_status_label("Missing File. Please select a video file.")
        return

    # Get the values from the input fields
    fps = fps_entry.get()
    desired_width = width_entry.get()

    # Check if any other parameter is missing
    if not fps or not desired_width:
        update_status_label("Please enter all the required values.")
        return

    # Check if valid numbers are entered
    try:
        fps = float(fps)
        width = int(desired_width)
    except ValueError:
        update_status_label("Invalid Values. Please enter valid numbers for FPS and Width.")
        return

    # Run the conversion
    if selected_mov_file:
        output_file = filedialog.asksaveasfilename(title="Save as .gif",
                                                   defaultextension=".gif",
                                                   filetypes=(("GIF files", "*.gif"), ("All files", "*.*")))
        if output_file:
            # Start the conversion process in a separate thread
            conversion_thread = threading.Thread(target=perform_conversion, args=(selected_mov_file, output_file), daemon=True)
            conversion_thread.start()
            update_status_label("Processing... This may take a while.")

# Performing conversion process
def perform_conversion(input_file, output_file):
    video = VideoFileClip(input_file)

    # Frame rate from user input
    frame_rate = float(fps_entry.get())

    # Calculate the frame interval based on actual frame rate of the video - video.fps
    frame_interval = float(video.fps / frame_rate)   

    # Get the desired width from user input
    desired_width = int(width_entry.get())

    # Calculate the proportional height based on the aspect ratio of the video
    aspect_ratio = video.size[0] / video.size[1]
    desired_height = int(desired_width / aspect_ratio)

    # Initialize a list to store the frames
    frames = []

    # Extract frames at the specified frame interval
    for i, frame in enumerate(video.iter_frames()):
        rounded_interval = int(i % frame_interval)
        if rounded_interval == 0:
            frame_image = Image.fromarray(frame)
            resized_frame = frame_image.resize((desired_width, desired_height))
            frames.append(resized_frame)

    # Calculate the duration per frame in milliseconds
    frame_duration = int(1000 / frame_rate)

    # Save frames as a GIF using imageio
    imageio.mimsave(output_file, frames, duration=frame_duration, loop=0)

    # Update status label
    update_status_label("Conversion Complete")
    convert_button.configure(state=tk.NORMAL)

    # Show and enable the "Open Directory" button
    open_directory_button.config(state=tk.NORMAL)
    open_directory_button.pack(pady=40)

# Open output directory
def open_output_directory():
    output_directory = os.path.dirname(output_file)
    os.startfile(output_directory)

# Button hover
def on_enter(event, button):
    button.config(bg='#555')  # Change the background color when the mouse enters

def on_leave(event, button):
    button.config(bg='#333')  # Change the background color back when the mouse leaves

# Text placeholder in FPS textarea
def on_entry_click(event):
    if fps_entry.get() == '10 (Recommended)':
        fps_entry.delete(0, tk.END)  # Remove the placeholder text
        fps_entry.config(fg='black')  # Change the text color to black

def on_entry_leave(event):
    if fps_entry.get() == '':
        fps_entry.insert(0, '10 (Recommended)')  # Insert the placeholder text
        fps_entry.config(fg='#BBB')  # Change the text color to gray





#########################
###### GUI Styles #######
#########################

window = tk.Tk()
window.title("Video to GIF Converter")

# Define a custom font
custom_font = ("Corbel", 12)

# Change background color to gray (#222)
window.configure(bg="#222")

# Apply custom font to all components
window.option_add("*Font", custom_font)

window_width = 700  # Specify the desired width of the window
window_height = 700  # Specify the desired height of the window

# Calculate the screen dimensions to center the window
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set the window size and position
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Add padding at the top
top_padding = tk.Frame(window, height=60, bg="#222")
top_padding.pack()



############################
###### GUI Components ######
############################

# Select video button
select_button = tk.Button(
    window, 
    text="Select video (.mov, .mp4)", 
    command=select_mov_file,
    relief="flat",
    bg="#333",
    fg="#DDD",
    activebackground="#333",
    activeforeground="#DDD",
)
select_button.pack()
select_button.bind("<Enter>", lambda event: on_enter(event, select_button))  # Bind the mouse enter event to the function
select_button.bind("<Leave>", lambda event: on_leave(event, select_button))  # Bind the mouse leave event to the function

# Video preview image
preview_label = tk.Label(window, bg="#222", fg="#666")
preview_label.pack(pady=10)

# Frame Rate label
fps_label = tk.Label(window, text="Frame Rate (fps):", bg="#222", fg="#666")
fps_label.pack()

# Frame Rate textarea
placeholder_text = '10 (Recommended)'
fps_entry = tk.Entry(window, fg='#BBB', justify='center')
fps_entry.insert(0, placeholder_text)
fps_entry.pack()
fps_entry.bind("<KeyRelease>", estimate_file_size_and_update)
fps_entry.bind('<FocusIn>', on_entry_click)
fps_entry.bind('<FocusOut>', on_entry_leave)

# Width label
width_label = tk.Label(window, text="Desired Width:", bg="#222", fg="#666")
width_label.pack()

# Width textarea
width_entry = tk.Entry(window, justify='center')
width_entry.pack()
width_entry.bind("<KeyRelease>", estimate_file_size_and_update)

# Convert to gif button
convert_button = tk.Button(
    window, 
    text="CONVERT to .GIF", 
    command=convert_mov_to_gif,
    relief="flat",
    bg="#333",
    fg="#DDD",
    activebackground="#333",
    activeforeground="#DDD",    
)
convert_button.pack(pady=10)
convert_button.bind("<Enter>", lambda event: on_enter(event, convert_button))  # Bind the mouse enter event to the function
convert_button.bind("<Leave>", lambda event: on_leave(event, convert_button))  # Bind the mouse leave event to the function

# Status of conversion label
status_label = tk.Label(window, text="", fg="red", bg="#222")
status_label.pack()

# Size estimate label
size_label = tk.Label(window, text="", bg="#222", fg="#666")
size_label.pack()

# Open directory button
open_directory_button = tk.Button(
    window, 
    text="Open saved file location", 
    command=open_output_directory,
    state=tk.DISABLED,
    relief="flat",
    bg="#333",
    fg="#DDD",
    activebackground="#333",
    activeforeground="#DDD",   
)
open_directory_button.pack_forget()
open_directory_button.bind("<Enter>", lambda event: on_enter(event, open_directory_button))  # Bind the mouse enter event to the function
open_directory_button.bind("<Leave>", lambda event: on_leave(event, open_directory_button))  # Bind the mouse leave event to the function

window.mainloop()
