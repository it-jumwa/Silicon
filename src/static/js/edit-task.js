/**
 * Handle the Edit button click event.
 * Fetches the task data from the server and opens the edit form.
 *
 * @param {number} taskId - The ID of the task to edit.
 */
function handleEditButton(taskId) {
  fetch(`/get_task/${taskId}`)
  .then((response) => {
    if (!response.ok) throw new Error('Task not found');
    return response.json();
  })
  .then(openEditForm)
  .catch((error) => alert(`Error: ${error.message}`));
}

/**
 * Open the edit form and pre-fill it with the task's current data.
 *
 * @param {Object} task - The task data to fill in the edit form.
 */
function openEditForm(task) {
  const editPopup = document.getElementById('edit-task-popup');
  if (!editPopup) {
    alert('Edit popup element not found!');
    return;
  }

  editPopup.style.display = 'block';

  // Pre-fill the form fields
  const formFields = {
    'edit-title': task.title,
    'edit-description': task.description,
    'edit-story-point': task.story_point,
    'edit-priority-tag': task.priority_tag,
    'edit-progress-tag': task.progress_tag,
  };

  // Pre-fill the form fields (check for field existence to prevent errors)
  Object.entries(formFields).forEach(([key, value]) => {
    const input = document.getElementById(key);
    if (input) {
      input.value = value;
    } else {
      console.warn(`Field with ID "${key}" not found.`);
    }
  });

  // Set the development tag checkboxes based on the bit vector
  const bitVector = parseInt(task.development_bit_vector, 10);
  document.querySelectorAll('input[name="edit-development-tags"]').forEach((checkbox) => {
    const tagValue = parseInt(checkbox.value, 10);
    checkbox.checked = (bitVector & tagValue) === tagValue;
  });

  // Handle progress stage visibility if task is in progress
  const progressTag = document.getElementById('edit-progress-tag');
  const inProgressTag = document.getElementById('edit-in-progress-tag');
  if (task.progress_tag === 'in-progress') {
    inProgressTag.style.visibility = 'visible';
    inProgressTag.value = task.in_progress_stage || 'planning'; // Default to 'planning'
  } else {
    inProgressTag.style.visibility = 'hidden';
    inProgressTag.value = ''; // Clear value when not needed
  }
}

/**
 * Handle the edit form submission event.
 * Collects form data and sends it to the server to update the task.
 */
document.getElementById('edit-task-form')?.addEventListener('submit', (event) => {
  event.preventDefault();

  // Collect form data
  const updatedTask = {
    title: document.getElementById('edit-title').value,
    description: document.getElementById('edit-description').value,
    story_point: document.getElementById('edit-story-point').value,
    priority_tag: document.getElementById('edit-priority-tag').value,
    progress_tag: document.getElementById('edit-progress-tag').value,
    in_progress_stage: document.getElementById('edit-in-progress-tag').value,
    development_bit_vector: getDevelopmentBitVector(),
  };

  // Send the updated data to the server
  fetch(`/update_task/${taskId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updatedTask),
  })
  .then((response) => {
    if (!response.ok) throw new Error('Failed to update task');
    closeEditForm();
    alert('Task updated successfully!');
  })
  .catch((error) => alert(`Error: ${error.message}`));
});

/**
 * Get the development tag bit vector based on selected checkboxes.
 *
 * @returns {number} - The calculated bit vector.
 */
function getDevelopmentBitVector() {
  let bitVector = 0;
  document.querySelectorAll('input[name="edit-development-tags"]:checked').forEach((checkbox) => {
    bitVector |= parseInt(checkbox.value, 10);
  });
  return bitVector;
}

/**
 * Close the edit form and reset the form fields.
 */
function closeEditForm() {
  const editPopup = document.getElementById('edit-task-popup');
  if (editPopup) editPopup.style.display = 'none';
  document.getElementById('edit-task-form')?.reset();

  // Hide the progress stage dropdown if it was visible
  const inProgressTag = document.getElementById('edit-in-progress-tag');
  if (inProgressTag) {
    inProgressTag.style.visibility = 'hidden';
    inProgressTag.value = ''; // Reset its value
  }
}
