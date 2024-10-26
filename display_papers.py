import csv
import tkinter as tk
from tkinter import ttk
import webbrowser
import sys
import sqlite3
import json

from paper import Paper

# Function to open a URL in the default web browser
def open_url(url):
    webbrowser.open_new(url)

# Function to handle item selection on double-click
def on_item_double_clicked(event, tree):
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        url = item['values'][6]
        open_url(url)

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

# Function to copy BibTeX to clipboard
def copy_bibtex(tree, bibtex_dict):
    bibtex_entries = []
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        title = item['values'][0]
        bibtex = bibtex_dict.get(title, "")
        bibtex_entries.append(bibtex)
    all_bibtex = "\n\n".join(bibtex_entries)
    root.clipboard_clear()
    root.clipboard_append(all_bibtex)
    root.update()  # now it stays on the clipboard after the window is closed

# Function to open and display the abstracts in new windows
def open_abstract(tree, abstract_dict):
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        title = item['values'][0]
        abstract = abstract_dict.get(title, "")
        
        # Create a new window
        abstract_window = tk.Toplevel(root)
        abstract_window.title(f"Abstract - {title}")
        
        # Create a Text widget to display the abstract
        text_widget = tk.Text(abstract_window, wrap=tk.WORD)
        text_widget.insert(tk.END, abstract)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
        text_widget.pack(fill=tk.BOTH, expand=True)

# Read the data from the SQLite database
def read_data_from_db(db_path):
    papers = []
    bibtex_dict = {}
    abstract_dict = {}
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM papers")
    data = c.fetchall()
    conn.close()

    for d in data:
        similarities = json.loads(d[9])
        paper = {
            'title': d[0],
            'authors': d[1],
            'venue': d[2],
            'year': d[3],
            'bibtex': d[4],
            'url': d[5],
            'abstract': d[6],
            'accepted': d[8],
            'similarity': similarities[0][1] if similarities else 0,
        }
        papers.append(paper)
        bibtex_dict[d[0]] = d[4]  # Store the BibTeX entry in the dictionary
        abstract_dict[d[0]] = d[6]  # Store the abstract in the dictionary
    return papers, bibtex_dict, abstract_dict

# Main function to create the GUI
def main(db_path):
    global root
    papers, bibtex_dict, abstract_dict = read_data_from_db(db_path)

    # Create the main window
    root = tk.Tk()
    root.title("Papers")

    # Create a Treeview widget
    columns = ('Title', 'Venue', 'Accepted', 'Year', 'Similarity', 'Authors', 'URL')
    tree = ttk.Treeview(root, columns=columns, show='headings')

    # Define column headings
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_treeview(tree, _col, False))

    # Insert the data into the Treeview
    for paper in papers:
        tree.insert('', tk.END, values=(paper['title'], paper['venue'], paper['accepted'], paper['year'], '{:.3f}'.format(paper['similarity']), paper['authors'], paper['url']))

    # Adjust column widths
    def adjust_column_widths(tree):
        for col in columns:
            max_width = max(len(col), 10)  # Set a minimum width
            for item in tree.get_children():
                text = str(tree.item(item, 'values')[columns.index(col)])
                if col not in ['URL', 'Authors']:
                    max_width = max(max_width, len(text))
            #if col == 'Title':
            #    max_width = min(max_width, 50)  # Set a reasonable maximum width for the title column
            tree.column(col, width=max_width * 8)  # Adjust the multiplier as needed

    adjust_column_widths(tree)

    # Create a context menu
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Copy BibTeX", command=lambda: copy_bibtex(tree, bibtex_dict))
    context_menu.add_command(label="Open Abstract", command=lambda: open_abstract(tree, abstract_dict))

    # Function to show the context menu
    def show_context_menu(event):
        # Select the row under the cursor if it is not already selected
        row_id = tree.identify_row(event.y)
        if row_id not in tree.selection():
            tree.selection_set(row_id)
        context_menu.post(event.x_root, event.y_root)

    # Bind the left-click event to hide the context menu
    tree.bind('<Button-1>', lambda event: context_menu.unpost())

    # Bind the right-click event to show the context menu
    tree.bind('<Button-3>', show_context_menu)

    # Bind the double-click event to the handler
    tree.bind('<Double-1>', lambda event: on_item_double_clicked(event, tree))

    # Pack the Treeview widget
    tree.pack(fill=tk.BOTH, expand=True)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python display_papers.py <database_path>")
        sys.exit(1)
    db_path = sys.argv[1]
    main(db_path)