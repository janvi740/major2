import tkinter as tk
from tkinter import filedialog
import requests

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Upload and Search")

        self.file_paths = []

        self.create_widgets()

    def create_widgets(self):
        # File upload section
        upload_frame = tk.Frame(self, pady=10)
        upload_frame.pack()

        tk.Label(upload_frame, text="Select Files to Upload:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(10, 5))
        self.file_listbox = tk.Listbox(upload_frame, selectmode=tk.MULTIPLE, width=50, height=5, font=("Arial", 10))
        self.file_listbox.pack(side=tk.LEFT, padx=(0, 10))

        upload_button = tk.Button(upload_frame, text="Upload", command=self.upload_files, font=("Arial", 10))
        upload_button.pack(side=tk.LEFT)

        add_button = tk.Button(upload_frame, text="Add Files", command=self.add_files, font=("Arial", 10))
        add_button.pack(side=tk.LEFT, padx=(10, 0))

        # Search section
        search_frame = tk.Frame(self, pady=10)
        search_frame.pack()

        tk.Label(search_frame, text="Search Keyword:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(10, 5))
        self.search_entry = tk.Entry(search_frame, width=50, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        search_button = tk.Button(search_frame, text="Search", command=self.search_files, font=("Arial", 10))
        search_button.pack(side=tk.LEFT)

        # Result section
        result_frame = tk.Frame(self, pady=10)
        result_frame.pack()

        self.result_text = tk.Text(result_frame, height=10, width=60, font=("Arial", 10))
        self.result_text.pack()

    def add_files(self):
        file_paths = filedialog.askopenfilenames()
        for file_path in file_paths:
            self.file_paths.append(file_path)
            self.file_listbox.insert(tk.END, file_path)

    def upload_files(self):
        if not self.file_paths:
            return

        for file_path in self.file_paths:
            print("Uploading file:", file_path)
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post('http://localhost:5000/upload', files=files)
                if response.status_code == 200:
                    print(f"File {file_path} uploaded successfully")
                else:
                    print(f"Error uploading file {file_path}")

        self.file_listbox.delete(0, tk.END)
        self.file_paths.clear()

    def search_files(self):
        keyword = self.search_entry.get()
        if not keyword:
            return

        response = requests.get(f'http://localhost:5000/search?keyword={keyword}')
        if response.status_code == 200:
            files = response.json()
            result_text = ''
            for file in files:
                result_text += f"Filename: {file['Filename']}, FileID: {file['FileID']}\n"  # Updated line
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
        elif response.status_code == 404:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No files found for the provided keyword")
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Error searching files. Please try again.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
