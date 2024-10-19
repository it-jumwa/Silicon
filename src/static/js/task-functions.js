/**
 * @fileoverview Task management script that handles adding, deleting, and
 * fetching tasks from a server, as well as updating the product backlog
 */

/**
 * @const {Element} taskForm - Reference to the task form element.
 * @const {Element} listView - Reference to the product backlog container
 * @const {string[]} DEVELOPMENT_TAGS - The available development tags
 */
const taskForm = document.getElementById('task-form');
const listView = document.getElementById('list-view');
const cardView = document.getElementById('card-view');
const availableTags = ['front-end', 'back-end', 'ui-ux', 'api', 'testing'];

/**
 * Loads tasks from the server when the DOM is fully loaded.
 * @listens {DOMContentLoaded}
 */
document.addEventListener('DOMContentLoaded', getTasks);

/**
 * Handles the task form submission event.
 * @listens submit
 * @param {Event} event - The form submission event.
 */
taskForm.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent the default form submission behavior.

  /**
   * @type {string} title - The trimmed task title input value.
   * @type {string} description - The trimmed task description input value.
   * @type {number} story_point - The task's story point estimate, parsed as an
   *     integer.
   * @type {string} development_tag - The development stage or area associated
   *     with the task.
   * @type {string} priority_tag - The priority level of the task (e.g., high,
   *     medium, low).
   * @type {string} progress_tag - The current progress status of the task
   *     (e.g., not started, in-progress, completed).
   */
  const title = document.getElementById('title').value.trim();
  const description = document.getElementById('description').value.trim();
  const story_point = parseInt(
      document.getElementById('story-point').value.trim());
  let developmentTags = 0;
  // Calculate the bit vector for selected checkboxes
  document.querySelectorAll('input[name="development-tags"]:checked').
      forEach((checkbox) => {
        developmentTags |= parseInt(checkbox.value); // Use bitwise OR
        // to add the value
      });
  let development_bit_vector = decToFiveDigitBinary(developmentTags);

  const priority_tag = document.getElementById('priority-tag').value;
  const progress_tag = document.getElementById('progress-tag').value;

  console.log('Title: ' + title + '\nDesc: ' + description + '\nDevelopment' +
      ' Tag: ' + development_bit_vector + '\nPriority Tag: ' + priority_tag +
      '\nStory Point: ' + story_point +
      '\nProgress Tag: ' + progress_tag);

  // Check if parameters are provided
  if (title && description && !isNaN(story_point) && (developmentTags > 0) &&
      priority_tag && progress_tag) {
    if (story_point >= 1 && story_point <= 10) {
      // Story point is valid, proceed with task creation
      addTask(title, description, story_point, development_bit_vector,
          priority_tag,
          progress_tag);
      // Clear the form fields
      taskForm.reset();
      closeForm();
    } else {
      // Alert if story point is out of range
      alert('Story point estimate must be between 1 and 10.');
    }
  } else {
    // Alert if inputs are empty
    alert('Please enter all parameters');
  }
});

/**
 * Sends a POST request to add a task and updates the task list.
 *
 * @param {string} title - The task title.
 * @param {string} description - The task description.
 * @param {number} story_point - The task's story point estimate.
 * stage or area associated with the task (e.g., frontend, backend).
 * @param {string} development_bit_vector - The bit vector representing the
 * development tags
 * @param {string} priority_tag - The tag indicating the priority level of
 * the task (e.g., high, medium, low).
 * @param {string} progress_tag - The tag indicating the current progress
 * status of the task (e.g., not started, in-progress, completed).
 */
function addTask(
    title, description, story_point, development_bit_vector, priority_tag,
    progress_tag) {
  fetch('/add_task', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title,
      description,
      story_point,
      development_bit_vector,
      priority_tag,
      progress_tag,
    }),
  }).then(response => response.json()).then(tasks => {
    // Update the task list with the new tasks
    appendTask(tasks);
  })
      // Log errors to the console
      .catch(error => console.error('Error:', error));
}

/**
 * Sends a DELETE request to remove a task and updates the task list.
 *
 * @param {number} taskId - The ID of the task to be deleted.
 */
function deleteTask(taskId) {
  fetch(`/delete_task/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(() => {
    getTasks();
  }).catch(error => console.error('Error:', error));
}

/**
 * Sends a GET request to fetch tasks from the server and updates the task list.
 */
function getTasks() {
  fetch('/get_tasks', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json()).then(data => {
    // Update the task list with the tasks received from the server
    displayListView(data.tasks);
    displayCardView(data.tasks);
  })
      // Log errors to the console
      .catch(error => console.error('Error:', error));
}

/**
 * Updates the task list in the DOM with the provided tasks.
 *
 * @param {Array<Object>} tasks - Array of task objects, each containing title,
 * description, and id properties.
 */
function displayListView(tasks) {
  // Clear the current task list
  listView.innerHTML = '';

  // Update the task list with the new tasks
  tasks.forEach(task => {
    /** @type {Element} taskItem - The list item element for the task. */
    const taskItem = document.createElement('div');
    taskItem.className = 'task-item';
    // Add task title, description and delete button
    taskItem.innerHTML = `
    <div class="list-header">
      <strong>${task.title}</strong>
      <button class="icon-button edit-task-btn"><img src="static/images/icon-edit.svg" alt="edit-task" class="icon edit-task-icon" onclick="handleEditButton(${task.id})"/></button>
    </div>
    <div>
      Story Points: ${task.story_point}<br>
      Priority: <span class="task-tag priority-tag">#${task.priority_tag}</span><br>
      Status: <span class="task-tag progress-tag">#${task.progress_tag}</span><br>
      <div class="development-tags">Dev: </div></div>`;
    // Create the span elements for development tags and append to taskItem
    taskItem.querySelector('.development-tags').
        appendChild(decodeDevelopmentTags(task.development_bit_vector));

    taskItem.innerHTML += `
      <button type="button" class="delete-task-btn" onclick="confirmDeletion('${task.title}', ${task.id})">&times;</button>
    </div>
    <button type="button" class="read-more-btn" onclick="openModal(${task.id})">Read More</button>
  `;
    // Append the new task to the task list
    listView.appendChild(taskItem);
  });
}

/**
 * Updates the task list in the DOM with the provided tasks.
 *
 * @param {Array<Object>} tasks - Array of task objects, each containing title,
 * description, and id properties.
 */
function displayCardView(tasks) {
  // Clear the columns
  document.getElementById('not-started-tasks').innerHTML = '';
  document.getElementById('in-progress-tasks').innerHTML = '';
  document.getElementById('completed-tasks').innerHTML = '';

  tasks.forEach(task => {
    // Create task card element
    const taskItem = document.createElement('div');
    taskItem.className = 'task-card';
    taskItem.setAttribute('draggable', 'true');
    taskItem.setAttribute('id', `task-${task.id}`); // Add unique ID for each
                                                    // task

    // Add task details (title, description, etc.)
    taskItem.innerHTML = `
    <div class="list-header">
      <strong>${task.title}</strong>
      <button class="icon-button edit-task-btn"><img src="static/images/icon-edit.svg" alt="edit-task" class="icon edit-task-icon" onclick="handleEditButton(${task.id})"/></button>
    </div>
      <text class="author">${task.user}</text><br>
      <span class="story-point">Story Points: ${task.story_point}</span>
    <div class="task-tags">
      <span class="task-tag priority-tag">#${task.priority_tag}</span><br>
      <span class="task-tag progress-tag">#${task.progress_tag}</span>
      <div class="development-tags"></div>
    </div>
    <p class="task-description">${task.description}</p>
    Created At: ${task.created_at}<br>
    <button type="button" class="delete-task-btn" onclick="confirmDeletion('${task.title}', ${task.id})">&times;</button>
    </div>
    <button type='button' class="button read-more-btn displaystyle='width=100%'" onclick="openModal(${task.id})">Read More</button>
    `;

    taskItem.querySelector('.development-tags').
        appendChild(decodeDevelopmentTags(task.development_bit_vector));

    // Append task to the correct column based on the status
    if (task.progress_tag === 'not-started') {
      document.getElementById('not-started-tasks').appendChild(taskItem);
    } else if (task.progress_tag === 'in-progress') {
      document.getElementById('in-progress-tasks').appendChild(taskItem);
    } else if (task.progress_tag === 'completed') {
      document.getElementById('completed-tasks').appendChild(taskItem);
    }

    // Make sure drag listeners are added
    taskItem.addEventListener('dragstart', dragStart);
    taskItem.addEventListener('dragend', dragEnd);
  });
}

/**
 * Initializes event listeners for showing and hiding the secondary progress tag
 * when the primary progress tag changes.
 * @listens {DOMContentLoaded}
 */
document.addEventListener('DOMContentLoaded', function() {
  /**
   * @const {Element} progressTag - Reference to the primary progress tag
   *     select element.
   * @const {Element} inProgressTag - Reference to the secondary in-progress
   *     tag select element.
   * @const {Element} inProgressLabel - Reference to the label for the
   *     in-progress tag.
   */
  const progressTag = document.getElementById('progress-tag');
  const inProgressTag = document.getElementById('in-progress-tag');
  const inProgressLabel = document.querySelector(
      'label[for="in-progress-tag"]');

  /**
   * Toggles the visibility of the secondary progress tag and its label based on
   * the value of the primary progress tag.
   * @listens {change}
   */
  progressTag.addEventListener('change', function() {
    // Show in-progress tag and label if the primary tag is set to 'in-progress'
    if (progressTag.value === 'in-progress') {
      inProgressTag.style.visibility = 'visible';
      inProgressLabel.style.visibility = 'visible';
    } else {
      // Otherwise, hide the in-progress tag and its label
      inProgressTag.style.visibility = 'hidden';
      inProgressLabel.style.visibility = 'hidden';
    }
  });
});

/**
 * Appends a new task to the existing task list in the DOM.
 *
 * @param {Object} task - The new task object containing title, description,
 *     and story_point.
 */
function appendTask(task) {
  const taskItem = document.createElement('div');
  taskItem.className = 'task-item';
  // Create the task content
  taskItem.innerHTML = `
    <div class="list-header">
      <strong>${task.title}</strong>
      <button class="icon-button edit-task-btn"><img src="static/images/icon-edit.svg" alt="edit-task" class="icon edit-task-icon"/></button>
    </div>
    <div>
      Story Points: ${task.story_point}<br>
      Priority: <span class="task-tag priority-tag">#${task.priority_tag}</span><br>
      Status: <span class="task-tag progress-tag">#${task.progress_tag}</span><br>
      <div class="development-tags">Dev: </div>
    </div>
  <button type="button" class="delete-task-btn" onclick="confirmDeletion('${task.title}', ${task.id})">&times;</button>
  <button type="button" class="read-more-btn" onclick="openModal(${task.id})">Read More</button>`;
  // Create the span elements for development tags and append to taskItem
  taskItem.querySelector('.development-tags').
      appendChild(decodeDevelopmentTags(task.development_bit_vector));

  // Append the new task to the task list and card view
  listView.appendChild(taskItem);
  appendTaskToCardView(task);
}

/**
 * Appends the new task to the appropriate column in the card view.
 *
 * @param {Object} task - The new task object.
 */
function appendTaskToCardView(task) {
  const taskItem = document.createElement('div');
  taskItem.className = 'task-card';
  taskItem.setAttribute('draggable', 'true');
  taskItem.setAttribute('id', `task-${task.id}`);

  taskItem.innerHTML = `
    <div class="list-header">
      <strong>${task.title}</strong>
      <button class="icon-button edit-task-btn">
        <img src="static/images/icon-edit.svg" alt="edit-task" class="icon edit-task-icon"/>
      </button>
    </div>
    <text class="author">${task.user}</text><br>
    <span class="story-point">Story Points: ${task.story_point}</span>
    <div class="task-tags">
      <span class="task-tag priority-tag">#${task.priority_tag}</span><br>
      <span class="task-tag progress-tag">#${task.progress_tag}</span>
      <div class="development-tags"></div>
    </div>
    <p class="task-description">${task.description}</p>
    Created At: ${task.created_at}<br>
    <button type="button" class="delete-task-btn" onclick="confirmDeletion('${task.title}', ${task.id})">&times;</button>
    <button type="button" class="read-more-btn" onclick="openModal(${task.id})">Read More</button>
  `;

  // Append development tags to the card
  taskItem.querySelector('.development-tags').
      appendChild(decodeDevelopmentTags(task.development_bit_vector));

  // Append the task card to the appropriate column based on progress tag
  if (task.progress_tag === 'not-started') {
    document.getElementById('not-started-tasks').appendChild(taskItem);
  } else if (task.progress_tag === 'in-progress') {
    document.getElementById('in-progress-tasks').appendChild(taskItem);
  } else if (task.progress_tag === 'completed') {
    document.getElementById('completed-tasks').appendChild(taskItem);
  }

  // Add drag event listeners to the task card
  taskItem.addEventListener('dragstart', dragStart);
  taskItem.addEventListener('dragend', dragEnd);
}

// Function to open the task details modal and display task details
function openModal(taskId) {
  fetch(`/get_task/${taskId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json()).then(task => {
    // Populate the modal with task details
    document.getElementById('modal-title').innerText = task.title;
    document.getElementById('modal-description').innerText = task.description;
    document.getElementById('modal-story-points').innerText = task.story_point;
    document.getElementById('modal-priority').innerText = '#' +
        task.priority_tag;
    document.getElementById('modal-status').innerText = '#' + task.progress_tag;
    document.getElementById('modal-development-tags').innerHTML = '';
    document.querySelector('.development-tags').
        appendChild(decodeDevelopmentTags(task.development_bit_vector));
    document.getElementById('modal-creator').innerText = task.user;
    document.getElementById('modal-created-at').innerText = task.created_at;

    // Show the task details modal
    document.getElementById('task-details-modal').style.display = 'block';
  });
}

// Function to close the task details modal
function closeModal() {
  document.getElementById('task-details-modal').style.display = 'none';
}

// Function to toggle between card and list view
function toggleView(view) {
  const listViewButton = document.getElementById('list-view-button');
  const cardViewButton = document.getElementById('card-view-button');

  if (view === 'list') {
    console.log('Switch to list view');
    listView.style.display = 'flex';
    cardView.style.display = 'none';
    listViewButton.classList.add('active');
    cardViewButton.classList.remove('active');
  } else if (view === 'card') {
    console.log('Switch to card view');
    listView.style.display = 'none';
    cardView.style.display = 'block';
    cardViewButton.classList.add('active');
    listViewButton.classList.remove('active');
  }
}

/**
 * Decodes the development tags from the bit vector string and returns them as
 * an array of hashtags.
 * @param {string} bitVector - A string representing the bit vector.
 * @returns {DocumentFragment} - A string of hashtags separated by spaces.
 */
function decodeDevelopmentTags(bitVector) {
  const fragment = document.createDocumentFragment();
  // Iterate over the bit vector
  for (let i = bitVector.length - 1, j = 0; i >= 0; i--, j++) {
    // Check if the current bit is '1'
    if (bitVector[i] === '1') {
      // Create a new span element with the corresponding tag
      const span = document.createElement('span');
      span.className = 'task-tag development-tag';
      span.textContent = `#${availableTags[j]}`;
      fragment.appendChild(span);
    }
  }
  return fragment;
}

function decToFiveDigitBinary(decimal) {
  // Convert decimal to binary and get a string
  let binaryString = decimal.toString();

  // Pad with leading zeros to ensure it's at least 5 digits
  while (binaryString.length < 5) {
    binaryString = '0' + binaryString; // Add leading zero
  }

  if (binaryString.length > 5) {
    console.warn(
        'Warning: The decimal value exceeds the range for a 5-digit binary representation.');
    // Truncates to last 5 digits
    binaryString = binaryString.slice(-5);
  }
  return binaryString;
}

/**
 * Confirms task deletion and deletes the task if confirmed.
 *
 * @param {string} taskTitle - The title of the task to delete.
 * @param {number} taskId - The ID of the task to delete.
 */
function confirmDeletion(taskTitle, taskId) {
  const confirmation = confirm(`Are you sure you want to delete "${taskTitle}"?`);

  if (confirmation) {
    deleteTask(taskId) // Attempt to delete the task from the server.
        .then(() => {
          alert(`"${taskTitle}" has been deleted.`);
        })
        .catch((error) => {
      console.error('Error deleting task:', error);
      alert(`Failed to delete "${taskTitle}". Please try again.`);
    });
  } else {
    alert(`"${taskTitle}" was not deleted.`);
  }
}
