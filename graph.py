import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

from schemas import (
    JobInformation,
    JobClassification,
    SkillAnalysis,
    HiringReport,
)

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY missing hai. .env file check karein."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=API_KEY,
)

class JobState(TypedDict, total=False):
    job_description: str
    job_title: str
    company_name: str
    required_experience: str
    required_skills: List[str]
    job_category: str
    employment_type: str
    work_arrangement: str
    technical_skills: List[str]
    soft_skills: List[str]
    top_3_skills: List[str]
    hiring_summary: str
    report: dict


# Node 1: Information Extraction
def information_extraction(state: JobState):
    extractor = llm.with_structured_output(JobInformation)

    result = extractor.invoke([
        (
            "system",
            "Extract job information only from the supplied "
            "job description. Do not invent missing details. "
            "Use Not specified when information is absent. "
            "Extract relevant required skills."
        ),
        ("human", state["job_description"]),
    ])

    return result.model_dump()


# Node 2: Job Classification
def job_classification(state: JobState):
    classifier = llm.with_structured_output(JobClassification)

    result = classifier.invoke([
        (
            "system",
            "Classify the job into a suitable category such as "
            "Artificial Intelligence, Web Development, Data "
            "Science, Mobile Development, DevOps, or Other. "
            "Determine employment type: Full-time, Part-time, "
            "Internship, Contract, or Not specified. "
            "Determine work arrangement: Remote, Hybrid, "
            "On-site, or Not specified. Do not confuse "
            "employment type with work arrangement."
        ),
        (
            "human",
            f"Job description:\n{state['job_description']}\n"
            f"Job title: {state.get('job_title', 'Not specified')}"
        ),
    ])

    return result.model_dump()


# Node 3: Skill Analysis
def skill_analysis(state: JobState):
    analyzer = llm.with_structured_output(SkillAnalysis)

    result = analyzer.invoke([
        (
            "system",
            "Analyze the job description and identify technical "
            "skills and soft skills. Select up to three most "
            "important skills based on the job requirements. "
            "Prefer skills explicitly required in the description. "
            "Do not invent employer requirements."
        ),
        (
            "human",
            f"Job description:\n{state['job_description']}\n"
            f"Required skills: {state.get('required_skills', [])}"
        ),
    ])

    # Limit the priority list to three skills.
    data = result.model_dump()
    data["top_3_skills"] = data["top_3_skills"][:3]
    return data


# Node 4: Hiring Report
def hiring_report(state: JobState):
    report = HiringReport(
        job_title=state.get("job_title", "Not specified"),
        company_name=state.get("company_name", "Not specified"),
        required_experience=state.get(
            "required_experience", "Not specified"
        ),
        required_skills=state.get("required_skills", []),
        job_category=state.get("job_category", "Other"),
        employment_type=state.get(
            "employment_type", "Not specified"
        ),
        work_arrangement=state.get(
            "work_arrangement", "Not specified"
        ),
        technical_skills=state.get("technical_skills", []),
        soft_skills=state.get("soft_skills", []),
        top_3_skills=state.get("top_3_skills", [])[:3],
        hiring_summary=(
            f"{state.get('job_title', 'This role')} belongs to "
            f"{state.get('job_category', 'Other')}. "
            "Review the listed skills and requirements "
            "against the original job description."
        ),
    )

    return {"report": report.model_dump()}


# Build and connect the graph
builder = StateGraph(JobState)

builder.add_node("information_extraction", information_extraction)
builder.add_node("job_classification", job_classification)
builder.add_node("skill_analysis", skill_analysis)
builder.add_node("hiring_report", hiring_report)

builder.add_edge(START, "information_extraction")
builder.add_edge("information_extraction", "job_classification")
builder.add_edge("job_classification", "skill_analysis")
builder.add_edge("skill_analysis", "hiring_report")
builder.add_edge("hiring_report", END)

job_graph = builder.compile()


def analyze_job(description: str) -> dict:
    if not description or not description.strip():
        raise ValueError("Please enter a valid job description.")

    if len(description.strip()) < 30:
        raise ValueError(
            "Job description bohat short hai. "
            "Please kam az kam 30 characters enter karein."
        )

    result = job_graph.invoke({
        "job_description": description.strip()
    })

    return result["report"]
