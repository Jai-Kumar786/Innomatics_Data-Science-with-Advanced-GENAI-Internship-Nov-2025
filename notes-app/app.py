from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app with templates folder specification
app = Flask(__name__, template_folder='templates')

# In-memory list to store notes (resets on app restart)
notes = []

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route handler for both GET and POST requests.
    
    GET: Displays the home page with existing notes
    POST: Processes form submission, adds new note, and redirects
    """
    if request.method == 'POST':
        # Retrieve note from form data using request.form (not request.args)
        note = request.form.get('note', '').strip()
        
        # Validation: Only append if note is not empty
        if note:
            notes.append(note)
        
        # Redirect to prevent form resubmission on page refresh
        return redirect(url_for('index'))
    
    # GET request: Display the form and existing notes
    return render_template('home.html', notes=notes)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_note(index):
    """
    Delete a note by its index.
    
    Args:
        index: The position of the note to delete
    """
    try:
        if 0 <= index < len(notes):
            notes.pop(index)
    except (ValueError, IndexError):
        pass
    
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_notes():
    """Clear all notes from the list."""
    notes.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)