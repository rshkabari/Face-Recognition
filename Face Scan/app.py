import cv2
import shelve
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import face_recognition

# Initialize the video capture object
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("The camera could not be opened.")

def save_to_database(name, encoding):
    # Open the database file
    with shelve.open('registered_faces.db') as db:
        # Save the encoding under the provided name
        db[name] = encoding

def load_from_database():
    # Open the database file
    with shelve.open('registered_faces.db') as db:
        # Return a dictionary of all registered faces
        return dict(db)

def register_face():
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture video frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
        cv2.imshow('Registering Face', frame)
        
        if face_encodings:
            cv2.destroyAllWindows()
            name = simpledialog.askstring("Register Face", "Enter your name:")
            if name:
                save_to_database(name, face_encodings[0])
                messagebox.showinfo("Success", "Face registered successfully!")
                break
            else:
                messagebox.showerror("Error", "No name entered, registration cancelled.")
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def recognize_face():
    known_faces = load_from_database()
    known_face_encodings = list(known_faces.values())
    known_face_names = list(known_faces.keys())

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture video frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        cv2.imshow('Recognizing Face', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def on_exit_button():
    # Release the video capture before closing the GUI
    cap.release()
    # Destroy the root window to properly close the application
    root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_exit_button)

# Main GUI
root = tk.Tk()
root.title("Facial Recognition Software")

# Load background image
background_image = Image.open("background.png")  # Make sure to use the path to your dark face silhouette image
background_photo = ImageTk.PhotoImage(background_image)

# Update the window size based on the image size
root.geometry(f"{background_image.width}x{background_image.height}")

# Create a Canvas that fills the window and has no border
canvas = tk.Canvas(root, width=background_image.width, height=background_image.height, bd=0, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Set the background image on the Canvas
canvas.create_image(0, 0, image=background_photo, anchor=tk.NW)

# Center the window on the screen
window_width = background_image.width
window_height = background_image.height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Display the "Welcome" text on the Canvas
canvas.create_text(window_width/2.05, window_height*0.375, text="Welcome", fill="white", font=("Times New Roman", 50, "bold"))

# Button styling
button_bg_color = "#333333"  # Darker background for the button
button_fg_color = "white"
button_font = ("Times New Roman", 14, "bold")

# Button dimensions
button_width = 150  # Define the width of the button
button_height = 30  # Define the height of the button

# Adjust button positions
button_y_position = background_image.height - button_height - 575  
button_x_position = background_image.width - button_width - 445

# Register button
register_button = tk.Button(root, text="Register Face", command=register_face, bg=button_bg_color, fg=button_fg_color, font=button_font, relief=tk.FLAT)
register_button.place(x=button_x_position, y=button_y_position + 2*(button_height + 10), width=button_width, height=button_height)

# Recognize button
recognize_button = tk.Button(root, text="Recognize Face", command=recognize_face, bg=button_bg_color, fg=button_fg_color, font=button_font, relief=tk.FLAT)
recognize_button.place(x=button_x_position, y=button_y_position + 3*(button_height + 10), width=button_width, height=button_height)

# Exit button
exit_button = tk.Button(root, text="Exit", command=on_exit_button, bg=button_bg_color, fg=button_fg_color, font=button_font, relief=tk.FLAT)
exit_button.place(x=button_x_position, y=button_y_position + 4*(button_height + 10), width=button_width, height=button_height)

root.mainloop()
