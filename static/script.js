const descriptionInput = document.getElementById("jobDescription");
const analyzeBtn = document.getElementById("analyzeBtn");
const buttonText = document.getElementById("buttonText");
const charCount = document.getElementById("charCount");
const errorBox = document.getElementById("errorBox");
const loadingBox = document.getElementById("loadingBox");
const loadingText = document.getElementById("loadingText");
const reportSection = document.getElementById("reportSection");

let currentReport = null;

const sampleDescription = `We are hiring an AI Engineer at ABC Technologies.
Candidates should have 2-4 years of experience in Artificial
Intelligence and Machine Learning. Required technical skills
include Python, FastAPI, LangGraph, SQL and LLM APIs.
Strong communication, teamwork and problem-solving skills
are important. This is a full-time hybrid position.`;

descriptionInput.addEventListener("input", () => {
    charCount.textContent =
        `${descriptionInput.value.length} / 20000 characters`;
});

document.getElementById("sampleBtn").addEventListener("click", () => {
    descriptionInput.value = sampleDescription;
    descriptionInput.dispatchEvent(new Event("input"));
    descriptionInput.focus();
});

function showTags(containerId, skills) {
    const container = document.getElementById(containerId);
    container.replaceChildren();

    if (!Array.isArray(skills) || skills.length === 0) {
        const empty = document.createElement("span");
        empty.className = "empty-text";
        empty.textContent = "No skills identified.";
        container.appendChild(empty);
        return;
    }

    skills.forEach((skill) => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = String(skill);
        container.appendChild(tag);
    });
}

function showTopSkills(skills) {
    const container = document.getElementById("topSkills");
    container.replaceChildren();

    if (!Array.isArray(skills) || skills.length === 0) {
        const empty = document.createElement("p");
        empty.className = "empty-text";
        empty.textContent = "No priority skills identified.";
        container.appendChild(empty);
        return;
    }

    skills.slice(0, 3).forEach((skill, index) => {
        const item = document.createElement("div");
        item.className = "top-skill";

        const number = document.createElement("span");
        number.className = "skill-number";
        number.textContent = String(index + 1);

        const name = document.createElement("span");
        name.textContent = String(skill);

        item.append(number, name);
        container.appendChild(item);
    });
}

function displayReport(report) {
    document.getElementById("jobTitle").textContent =
        report.job_title || "Not specified";

    document.getElementById("companyName").textContent =
        report.company_name || "Company not specified";

    document.getElementById("experience").textContent =
        report.required_experience || "Not specified";

    document.getElementById("jobCategory").textContent =
        report.job_category || "Other";

    document.getElementById("employmentType").textContent =
        report.employment_type || "Not specified";

    document.getElementById("workArrangement").textContent =
        report.work_arrangement || "Not specified";

    document.getElementById("hiringSummary").textContent =
        report.hiring_summary || "No summary available.";

    showTags("requiredSkills", report.required_skills);
    showTags("technicalSkills", report.technical_skills);
    showTags("softSkills", report.soft_skills);
    showTopSkills(report.top_3_skills);

    reportSection.classList.remove("hidden");

    reportSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

analyzeBtn.addEventListener("click", async () => {
    const description = descriptionInput.value.trim();

    errorBox.classList.add("hidden");

    if (!description) {
        showError("Please paste a job description first.");
        descriptionInput.focus();
        return;
    }

    if (description.length < 30) {
        showError(
            "Please enter a more detailed job description " +
            "(at least 30 characters)."
        );
        return;
    }

    analyzeBtn.disabled = true;
    buttonText.textContent = "Analyzing...";
    loadingBox.classList.remove("hidden");
    reportSection.classList.add("hidden");

    const stages = [
        "Extracting job information...",
        "Classifying the job...",
        "Analyzing technical and soft skills...",
        "Preparing the hiring report..."
    ];

    let stageIndex = 0;
    loadingText.textContent = stages[stageIndex];

    const stageTimer = setInterval(() => {
        stageIndex = (stageIndex + 1) % stages.length;
        loadingText.textContent = stages[stageIndex];
    }, 1800);

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                job_description: description
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to analyze this job description."
            );
        }

        if (!data.report) {
            throw new Error("The server returned an empty report.");
        }

        currentReport = data.report;
        displayReport(currentReport);

    } catch (error) {
        showError(
            error.message ||
            "Connection failed. Please check whether the server is running."
        );
    } finally {
        clearInterval(stageTimer);
        loadingBox.classList.add("hidden");
        analyzeBtn.disabled = false;
        buttonText.textContent = "Analyze Job Description";
    }
});

document.getElementById("downloadBtn").addEventListener("click", () => {
    if (!currentReport) {
        showError("Please analyze a job description first.");
        return;
    }

    const json = JSON.stringify(currentReport, null, 4);
    const blob = new Blob([json], {
        type: "application/json;charset=utf-8"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "hiring_report.json";
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);
});

document.getElementById("newAnalysisBtn").addEventListener("click", () => {
    descriptionInput.value = "";
    descriptionInput.dispatchEvent(new Event("input"));

    currentReport = null;
    reportSection.classList.add("hidden");
    errorBox.classList.add("hidden");

    descriptionInput.focus();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});
