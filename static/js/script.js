const themeToggle = document.getElementById("theme-toggle");

themeToggle.onclick = () => {

    document.body.classList.toggle("light-mode");

    if(document.body.classList.contains("light-mode")){

        themeToggle.innerHTML = "☀️";

    }else{

        themeToggle.innerHTML = "🌙";
    }
}


/* LIVE CLOCK */

function updateClock(){

    const now = new Date();

    const time = now.toLocaleTimeString();

    const date = now.toLocaleDateString(
        'en-IN',
        {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        }
    );

    document.getElementById("live-clock").innerHTML = time;

    document.getElementById("live-date").innerHTML = date;
}

setInterval(updateClock, 1000);

updateClock();