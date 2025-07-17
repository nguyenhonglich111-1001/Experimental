# Experiment: AI-Powered Testing with Octomind

This document details the process and findings of using Octomind, an AI-powered test automation tool, on a sample web application.

## Phase 1: The "Smart Notes" Web Application

To have a target for our testing experiment, a simple "Smart Notes" web application was developed.

### Application Overview

The "Smart Notes" app is a single-page application that allows users to perform CRUD (Create, Read, Update, Delete) operations on notes. It also includes an AI-powered feature to summarize note content using the Google Gemini API.

### Tech Stack

-   **Backend:** Flask (Python)
-   **Frontend:** HTML, Bootstrap, JavaScript
-   **AI Integration:** Google Gemini API for summarization
-   **Database:** A simple `db.json` file for storing notes.

### Features

-   Create, edit, and delete notes.
-   View all notes in a card-based layout.
-   Click a "Summarize" button to get an AI-generated summary of any note.
-   Responsive design using Bootstrap.

## Phase 2: Integrating Octomind (To Be Done)

The next phase of this experiment will involve:

1.  Setting up an Octomind account.
2.  Pointing Octomind to the running "Smart Notes" application.
3.  Allowing Octomind to automatically generate a suite of Playwright tests.
4.  Reviewing the generated tests for coverage and accuracy.
5.  Intentionally introducing a bug to test Octomind's failure detection and reporting.

## Phase 3: Findings and Conclusion (To Be Done)

This section will be updated with the results and conclusions of the experiment.
