# Product Requirements — Nexus: AI-Powered Project Management SaaS

## Background
Nexus is a next-generation project management tool that uses AI to assist teams in planning,
tracking, and delivering software projects. This document outlines the requirements for the
initial release targeting software development teams of 5-50 people.

Note: Some requirements below are subject to change pending legal review of AI-generated content policies.

## 1. Workspace and Team Management

### 1.1 Organisations and Workspaces
The platform should support a multi-tenant architecture where each company has an isolated workspace.
Workspace administrators must be able to invite team members by email.
The system needs to handle cases where invited users don't already have accounts — the exact flow is TBD.
Role-based access control is required but the specific roles and permissions are still being defined with stakeholders.

### 1.2 Team Collaboration
Team members must be able to see each other's availability (online/offline/busy).
The platform should integrate with Slack — the exact scope of this integration is unclear at this stage.
Calendar integration is desired but may be out of scope for v1.

## 2. Project and Sprint Management

### 2.1 Projects
Users must be able to create projects with a name, description, and target completion date.
Each project must have a configurable workflow (the default workflow should be: Backlog → In Progress → In Review → Done).
Custom workflows should be supported but the UI for creating them has not been designed yet.

### 2.2 Tasks and Stories
Users must be able to create tasks/stories within a project.
Tasks must support: title, description, assignee, due date, priority (Low/Medium/High/Critical), story points, and labels.
There is a requirement from the product team for tasks to have sub-tasks but engineering has concerns about complexity — resolution pending.
Tasks must be linked to sprints.

### 2.3 Sprint Planning
The system must support fixed-length sprints (1 week, 2 weeks, or 4 weeks — configurable per project).
Sprint planning meetings should be facilitated by the platform — the exact mechanism is unclear.
Velocity tracking across sprints is required for the dashboard.

## 3. AI Features

### 3.1 AI Sprint Planning Assistant
The AI assistant must be able to suggest which tasks to include in a sprint based on team capacity and historical velocity.
The AI must never make decisions autonomously — all AI suggestions require explicit human approval before taking effect.
AI suggestions must include a confidence score and reasoning.
The AI model to use has not been finalised — candidates are GPT-4o and Claude Sonnet.

### 3.2 AI Task Breakdown
Users must be able to ask the AI to break a high-level task into subtasks.
The AI breakdown must be editable before saving.
There are open questions about whether AI-generated content should be watermarked or labelled.

### 3.3 Risk Detection
The system should proactively identify at-risk sprints (e.g. too many points, key assignee unavailable).
Alert thresholds are not yet defined — will require input from 3 pilot customers.

## 4. Reporting and Analytics

### 4.1 Burndown Charts
Each sprint must have a burndown chart showing remaining points vs time.
The chart must update in real-time as tasks are completed.
Export to PDF is required — the exact format has not been specified.

### 4.2 Team Velocity
The dashboard must show team velocity over the last N sprints (N is configurable, default 6).
Individual contributor velocity should be available but there are privacy concerns that need legal sign-off.

### 4.3 Project Health Score
Each project should have an AI-generated health score based on velocity, blockers, and deadline proximity.
The algorithm for calculating the health score has not been defined.
Health score history must be stored to show trends.

## 5. Integrations

### 5.1 GitHub Integration
The platform must integrate with GitHub to link commits and pull requests to tasks.
Automatically closing tasks when a linked PR is merged is desired but the exact conditions are TBD.
GitHub Actions integration for CI/CD status on tasks is mentioned in the roadmap but not confirmed for v1.

### 5.2 Communication
Email notifications are required for: task assignment, mention, due date approaching, sprint start/end.
Push notifications are desired for mobile but there is no mobile app in scope for v1 — this may apply to browser push notifications.

## 6. Non-Functional Requirements

### 6.1 Performance
The task board must render within 2 seconds for boards with up to 500 tasks.
Real-time updates (task status changes visible to all team members) must propagate within 500ms.
The platform must support at least 500 concurrent active users in the initial launch.
AI responses must be returned within 5 seconds — if exceeded, a timeout with retry option is shown.

### 6.2 Security and Compliance
All data must be encrypted at rest (AES-256) and in transit (TLS 1.3+).
The platform must be GDPR compliant — a full GDPR audit is planned for Q3 but specific requirements are pending.
SOC 2 Type II compliance is a goal for the end of year but not a launch requirement.
User data must never be used to train AI models without explicit opt-in consent.

### 6.3 Scalability
The architecture must support horizontal scaling to handle 10x current load without re-architecture.
Database queries on task boards must be optimised for boards with 1000+ tasks.

## 7. Technical Requirements

### 7.1 Backend
Django 5.1 with PostgreSQL 15+.
Django Channels with Redis for WebSocket real-time updates.
Celery with Redis for async task processing (notifications, AI jobs).
The AI integration layer must be model-agnostic to allow switching providers.

### 7.2 Infrastructure
Kubernetes deployment on AWS EKS.
Multi-region deployment is required but which regions has not been confirmed.
CI/CD pipeline via GitHub Actions — pipeline design TBD.

### 7.3 Data Retention
User data must be retained for a minimum of 3 years.
Deleted workspaces must have data retained for 90 days before permanent deletion (for recovery purposes).
Audit logs must be immutable and retained for 7 years.
