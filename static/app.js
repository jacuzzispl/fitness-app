const formWorkout = document.getElementById("workoutForm");
const formExercise = document.getElementById("exerciseForm");
const formExerciseInputs = formExercise.querySelectorAll("input, button");

formWorkout.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!formWorkout.checkValidity()) {
        formWorkout.reportValidity();
        return;
    }

    formExerciseInputs.forEach(el => el.disabled = false);
});


async function submitExercise() {
    console.log("Successful - Exercise")
    const exercise = {
                exercise: document.getElementById("exerciseName").value,
                sets: Number(document.getElementById("sets").value),
                reps: Number(document.getElementById("reps").value),
                weight: Number(document.getElementById("weight").value),
                type: "Exercise"
    }


    const response = await fetch("http://127.0.0.1:8000/workouts", {
        method: "POST",
        headers: { "Content-Type" : "application/json" },
        body: JSON.stringify(exercise)
    });

    const data = await response.json();
    console.log("Server response:", data);

};






async function submitWorkout() {
    console.log("Successful - Workout")
    const workout = {
        name: document.getElementById("workoutName").value,
        date: document.getElementById("workoutDate").value,
        type: "Workout"
    }

    const response = await fetch("http://127.0.0.1:8000/workouts", {
        method: "POST",
        headers: {"Content-Type" : "application/json"},
        body: JSON.stringify(workout)
    });

    const data = await response.json()
    console.log(data)


}



function redirect(url) {
    window.location.href = url
}



function async uploadFile() {
    
}



