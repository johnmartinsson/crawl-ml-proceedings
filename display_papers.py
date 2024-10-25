import csv
import tkinter as tk
from tkinter import ttk
import webbrowser
import sys

# Function to open a URL in the default web browser
def open_url(url):
    webbrowser.open_new(url)

# Read the CSV file
papers = []
with open(sys.argv[1], 'r') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        papers.append({
            'title': row[4],
            'venue': row[1],
            'year': row[2],
            'similarity': row[0],
            'authors': row[5],
            'url': row[3]
        })

# Create the main window
root = tk.Tk()
root.title("Papers")

# Create a Treeview widget
columns = ('Title', 'Venue', 'Year', 'Similarity', 'Authors', 'URL')
tree = ttk.Treeview(root, columns=columns, show='headings')

# Define column headings
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_treeview(tree, _col, False))

# Insert the data into the Treeview
for paper in papers:
    tree.insert('', tk.END, values=(paper['title'], paper['venue'], paper['year'], paper['similarity'], paper['authors'], paper['url']))

# Function to handle item selection
def on_item_selected(event):
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        url = item['values'][5]
        open_url(url)

# Bind the selection event to the handler
tree.bind('<<TreeviewSelect>>', on_item_selected)

# Pack the Treeview widget
tree.pack(fill=tk.BOTH, expand=True)

# Sorting function
def sort_treeview(treeview, col, reverse):
    l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        treeview.move(k, '', index)

    treeview.heading(col, command=lambda: sort_treeview(treeview, col, not reverse))

# Run the application
root.mainloop()