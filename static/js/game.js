let selectedNumber = null;
let currentScore = INITIAL_SCORE;
let seconds = INITIAL_TIME;
let timerInterval = null;

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("score-count").textContent = currentScore;
    document.getElementById("error-count").textContent = INITIAL_ERRORS;
    document.getElementById("time-counter").textContent = seconds;

    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById("time-counter").textContent = seconds;
    }, 1000);

    const numberButtons = document.querySelectorAll(".number-btn");
    const cells = document.querySelectorAll(".cell.editable");

    numberButtons.forEach(button => {
        button.addEventListener("click", function () {
            numberButtons.forEach(b => b.classList.remove("selected"));
            this.classList.add("selected");
            selectedNumber = parseInt(this.dataset.number);
        });
    });

    cells.forEach(cell => {
        cell.addEventListener("click", function () {
            if (!selectedNumber) return;

            fetch("/play", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    row: parseInt(this.dataset.row),
                    col: parseInt(this.dataset.col),
                    value: selectedNumber
                })
            })
            .then(res => res.json())
            .then(data => {

                if (data.score !== undefined) {
                    currentScore += data.score;
                    document.getElementById("score-count").textContent = currentScore;
                }

                if (data.status === "ok") {
                    this.textContent = selectedNumber;
                    this.classList.remove("editable");
                }
                else if (data.status === "win") {
                    clearInterval(timerInterval);

                    fetch("/finish-game", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ elapsed_time: seconds })
                    }).then(() => {
                        alert("Congratulations! You win 🎉");
                        window.location.href = "/menu";
                    });
                }
                else if (data.status === "game_over") {
                    clearInterval(timerInterval);
                    alert("Game Over");
                    window.location.href = "/menu";
                }
                else {
                    document.getElementById("error-count").textContent = data.errors;
                }
            });
        });
    });
});
