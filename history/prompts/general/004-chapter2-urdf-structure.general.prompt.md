---
id: 004
title: Write Chapter 2 Introduction and URDF Structure Section
stage: general
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: physical-ai-textbook
branch: master
user: user
command: direct-request
labels: ["documentation", "urdf", "chapter-2", "textbook", "links", "joints", "transmissions"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - docs/chapter-2.md (created)
tests:
  - N/A (documentation content)
---

## Prompt

[SPEC-KIT: Physical AI Textbook]
MODULE: The Robotic Nervous System (ROS 2)
TASK: Write the Introduction and URDF Structure section for Chapter 2.
FORMAT: Docusaurus Markdown (Frontmatter, Title, #, ##, ###).
TARGET FILE: docs/chapter-2.md
CONTENT:
1. Frontmatter (id: 'chapter-2', title: 'Chapter 2: Designing the Robot Body (URDF)', sidebar_label: 'Chapter 2: URDF & Dynamics'), Learning Objectives, and Introduction to URDF (Unified Robot Description Format).
2. Explain the role of *Links* (rigid body parts) and *Joints* (connections that allow motion) in a humanoid model.
3. Introduce *Transmissions* and how they link actuators to joints.
OUTPUT: Provide the complete Docusaurus Markdown content for the first section of Chapter 2.

## Response snapshot

Created comprehensive Chapter 2 first section covering:

**Introduction**
- Architecture drafting analogy for URDF
- Table showing humanoid complexity (60-80+ components)
- URDF file structure overview with XML example

**Links: The Rigid Bodies**
- Anatomy of a link (visual, collision, inertial)
- Visual properties: geometry options (box, cylinder, sphere, mesh), materials
- Collision properties: why they differ from visual, ASCII diagram comparison
- Multiple collision geometry strategy
- Inertial properties: center of mass, inertia tensor, formulas for primitives
- Base link example

**Joints: The Connections**
- Six joint types with ASCII diagram (fixed, revolute, continuous, prismatic, floating, planar)
- Joint anatomy: parent/child, origin, axis, limits, dynamics
- ASCII diagram of parent-child coordinate frames
- Axis configuration table
- Realistic joint limits table for humanoids
- Complete examples: shoulder (3 joints), elbow, fixed sensor mount

**Transmissions: Connecting Actuators to Joints**
- Why transmissions matter (gear reduction, belt drives, differentials, tendons)
- ASCII diagram of actuator-to-joint mapping types
- Transmission syntax with all elements explained
- Hardware interfaces table
- ros2_control flow diagram
- Examples: high-torque leg, direct-drive arm, position-controlled gripper

**Putting It Together**
- Complete 2-DOF arm URDF example (~100 lines)

**Section Summary and Review Questions** (4 questions)

## Outcome

- Impact: Created foundational Chapter 2 content (~650 lines) covering URDF structure in depth
- Tests: N/A (documentation)
- Files: 1 file created (docs/chapter-2.md)
- Next prompts: Add sensors/Gazebo plugins section, Xacro section, hands-on exercises
- Reflection: Heavy use of ASCII diagrams for visual learners; included complete working URDF example; connected to ros2_control for practical relevance

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add syntax highlighting for XML code blocks with `xml` language tag
