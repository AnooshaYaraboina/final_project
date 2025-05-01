// --------- SEARCH FUNCTION ---------
function performSearch() {
    let query = document.getElementById("searchInput")?.value.trim();

    if (!query) {
        document.getElementById("searchResults").innerHTML = "<p>Please enter a search term.</p>";
        return;
    }

    // Simulate encrypted search logic
    let simulatedResults = ["Alice", "Bob", "Charlie", "David"];
    let filteredResults = simulatedResults.filter(name => name.toLowerCase().includes(query.toLowerCase()));

    let resultHtml = "<h3>Search Results:</h3>";
    if (filteredResults.length > 0) {
        resultHtml += "<ul>";
        filteredResults.forEach(result => {
            resultHtml += `<li>${result}</li>`;
        });
        resultHtml += "</ul>";
    } else {
        resultHtml += "<p>No matching results found.</p>";
    }

    document.getElementById("searchResults").innerHTML = resultHtml;
}

// --------- AUTH FORM TOGGLE ---------
document.addEventListener("DOMContentLoaded", function () {
    const toggleAuthText = document.getElementById("toggle-auth");
    const authTitle = document.getElementById("auth-title");
    const nameInput = document.getElementById("name");
    const authForm = document.getElementById("auth-form");

    if (toggleAuthText) {
        toggleAuthText.addEventListener("click", function () {
            if (authTitle.innerText === "Login") {
                authTitle.innerText = "Sign Up";
                nameInput.classList.remove("hidden");
                authForm.querySelector("button").innerText = "Sign Up";
                toggleAuthText.innerHTML = "Already have an account? <span>Login</span>";
            } else {
                authTitle.innerText = "Login";
                nameInput.classList.add("hidden");
                authForm.querySelector("button").innerText = "Login";
                toggleAuthText.innerHTML = "Don't have an account? <span>Sign Up</span>";
            }
        });
    }

    // --------- FILE UPLOAD FUNCTION ---------
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");

    if (uploadForm && fileInput && uploadStatus) {
        uploadForm.addEventListener("submit", function (e) {
            e.preventDefault();

            if (!fileInput.files.length) {
                uploadStatus.textContent = "Please select a file.";
                uploadStatus.className = "status-text error";
                return;
            }

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);

            fetch("/upload", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    uploadStatus.textContent = "✅ File uploaded successfully!";
                    uploadStatus.className = "status-text success";
                    fileInput.value = "";
                } else {
                    uploadStatus.textContent = "❌ Upload failed.";
                    uploadStatus.className = "status-text error";
                }
            })
            .catch(() => {
                uploadStatus.textContent = "❌ Upload failed. Server error.";
                uploadStatus.className = "status-text error";
            });
        });
    }
});
