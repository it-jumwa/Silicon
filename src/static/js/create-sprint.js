document.addEventListener("DOMContentLoaded", function() {
    // Reference to the button that shows the sprint form
    const createSprintBtn = document.getElementById('create-sprint-btn');
    const sprintFormContainer = document.getElementById("sprint-form-container");
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");
    const submitSprintBtn = document.getElementById("submit-sprint-btn");

// sprint form
    createSprintBtn.addEventListener("click", function() {
        sprintFormContainer.style.display = 'block'; 
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        startDateInput.value = formattedDate; 
    });

    sprintFormContainer.addEventListener("submit", function(event) {
        event.preventDefault(); 

        const startDate = startDateInput.value; 
        const endDate = endDateInput.value;

        if (startDate && endDate) {
            // for future use 
            localStorage.setItem('sprintStartDate', startDate);
            localStorage.setItem('sprintEndDate', endDate);

            alert("Sprint created successfully...\n Start Date: " + startDate + "\n End Date: " + endDate);
            startDateInput.value = '';
            endDateInput.value = '';
            sprintFormContainer.style.display = 'none';
        } 
    });
});

