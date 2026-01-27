const newGameBtn = document.getElementById("new-game-btn");
const difficultySelector = document.getElementById("difficulty-selector");

if (newGameBtn) {
    newGameBtn.addEventListener("click", () => {
        difficultySelector.classList.toggle("hidden");
    });
}
