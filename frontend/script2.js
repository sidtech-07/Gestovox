// ========================
// Session Management Logic
// ========================

// Check authentication status on page load
window.onload = function() {
    // Fade-in animation
    document.body.style.opacity = '1';

    // Check login status for all pages
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const currentPage = window.location.pathname;

    // Redirect logic
    if (currentPage.includes('dashboard.html') || currentPage.includes('contact.html')|| currentPage.includes('about.html')) {
        if (!isLoggedIn) {
            window.location.href = 'index.html';
        }
    }

    if (currentPage.includes('index.html') && isLoggedIn) {
        window.location.href = 'about.html';
    }

    // Page-specific functionality
    if (currentPage.includes('index.html')) {
        // Pre-fill username from localStorage
        const savedUsername = localStorage.getItem('gestureUser');
        if (currentPage.includes('index.html')) {
            const savedUsername = localStorage.getItem('gestureUser');
            if (savedUsername) {
                document.getElementById('username').value = savedUsername;
            }
    
            document.getElementById('loginForm').addEventListener('submit', function (e) {
                e.preventDefault();
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value.trim();
    
                if (username && password) {
                    const savedPassword = localStorage.getItem(`gesturePassword_${username}`);
    
                    if (savedPassword) {
                        // Check if the entered password matches the saved password
                        if (password === savedPassword) {
                            sessionStorage.setItem('isLoggedIn', 'true');
                            sessionStorage.setItem('username', username);
                            window.location.href = 'about.html';
                        } else {
                            alert('Incorrect password');
                        }
                    } else {
                        // Save the username and password for the first time
                        localStorage.setItem('gestureUser', username);
                        localStorage.setItem(`gesturePassword_${username}`, password);
                        sessionStorage.setItem('isLoggedIn', 'true');
                        sessionStorage.setItem('username', username);
                        window.location.href = 'about.html';
                    }
                }
            });
        }
    }

    if (currentPage.includes('dashboard.html')||currentPage.includes('about.html')) {
        // Display username from session
        const username = sessionStorage.getItem('username');
        if (username) {
            document.getElementById('userDisplay').textContent = username;
        }

       // Flag to track system state
let isActive = false;

// Launch system handler
document.getElementById('launchButton').addEventListener('click', function() {
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching System...';
    this.disabled = true;

    setTimeout(() => {
        alert('Control system activated! It will now run in the background.');
        this.innerHTML = '<i class="fas fa-check"></i> System Active';
        isActive = true; // Mark system as active

        // Enable the stop button
        let stopButton = document.getElementById('stop-btn');
        stopButton.innerHTML = '<i class="fas fa-stop-circle"></i> Stop System';
        stopButton.disabled = false;
    }, 2000);
});

// Stop system handler
document.getElementById('stop-btn').addEventListener('click', function() {
    // Check if system is active
    if (!isActive) {
        alert("Please activate the system first!");
        return; // Exit without running further code
    }

    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping System...';
    this.disabled = true;

    setTimeout(() => {
        alert('Control system stopped!');
        this.innerHTML = '<i class="fas fa-check"></i> System Stopped';
        isActive = false; // Mark system as inactive

        // Enable the launch button again
        let launchButton = document.getElementById('launchButton');
        launchButton.innerHTML = '<i class="fas fa-play-circle"></i> Launch System';
        launchButton.disabled = false;
    }, 2000);
});



        // Logout handler
        document.getElementById('logoutButton').addEventListener('click', function() {
            sessionStorage.clear();
            window.location.href = 'index.html';
        });
    }
};

// ========================
// Session Timeout Handler
// ========================
let idleTimer;
function resetIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(logoutDueToInactivity, 1800000); // 30 minutes
}

function logoutDueToInactivity() {
    sessionStorage.clear();
    alert('Session expired due to inactivity');
    window.location.href = 'index.html';
}

// Track user activity
document.addEventListener('mousemove', resetIdleTimer);
document.addEventListener('keypress', resetIdleTimer);



document.getElementById("launch-btn").addEventListener("click", function() {
    fetch("http://127.0.0.1:5000/start_transcription")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById("status").innerText = "Listening...";
            getTranscription();
        })
        .catch(error => console.error("Error:", error));
});
document.getElementById("launch-btn").addEventListener('click', function() {
    fetch("http://127.0.0.1:5000/stop_transcription")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById("status").innerText = "Stopped";
        })
        .catch(error => console.error("Error:", error));
});



function getTranscription() {
    setTimeout(() => {
        fetch("http://127.0.0.1:5000/get_transcription")
            .then(response => response.json())
            .then(data => {
                document.getElementById("transcription").innerText = data.transcription;
            })
            .catch(error => console.error("Error:", error));
    }, 5000);  // Wait 5 seconds before fetching transcription
}
document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll(".main-nav a");

    function changeActiveNav() {
        let scrollPosition = window.scrollY + 100; // Offset for better detection

        sections.forEach((section) => {
            if (scrollPosition >= section.offsetTop && scrollPosition < section.offsetTop + section.offsetHeight) {
                navLinks.forEach((link) => link.classList.remove("active"));

                let activeLink = document.querySelector(`.main-nav a[href="#${section.id}"]`);
                if (activeLink) {
                    activeLink.classList.add("active");
                }
            }
        });
    }

    window.addEventListener("scroll", changeActiveNav);
    changeActiveNav(); // Run on page load
});
