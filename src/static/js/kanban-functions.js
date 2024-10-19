document.addEventListener('DOMContentLoaded', () => {
  const kanbanCells = document.querySelectorAll('.card-grid');

  // Make kanban cells droppable
  kanbanCells.forEach(cell => {
    cell.addEventListener('dragover', dragOver);
    cell.addEventListener('dragenter', dragEnter);
    cell.addEventListener('dragleave', dragLeave);
    cell.addEventListener('drop', drop);
  });
});


function dragStart(e) {
  // Add a class to indicate dragging
  this.classList.add('dragging');

  // Get the initial mouse offset relative to the card's position
  e.dataTransfer.setData('text/plain', this.id); // For Firefox
  sourceCell = this.closest('.column');
}

function dragEnd() {
  this.classList.remove('dragging');
}

function dragOver(e) {
  e.preventDefault();
}

function dragEnter(e) {
  // Highlight drop zone on drag enter
  e.preventDefault();
  this.classList.add('drag-over');
}

function dragLeave() {
  this.classList.remove('drag-over');
}

function drop(e) {
  e.preventDefault();
  this.classList.remove('drag-over');

  // Select the dragged task card
  const card = document.querySelector('.dragging');

  // Append the dragged task card to the drop target (kanban cell)
  e.currentTarget.appendChild(card);
}
