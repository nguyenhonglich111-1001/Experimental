document.addEventListener('DOMContentLoaded', () => {
    const noteForm = document.getElementById('note-form');
    const notesContainer = document.getElementById('notes-container');
    const formTitle = document.getElementById('form-title');
    const noteIdInput = document.getElementById('note-id');
    const noteTitleInput = document.getElementById('note-title');
    const noteContentInput = document.getElementById('note-content');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const summaryModal = new bootstrap.Modal(document.getElementById('summaryModal'));
    const summaryContent = document.getElementById('summary-content');

    const API_URL = '/api/notes';

    // Fetch and display all notes
    const getNotes = async () => {
        const response = await fetch(API_URL);
        const notes = await response.json();
        notesContainer.innerHTML = '';
        notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = 'col-md-4';
            noteElement.innerHTML = `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${note.title}</h5>
                        <p class="card-text">${note.content.substring(0, 100)}...</p>
                        <button class="btn btn-sm btn-info" onclick="handleEdit('${note.id}')">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="handleDelete('${note.id}')">Delete</button>
                        <button class="btn btn-sm btn-success" onclick="handleSummarize('${note.id}')">Summarize</button>
                    </div>
                </div>
            `;
            notesContainer.appendChild(noteElement);
        });
    };

    // Handle form submission (Create/Update)
    noteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = noteIdInput.value;
        const title = noteTitleInput.value;
        const content = noteContentInput.value;

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/${id}` : API_URL;

        await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content }),
        });

        resetForm();
        getNotes();
    });

    // Reset form to "Create" state
    const resetForm = () => {
        formTitle.textContent = 'Create a New Note';
        noteIdInput.value = '';
        noteTitleInput.value = '';
        noteContentInput.value = '';
        cancelEditBtn.classList.add('d-none');
    };

    // Handle Edit button click
    window.handleEdit = async (id) => {
        const response = await fetch(`${API_URL}`);
        const notes = await response.json();
        const note = notes.find(n => n.id === id);

        if (note) {
            formTitle.textContent = 'Edit Note';
            noteIdInput.value = note.id;
            noteTitleInput.value = note.title;
            noteContentInput.value = note.content;
            cancelEditBtn.classList.remove('d-none');
            window.scrollTo(0, 0);
        }
    };
    
    // Handle Cancel Edit button click
    cancelEditBtn.addEventListener('click', resetForm);

    // Handle Delete button click
    window.handleDelete = async (id) => {
        if (confirm('Are you sure you want to delete this note?')) {
            await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            getNotes();
        }
    };

    // Handle Summarize button click
    window.handleSummarize = async (id) => {
        const response = await fetch(`${API_URL}`);
        const notes = await response.json();
        const note = notes.find(n => n.id === id);

        if (note) {
            summaryContent.textContent = 'Summarizing...';
            summaryModal.show();
            
            const summaryResponse = await fetch(`${API_URL}/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: note.content }),
            });
            const result = await summaryResponse.json();
            summaryContent.textContent = result.summary;
        }
    };

    // Initial load
    getNotes();
});
