---
sidebar_position: 1
slug: /intro
title: Introduction
---

# Physical AI Textbook

Welcome to the **Physical AI Textbook** - a comprehensive open-source curriculum for mastering humanoid robotics with ROS 2, simulation, and AI.

## What is Physical AI?

Physical AI refers to artificial intelligence systems that interact with the physical world through embodied agents - robots that can perceive, reason, and act in real environments. Unlike purely digital AI, Physical AI must handle:

- **Real-time constraints** - Decisions must be made in milliseconds
- **Uncertainty** - Sensor noise, model errors, and unexpected obstacles
- **Safety** - Actions have real-world consequences
- **Physics** - Gravity, friction, and dynamics affect every movement

## Course Overview

This textbook is organized into four modules:

### Module I: The Robotic Nervous System

Build the foundational infrastructure that makes humanoid robots possible.

| Chapter | Topic | Key Concepts |
|---------|-------|--------------|
| 1 | ROS 2 Foundations | Nodes, topics, services, actions |
| 2 | URDF & Robot Modeling | Links, joints, physics properties |
| 3 | Motion Control | PID, trajectory planning, ros2_control |
| 4 | Simulation | Isaac Sim, digital twins, sim-to-real |

### Module II: Intelligence & Learning (Coming Soon)

Add perception, planning, and learning capabilities to your robots.

### Module III: Advanced Capabilities (Coming Soon)

Master manipulation, locomotion, and human-robot interaction.

### Module IV: Deployment & Scale (Coming Soon)

Deploy robots in production with safety, monitoring, and fleet management.

## Prerequisites

To get the most from this textbook, you should have:

- **Programming**: Familiarity with Python and basic C++
- **Linux**: Comfort with command-line operations
- **Math**: Linear algebra and calculus fundamentals
- **No robotics experience required** - We start from the basics

## Getting Started

Ready to begin? Start with [Chapter 1: ROS 2 Foundations](/docs/chapter-1-ros2-urdf-introduction) to learn the communication backbone of modern robotics.

```bash
# Example: Your first ROS 2 command
ros2 topic list
```

## Development Environment

We recommend the following setup:

- **OS**: Ubuntu 22.04 LTS
- **ROS**: ROS 2 Humble
- **Simulation**: NVIDIA Isaac Sim 2023.1+
- **GPU**: NVIDIA RTX series (for simulation)

## Contributing

This is an open-source curriculum. Contributions, corrections, and improvements are welcome on [GitHub](https://github.com/hackathon-physical-ai/humanoid-textbook).

---

Let's build the future of robotics together.
