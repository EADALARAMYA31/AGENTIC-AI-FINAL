const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const { google } = require("googleapis");
const nodemailer = require("nodemailer");
const cron = require("node-cron");

const app = express();
app.use(cors());
app.use(bodyParser.json());

const PORT = 3000;

/* ---------------- GOOGLE CALENDAR SETUP ---------------- */

const auth = new google.auth.GoogleAuth({
  keyFile: "credentials.json",
  scopes: ["https://www.googleapis.com/auth/calendar"],
});

const calendar = google.calendar({ version: "v3", auth });

/* ---------------- LOCAL STORAGE ---------------- */

let assignments = [];

/* ---------------- GET EVENTS FROM CALENDAR ---------------- */

async function getEvents(date) {

  const res = await calendar.events.list({
    calendarId: "primary",
    timeMin: new Date(date + "T00:00:00Z").toISOString(),
    timeMax: new Date(date + "T23:59:59Z").toISOString(),
    singleEvents: true,
    orderBy: "startTime",
  });

  return res.data.items;
}

/* ---------------- CONFLICT DETECTION ---------------- */

function hasConflict(newStart, newEnd, events) {

  for (const e of events) {

    if (!e.start.dateTime) continue;

    const start = new Date(e.start.dateTime);
    const end = new Date(e.end.dateTime);

    if (newStart < end && newEnd > start) {
      return true;
    }
  }
  return false;
}

/* ---------------- ADD EVENT ---------------- */

app.post("/addEvent", async (req, res) => {

  try {

    const { name, date, start, end, priority } = req.body;

    const newStart = new Date(`${date}T${start}:00`);
    const newEnd = new Date(`${date}T${end}:00`);

    const events = await getEvents(date);

    if (hasConflict(newStart, newEnd, events)) {
      return res.json({ message: "⚠ Conflict detected!" });
    }

    await calendar.events.insert({
      calendarId: "primary",
      resource: {
        summary: `${name} (${priority})`,
        start: { dateTime: newStart },
        end: { dateTime: newEnd },
      },
    });

    res.json({ message: "✅ Event added successfully" });

  } catch (err) {
    console.log(err);
    res.status(500).send("Error creating event");
  }
});

/* ---------------- GET EVENTS ---------------- */

app.get("/events", async (req, res) => {

  const result = await calendar.events.list({
    calendarId: "primary",
    maxResults: 20,
    singleEvents: true,
    orderBy: "startTime",
  });

  const events = result.data.items.map(e => ({
    title: e.summary,
    date: e.start.dateTime?.split("T")[0],
    start: e.start.dateTime?.split("T")[1]?.substring(0,5),
    end: e.end.dateTime?.split("T")[1]?.substring(0,5)
  }));

  res.json(events);
});

/* ---------------- ASSIGNMENTS ---------------- */

app.post("/addAssignment", (req, res) => {

  assignments.push(req.body);
  res.json({ message: "Assignment Added" });
});

app.get("/assignments", (req, res) => {

  const today = new Date();

  assignments.forEach(a => {
    const diff =
      (new Date(a.deadline) - today) / (1000 * 60 * 60 * 24);

    if (diff <= 1) a.warning = "Due Soon!";
  });

  res.json(assignments);
});

/* ---------------- FREE TIME FINDER ---------------- */

async function findFreeTime() {

  const result = await calendar.events.list({
    calendarId: "primary",
    singleEvents: true,
    orderBy: "startTime",
  });

  const events = result.data.items;

  if (events.length === 0)
    return "🎉 You are completely free tomorrow.";

  const lastEvent = events[events.length - 1];

  return `You are free after ${lastEvent.end.dateTime.substring(11,16)}`;
}

/* ---------------- SIMPLE NLP ---------------- */

function parseSchedule(text) {

  text = text.toLowerCase();

  if (text.includes("tomorrow")) {

    const date = new Date();
    date.setDate(date.getDate() + 1);

    return {
      title: "Auto Meeting",
      date: date.toISOString().split("T")[0],
      time: "15:00",
    };
  }

  return null;
}

/* ---------------- AI ASSISTANT ---------------- */

app.post("/askAI", async (req, res) => {

  const q = req.body.question.toLowerCase();

  if (q.includes("free time")) {
    const reply = await findFreeTime();
    return res.json({ reply });
  }

  const schedule = parseSchedule(q);

  if (schedule) {
    return res.json({
      reply: `Understood! Scheduling ${schedule.title} tomorrow at ${schedule.time}`
    });
  }

  res.json({ reply: "I didn't understand the request." });
});

/* ---------------- EMAIL REMINDER ---------------- */

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "yourmail@gmail.com",
    pass: "app-password"
  }
});

function sendEmail(task) {

  transporter.sendMail({
    to: "student@gmail.com",
    subject: "Assignment Reminder",
    text: `${task} deadline is today!`
  });
}

/* CHECK EVERY HOUR */

cron.schedule("0 * * * *", () => {

  const today = new Date().toDateString();

  assignments.forEach(a => {

    if (new Date(a.deadline).toDateString() === today) {
      sendEmail(a.name);
    }
  });

});

/* ---------------- START SERVER ---------------- */

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});