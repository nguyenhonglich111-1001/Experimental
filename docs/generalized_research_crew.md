# Generalized Research Crew

## Task Overview

This task involved refactoring the specialized genetic research CrewAI setup into a more generalized research crew capable of gathering, analyzing, and reviewing data on any given topic. The key changes include:

*   **Renamed Function:** `run_genetic_crew` was renamed to `run_research_crew`.
*   **Generalized Agents:** The `Genetic Research Specialist` was generalized to `Senior Research Specialist`, and the `Genetic Data Analyst` was generalized to `Research Analyst and Report Writer`.
*   **Added Agent:** A new `Quality Assurance Reviewer` agent was added to ensure accuracy, completeness, and clarity of the research output.
*   **Generalized Tasks:** Research and analysis tasks were updated to be topic-agnostic.
*   **Added Task:** A new `review_task` was introduced for the `Quality Assurance Reviewer` to review the analysis.
*   **Updated Crew:** The CrewAI definition was updated to include all three agents and their respective tasks in a sequential process.

## Todos

*   None at this time. The implementation is complete.