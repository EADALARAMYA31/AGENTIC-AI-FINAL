const API = "http://localhost:3000";

/// -------- ADD ASSIGNMENT ----------
async function addAssignment() {

    const data = {
        name: document.getElementById("name").value,
        subject: document.getElementById("subject").value,
        deadline: document.getElementById("deadline").value
    };

    await fetch(API + "/addAssignment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    alert("Assignment Added!");

    loadCalendar(); // ✅ refresh calendar
}

/// -------- SHOW ASSIGNMENTS ----------
async function showAssignments() {

    const res = await fetch(API + "/assignments");
    const assignments = await res.json();

    const list = document.getElementById("assignmentList");
    list.innerHTML = "";

    assignments.forEach(a => {
        const li = document.createElement("li");
        li.textContent =
            `${a.name} - ${a.subject} (Deadline: ${a.deadline})`;
        list.appendChild(li);
    });
}

/// -------- LOAD CALENDAR ----------
async function loadCalendar() {

    const res = await fetch(API + "/events");
    const events = await res.json();

    const cal = document.getElementById("calendar");
    cal.innerHTML = "";

    events.forEach(e => {
        const li = document.createElement("li");
        li.textContent = `${e.title} — ${e.date}`;
        cal.appendChild(li);
    });
}

/// -------- AI ASSISTANT ----------
async function askAI() {

    const question =
        document.getElementById("question").value;

    const res = await fetch(API + "/askAI", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ question })
    });

    const data = await res.json();

    document.getElementById("reply").innerText =
        data.reply;
}

/// load calendar on start
loadCalendar();