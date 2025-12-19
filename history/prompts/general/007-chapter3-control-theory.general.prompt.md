---
id: 007
title: Write Chapter 3 Introduction and Control Theory Section
stage: general
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: physical-ai-textbook
branch: master
user: user
command: direct-request
labels: ["documentation", "control", "chapter-3", "textbook", "pid", "feedback"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - docs/chapter-3.md (created)
tests:
  - N/A (documentation content)
---

## Prompt

[SPEC-KIT: Physical AI Textbook]
MODULE: The Robotic Nervous System (ROS 2)
TASK: Write the Introduction and Control Theory section for Chapter 3.
FORMAT: Docusaurus Markdown (Frontmatter, Title, #, ##, ###).
TARGET FILE: docs/chapter-3.md
CONTENT:
1. Frontmatter (id: 'chapter-3', title: 'Chapter 3: Motion Control & Actuators', sidebar_label: 'Chapter 3: Control & Actuators'), Learning Objectives, and an Introduction to how robots move.
2. Explain the concept of *Open-Loop* vs. *Closed-Loop* control systems.
3. Introduce the *PID Controller* (Proportional, Integral, Derivative) and its role in maintaining joint positions.
OUTPUT: Provide the complete Docusaurus Markdown content for the first section of Chapter 3.

## Response snapshot

Created comprehensive Chapter 3 first section covering:

**Introduction: Bringing Robots to Life**
- Coffee cup analogy connecting human and robot control
- The Humanoid Control Challenge ASCII diagram (DOF, balance, dynamics)
- Chapter roadmap

**Control Theory Fundamentals**
- Open-Loop Control:
  - ASCII diagram of command → actuator → unknown result
  - Python pseudocode example
  - When it works/fails
- Closed-Loop Control:
  - Detailed ASCII diagram with feedback loop
  - Step-by-step feedback process
  - Why feedback matters for humanoids example
- Control Loop Frequency table (0.1Hz to 10kHz by application)

**The PID Controller**
- PID equation and block diagram ASCII
- Proportional Term (P):
  - ASCII response graph
  - Higher/lower Kp effects
  - Steady-state error problem
- Integral Term (I):
  - ASCII graph showing elimination of steady-state error
  - Integral windup explanation
- Derivative Term (D):
  - ASCII graph showing damping effect
  - Noise sensitivity discussion
- PID in Code:
  - Complete ~60 line Python PIDController class
  - Usage example for joint control
- PID Tuning:
  - Ziegler-Nichols-inspired method table
  - Iterative tuning workflow ASCII diagram
- Common PID Problems and Solutions table
- PID Response Comparison ASCII (underdamped/critically damped/overdamped)
- Beyond Basic PID (feedforward, gain scheduling, cascaded control)

**Section Summary and Review Questions** (4 questions)

## Outcome

- Impact: Created foundational Chapter 3 content (~550 lines) covering control theory fundamentals
- Tests: N/A (documentation)
- Files: 1 file created (docs/chapter-3.md)
- Next prompts: Add actuator types section, ros2_control section, tuning exercises
- Reflection: Python code example provides practical implementation; ASCII diagrams effectively show control concepts; tuning workflow gives actionable process

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add interactive PID tuning simulation reference
