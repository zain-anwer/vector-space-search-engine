import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import sys
import subprocess
from pathlib import Path

# Import your working search module
from vector_search import vector_search

class SearchEngineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trump Speeches - Vector Search Engine")
        self.root.geometry("600x500")
        self.root.configure(padx=20, pady=20)

        # Style configurations
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TLabel", font=("Helvetica", 10))

        self.create_widgets()

    def create_widgets(self):
        # --- Search Bar Area ---
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_entry = ttk.Entry(search_frame, font=("Helvetica", 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        # Bind the Enter key to the search function
        self.search_entry.bind('<Return>', lambda event: self.perform_search())

        search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.pack(side=tk.RIGHT)

        # --- Time & Status Label ---
        self.status_label = ttk.Label(self.root, text="Enter a query to begin searching.", foreground="gray")
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        # --- Results Area (Text Widget for clickable links) ---
        self.results_text = tk.Text(self.root, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED, cursor="arrow")
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Configure the link tag style (blue and underlined)
        self.results_text.tag_config("hyperlink", foreground="blue", underline=True)
        self.results_text.tag_bind("hyperlink", "<Enter>", lambda e: self.results_text.config(cursor="hand2"))
        self.results_text.tag_bind("hyperlink", "<Leave>", lambda e: self.results_text.config(cursor="arrow"))

    def perform_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return

        # Clear previous results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.status_label.config(text="Searching...", foreground="black")
        self.root.update() # Force UI update

        # --- Time the Search Execution ---
        start_time = time.time()
        
        try:
            # Your vector_search function returns a list of tuples: [(doc_id, score), ...]
            results = vector_search(query)
        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Search failed.")
            self.results_text.config(state=tk.DISABLED)
            return

        end_time = time.time()
        elapsed_time = end_time - start_time

        # --- Display Results ---
        if not results:
            self.status_label.config(text=f"No results found. (Time: {elapsed_time:.4f} seconds)")
        else:
            self.status_label.config(text=f"Found {len(results)} results in {elapsed_time:.4f} seconds.", foreground="green")

            for doc_id, score in results:
                file_name = f"speech_{doc_id}.txt"
                display_text = f"📄 {file_name} (Score: {score:.4f})\n"
                
                # Insert text
                self.results_text.insert(tk.END, display_text)
                
                # Apply the hyperlink tag to just the filename part
                # Format: line.start_char to line.end_char
                current_index = self.results_text.index(tk.INSERT)
                line_num = int(float(current_index)) - 1
                
                start_idx = f"{line_num}.2" # Skip the emoji and space
                end_idx = f"{line_num}.{2 + len(file_name)}"
                
                # Create a unique tag for this specific document
                unique_tag = f"link_{doc_id}"
                self.results_text.tag_add("hyperlink", start_idx, end_idx)
                self.results_text.tag_add(unique_tag, start_idx, end_idx)
                
                # Bind the click event to open this specific file
                self.results_text.tag_bind(unique_tag, "<Button-1>", lambda e, d_id=doc_id: self.open_document(d_id))
                
                # Add spacing between results
                self.results_text.insert(tk.END, "\n")

        self.results_text.config(state=tk.DISABLED)

    def open_document(self, doc_id):
        # Construct the file path
        file_path = Path('data') / 'trump_speeches' / f"speech_{doc_id}.txt"
        
        if not file_path.exists():
            messagebox.showerror("File Not Found", f"Could not find the file:\n{file_path.absolute()}")
            return

        # Cross-platform file opening
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin": # macOS
                subprocess.call(["open", str(file_path)])
            else: # Linux variants
                subprocess.call(["xdg-open", str(file_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()