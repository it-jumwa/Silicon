/**
 * @const {HTMLElement} Reference to the create task popup form
 * */
const taskFormContainer = document.getElementById('create-task-popup');

/**
 * This function is used to make the form visible for task creation
 *
 * Opens the task form by displaying the form container and disables the create
 * task button
 */
function openForm() {
  // Show the task form container
  taskFormContainer.style.display = 'block';
}

/**
 * This function is used to hide the task creation form
 *
 * Closes the task form by hiding the form container and re-enables the create
 * task button
 */
function closeForm() {
  // Hide the task form container
  taskFormContainer.style.display = 'none';
}
