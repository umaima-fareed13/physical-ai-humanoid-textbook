---
id: chapter-3
title: 'Chapter 3: Motion Control & Actuators'
sidebar_label: 'Chapter 3: Control & Actuators'
sidebar_position: 4
---

# Chapter 3: Motion Control & Actuators

## Learning Objectives

By the end of this chapter, you will be able to:

- **Distinguish** between open-loop and closed-loop control systems
- **Explain** the components of a PID controller and their individual effects
- **Tune** PID gains to achieve stable, responsive joint control
- **Identify** common actuator types used in humanoid robots
- **Describe** the relationship between actuators, transmissions, and joint motion
- **Implement** basic position and velocity controllers in ROS 2

---

## Introduction: Bringing Robots to Life

In Chapter 2, we learned to describe a robot's physical structure using URDF—its links, joints, and physical properties. But a URDF file is just a blueprint. To make a robot move, we need **control systems** that command actuators to produce motion and **feedback mechanisms** that ensure the robot does what we intend.

Consider what happens when you decide to pick up a coffee cup:

1. Your brain plans the motion (trajectory planning)
2. Motor neurons send signals to arm muscles (actuation commands)
3. Muscles contract, moving bones through joints (physical motion)
4. Sensory neurons report position and force (feedback)
5. Your brain adjusts commands based on feedback (closed-loop control)

This entire loop happens continuously, dozens of times per second, without conscious thought. Humanoid robots must replicate this cycle artificially—and that's the domain of **motion control**.

### The Control Challenge

Humanoid robot control is exceptionally difficult:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE HUMANOID CONTROL CHALLENGE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DEGREES OF FREEDOM                                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  Industrial arm: 6 DOF          Humanoid: 30-50+ DOF           │   │
│   │  ○─○─○─○─○─○─◇                   Head, torso, 2 arms,          │   │
│   │                                  2 legs, 2 hands = complexity   │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   BALANCE                                                               │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  Fixed base: stable             Humanoid: constantly falling   │   │
│   │  ┌───┐                          ┌───┐                          │   │
│   │  │   │ ← bolted down            │   │ ← must actively balance  │   │
│   │  └─┬─┘                          └─┬─┘                          │   │
│   │  ══╧══                            ╱╲                            │   │
│   │                                  ╱  ╲ ← small support polygon  │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   DYNAMICS                                                              │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  Static environment            Dynamic environment              │   │
│   │  Robot alone                   Robot + gravity + contacts +    │   │
│   │                                external forces + humans        │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Despite this complexity, we start with fundamentals that apply universally: **how to make a single joint go where we want it to go**.

### Chapter Roadmap

We'll build understanding from the ground up:

1. **Control Theory Basics**: Open-loop vs closed-loop, why feedback matters
2. **PID Control**: The workhorse algorithm for joint control
3. **Actuator Types**: Motors, hydraulics, and emerging technologies
4. **ros2_control**: ROS 2's framework for real-time control
5. **Tuning and Troubleshooting**: Making controllers work in practice

---

## Control Theory Fundamentals

Before diving into specific algorithms, we need to understand the fundamental distinction in control systems: **open-loop** versus **closed-loop** control.

### Open-Loop Control: Command and Hope

In **open-loop control**, commands are sent to actuators without any feedback about what actually happens. The system assumes the command will be executed perfectly.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       OPEN-LOOP CONTROL                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐   │
│   │   Desired    │         │              │         │    Actual    │   │
│   │   Position   │────────►│   Actuator   │────────►│   Position   │   │
│   │   (command)  │         │              │         │   (unknown)  │   │
│   └──────────────┘         └──────────────┘         └──────────────┘   │
│                                                                         │
│   Example: "Move motor 1000 steps"                                      │
│                                                                         │
│   Problems:                                                             │
│   • No way to know if motor actually moved 1000 steps                  │
│   • External forces (gravity, friction) cause errors                   │
│   • Errors accumulate over time                                        │
│   • No correction possible                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Real-world example**: A stepper motor commanded to move 90 degrees.

```python
# Open-loop control (pseudocode)
def move_joint_open_loop(target_angle):
    steps_needed = angle_to_steps(target_angle)
    for i in range(steps_needed):
        send_step_pulse()
        wait(step_period)
    # Done! ...but did it actually get there?
```

**When open-loop works:**
- Low-precision applications (rough positioning)
- Well-characterized systems with negligible disturbances
- Stepper motors with known loads and no slip

**When open-loop fails:**
- Any external force disturbs the system
- The actuator characteristics change (heating, wear)
- Precision matters
- **Almost all humanoid robot applications**

### Closed-Loop Control: Measure and Correct

In **closed-loop control** (also called **feedback control**), sensors measure the actual system state, and the controller adjusts commands based on the difference between desired and actual states.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CLOSED-LOOP CONTROL                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                              error = desired - actual                   │
│                                        │                                │
│   ┌──────────────┐    ┌────────────────▼───────────────┐               │
│   │   Desired    │    │                                │               │
│   │   Position   │───►│(+)         Controller          │               │
│   │   (setpoint) │    │ ○──────────────────────────────┼──┐            │
│   └──────────────┘    │(-)                             │  │            │
│                       └────────────────────────────────┘  │            │
│                              │                            │            │
│                              │ command                    │            │
│                              ▼                            │            │
│                       ┌──────────────┐                    │            │
│                       │              │                    │            │
│                       │   Actuator   │                    │            │
│                       │              │                    │            │
│                       └──────┬───────┘                    │            │
│                              │                            │            │
│                              │ motion                     │            │
│                              ▼                            │            │
│                       ┌──────────────┐                    │            │
│                       │    Plant     │                    │            │
│                       │   (robot     │                    │            │
│                       │    joint)    │                    │            │
│                       └──────┬───────┘                    │            │
│                              │                            │            │
│                              │ actual position            │            │
│                              ▼                            │            │
│                       ┌──────────────┐                    │            │
│                       │    Sensor    │────────────────────┘            │
│                       │  (encoder)   │        feedback                 │
│                       └──────────────┘                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**The feedback loop:**

1. **Setpoint**: The desired state (e.g., joint angle = 45°)
2. **Error**: Difference between setpoint and actual state
3. **Controller**: Algorithm that computes actuator command from error
4. **Actuator**: Device that produces motion (motor)
5. **Plant**: The physical system being controlled (robot joint)
6. **Sensor**: Measures actual state (encoder)
7. **Repeat**: Continuously at high frequency (100Hz - 10kHz)

**Key insight**: Closed-loop control doesn't need a perfect model of the system. It measures reality and corrects errors, making it robust to disturbances and model inaccuracies.

### Why Feedback Matters for Humanoids

Consider a humanoid robot arm holding a 2kg object:

**Without feedback (open-loop):**
```
Command: "Elbow angle = 90°"
Reality: Gravity pulls arm down
Result: Arm droops to 70°
Problem: No way to detect or correct this
```

**With feedback (closed-loop):**
```
Command: "Elbow angle = 90°"
Sensor reads: 85° (gravity is winning)
Controller: "Error is 5°, increase motor torque"
Motor torque increases
Sensor reads: 88°
Controller: "Error is 2°, increase a bit more"
...continues until error ≈ 0
```

The feedback loop continuously fights against gravity, friction, and any other disturbances to maintain the desired position.

### Control Loop Frequency

The speed of the feedback loop is critical:

| Application | Typical Frequency | Why |
|-------------|-------------------|-----|
| Temperature control | 0.1 - 1 Hz | Slow thermal dynamics |
| Mobile robot navigation | 10 - 50 Hz | Moderate speed motion |
| Robot arm position | 100 - 500 Hz | Fast, precise motion |
| Force/torque control | 1 - 10 kHz | Very fast dynamics |
| Balancing humanoid | 200 Hz - 1 kHz | Unstable, fast correction needed |

**Rule of thumb**: The control loop should be 10-100× faster than the fastest dynamics you need to control.

For humanoid robots, joint position control typically runs at **500-1000 Hz**, while higher-level behaviors (walking patterns) run at **100-200 Hz**.

---

## The PID Controller

The **PID controller** is the most widely used feedback control algorithm in robotics and industrial automation. Despite its simplicity, it's remarkably effective for joint-level control.

### What is PID?

PID stands for **Proportional-Integral-Derivative**—three terms that each contribute to the control output:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PID CONTROLLER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   error(t) = setpoint - measured_value                                  │
│                                                                         │
│   output = Kp × error      ← Proportional: react to current error      │
│          + Ki × ∫error dt  ← Integral: eliminate steady-state error    │
│          + Kd × d(error)/dt ← Derivative: dampen oscillations          │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │                    ┌────────────────┐                           │   │
│   │              ┌────►│  Proportional  │────┐                      │   │
│   │              │     │    Kp × e      │    │                      │   │
│   │              │     └────────────────┘    │                      │   │
│   │              │                           │                      │   │
│   │   error  ────┼────►┌────────────────┐    │                      │   │
│   │     e        │     │    Integral    │────┼────► output          │   │
│   │              │     │   Ki × ∫e dt   │    │         u            │   │
│   │              │     └────────────────┘    │                      │   │
│   │              │                           │                      │   │
│   │              │     ┌────────────────┐    │                      │   │
│   │              └────►│   Derivative   │────┘                      │   │
│   │                    │   Kd × de/dt   │                           │   │
│   │                    └────────────────┘                           │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Proportional Term (P)

The proportional term produces an output **proportional to the current error**:

```
P_output = Kp × error
```

**Intuition**: The further you are from the target, the harder you push.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PROPORTIONAL CONTROL                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Position                                                              │
│      ▲                                                                  │
│      │     setpoint ─────────────────────────────────────              │
│      │                        ╱──────────────────                      │
│      │                      ╱                                          │
│      │                    ╱    response with Kp                        │
│      │                  ╱                                              │
│      │                ╱                                                │
│      │              ╱                                                  │
│      │            ╱                                                    │
│      │──────────╱                                                      │
│      │        start                                                    │
│      └─────────────────────────────────────────────────────────► Time  │
│                                                                         │
│   • Large error → large output (fast initial response)                 │
│   • Small error → small output (slows as approaching target)           │
│   • Problem: May never reach setpoint (steady-state error)             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Higher Kp**:
- Faster response
- Smaller steady-state error
- But: Can cause oscillation and instability

**Lower Kp**:
- Slower response
- Larger steady-state error
- But: More stable, less oscillation

**The steady-state error problem**: With P-only control, when the error becomes small, the output becomes small—possibly too small to overcome friction or gravity. The system settles with some remaining error.

### The Integral Term (I)

The integral term accumulates error over time:

```
I_output = Ki × ∫error dt
```

**Intuition**: If you've been off-target for a while, push harder.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       INTEGRAL CONTROL                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Position                                                              │
│      ▲                                                                  │
│      │     setpoint ─────────────────────────────────────              │
│      │                              ════════════════════ ← with I      │
│      │                        ────────────────────────── ← P only      │
│      │                      ╱            (steady-state error)          │
│      │                    ╱                                            │
│      │                  ╱                                              │
│      │                ╱                                                │
│      │              ╱                                                  │
│      │            ╱                                                    │
│      │──────────╱                                                      │
│      └─────────────────────────────────────────────────────────► Time  │
│                                                                         │
│   • Accumulates error over time                                        │
│   • Eventually eliminates steady-state error                           │
│   • Problem: Can cause overshoot and oscillation (integral windup)     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**The integral eliminates steady-state error** because even a tiny persistent error will accumulate until the output is large enough to correct it.

**Higher Ki**:
- Faster elimination of steady-state error
- But: More overshoot, potential instability

**Lower Ki**:
- Slower correction of steady-state error
- But: Less overshoot, more stable

**Integral windup**: If the actuator saturates (reaches maximum output) while error persists, the integral term keeps growing. When the error finally reverses, the accumulated integral causes massive overshoot. Solutions include integral clamping and anti-windup schemes.

### The Derivative Term (D)

The derivative term responds to the **rate of change** of error:

```
D_output = Kd × d(error)/dt
```

**Intuition**: If you're approaching the target quickly, start braking.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DERIVATIVE CONTROL                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Position                                                              │
│      ▲                                                                  │
│      │     setpoint ─────────────────────────────────────              │
│      │                    ╭──╮                                         │
│      │                   ╱    ╲     ← overshoot without D              │
│      │                  ╱      ────────────────────────                │
│      │                 ╱                                               │
│      │                ╱ ─────────────────────────────── ← with D       │
│      │               ╱                    (damped)                     │
│      │              ╱                                                  │
│      │            ╱                                                    │
│      │──────────╱                                                      │
│      └─────────────────────────────────────────────────────────► Time  │
│                                                                         │
│   • Reacts to how fast error is changing                               │
│   • Provides "braking" as system approaches setpoint                   │
│   • Dampens oscillations                                               │
│   • Problem: Amplifies high-frequency noise                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Higher Kd**:
- More damping, less overshoot
- But: Amplifies sensor noise, can cause jitter

**Lower Kd**:
- Less noise sensitivity
- But: More overshoot, slower settling

**Noise sensitivity**: Since derivative measures rate of change, noisy sensors create noisy derivatives. A common solution is filtering the derivative term or computing derivative on the measurement rather than the error.

### PID in Code

Here's a discrete-time PID implementation suitable for robot control:

```python
class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, dt: float):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            dt: Control loop period (seconds)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt

        # State variables
        self.integral = 0.0
        self.previous_error = 0.0

        # Anti-windup limits
        self.integral_min = -100.0
        self.integral_max = 100.0

    def compute(self, setpoint: float, measured: float) -> float:
        """
        Compute PID output.

        Args:
            setpoint: Desired value
            measured: Current measured value

        Returns:
            Control output (e.g., motor torque command)
        """
        # Calculate error
        error = setpoint - measured

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * self.dt
        self.integral = max(self.integral_min,
                          min(self.integral_max, self.integral))
        i_term = self.ki * self.integral

        # Derivative term (on error)
        derivative = (error - self.previous_error) / self.dt
        d_term = self.kd * derivative

        # Store for next iteration
        self.previous_error = error

        # Total output
        output = p_term + i_term + d_term

        return output

    def reset(self):
        """Reset controller state (call when setpoint changes significantly)."""
        self.integral = 0.0
        self.previous_error = 0.0
```

**Usage for joint position control:**

```python
# Create controller for elbow joint
elbow_pid = PIDController(kp=100.0, ki=10.0, kd=5.0, dt=0.001)  # 1kHz

# Control loop (runs at 1kHz)
def control_loop():
    while running:
        # Read desired position from trajectory
        desired_angle = trajectory.get_position(current_time)

        # Read actual position from encoder
        actual_angle = encoder.read_position()

        # Compute control output
        torque_command = elbow_pid.compute(desired_angle, actual_angle)

        # Send to motor
        motor.set_torque(torque_command)

        # Wait for next control cycle
        sleep(0.001)  # 1ms = 1kHz
```

### PID Tuning

Choosing the right Kp, Ki, and Kd values is both art and science. Here's a systematic approach:

**Manual Tuning (Ziegler-Nichols-inspired):**

1. **Set Ki = 0, Kd = 0** (P-only control)
2. **Increase Kp** until the system oscillates continuously (this is Ku, the "ultimate gain")
3. **Measure oscillation period** Tu
4. **Apply tuning rules:**

| Controller | Kp | Ki | Kd |
|------------|-----|-----|-----|
| P only | 0.5 × Ku | 0 | 0 |
| PI | 0.45 × Ku | 0.54 × Ku / Tu | 0 |
| PID | 0.6 × Ku | 1.2 × Ku / Tu | 0.075 × Ku × Tu |

**Iterative tuning process:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       PID TUNING WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   START: Kp=0, Ki=0, Kd=0                                              │
│      │                                                                  │
│      ▼                                                                  │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ Step 1: Increase Kp until response is fast but oscillating  │     │
│   └──────────────────────────────────────────────────────────────┘     │
│      │                                                                  │
│      ▼                                                                  │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ Step 2: Add Kd to dampen oscillations                        │     │
│   └──────────────────────────────────────────────────────────────┘     │
│      │                                                                  │
│      ▼                                                                  │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ Step 3: Add Ki to eliminate steady-state error               │     │
│   └──────────────────────────────────────────────────────────────┘     │
│      │                                                                  │
│      ▼                                                                  │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ Step 4: Fine-tune all three, test under various conditions   │     │
│   └──────────────────────────────────────────────────────────────┘     │
│      │                                                                  │
│      ▼                                                                  │
│   DONE: Record final gains for this joint/load combination             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Common PID Problems and Solutions

| Problem | Symptom | Likely Cause | Solution |
|---------|---------|--------------|----------|
| **Oscillation** | Position swings around setpoint | Kp too high | Reduce Kp, increase Kd |
| **Sluggish response** | Slow to reach setpoint | Kp too low | Increase Kp |
| **Steady-state error** | Never quite reaches setpoint | Ki too low or zero | Increase Ki |
| **Overshoot** | Exceeds setpoint before settling | Kd too low, Ki too high | Increase Kd, reduce Ki |
| **Jitter/noise** | Output chatters rapidly | Kd too high, noisy sensor | Reduce Kd, filter measurement |
| **Windup** | Huge overshoot after saturation | No anti-windup | Add integral clamping |

### Visualizing PID Response

Different gain combinations produce characteristic responses:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PID RESPONSE COMPARISON                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Position                                                              │
│      ▲                                                                  │
│      │     setpoint ─────────────────────────────────────              │
│      │            ╭─╮                                                  │
│      │           ╱   ╲    ╭─╮                                          │
│      │          ╱     ╲  ╱   ╲        Underdamped (low Kd)            │
│      │         ╱       ╲╱     ╲──────                                  │
│      │        ╱                                                        │
│      │       ╱ ────────────────────── Critically damped (optimal)     │
│      │      ╱                                                          │
│      │     ╱                                                           │
│      │    ╱    ╱─────────────────────  Overdamped (high Kd)           │
│      │   ╱   ╱                                                         │
│      │──╱──╱                                                           │
│      └─────────────────────────────────────────────────────────► Time  │
│                                                                         │
│   GOAL: Critically damped or slightly underdamped                      │
│         - Fast response                                                │
│         - Minimal overshoot                                            │
│         - No steady-state error                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Beyond Basic PID

While PID works well for many joint control applications, humanoid robots often require more sophisticated approaches:

**Feedforward compensation:**
```python
# Add feedforward for gravity compensation
gravity_torque = compute_gravity_compensation(joint_angles)
pid_torque = pid.compute(setpoint, measured)
total_torque = pid_torque + gravity_torque
```

**Gain scheduling:**
```python
# Adjust gains based on operating condition
if load_mass > 2.0:
    pid.kp = high_load_kp
    pid.ki = high_load_ki
else:
    pid.kp = normal_kp
    pid.ki = normal_ki
```

**Cascaded control:**
```
Position PID → Velocity setpoint → Velocity PID → Torque command
```

We'll explore these advanced techniques later in this chapter and in subsequent chapters on whole-body control.

---

## Section Summary

In this section, we established the foundations of robot motion control:

**Open-Loop vs Closed-Loop:**
- Open-loop sends commands without feedback—simple but unreliable
- Closed-loop measures actual state and corrects errors—essential for precise robotics
- Humanoid robots require closed-loop control for every joint

**The Feedback Loop:**
- Setpoint (desired) → Error calculation → Controller → Actuator → Plant → Sensor → back to error
- Must run at high frequency (100Hz-1kHz for position control)
- Continuous correction handles disturbances like gravity and friction

**PID Control:**
- **Proportional (P)**: Reacts to current error—provides main driving force
- **Integral (I)**: Accumulates past error—eliminates steady-state offset
- **Derivative (D)**: Reacts to error rate of change—dampens oscillations
- Combined: `output = Kp×e + Ki×∫e dt + Kd×de/dt`

**PID Tuning:**
- Start with P-only, add D for damping, add I for zero steady-state error
- Trade-offs: speed vs stability, precision vs noise sensitivity
- Different joints may need different gains

In the next section, we'll explore the actuators that convert control signals into physical motion—the muscles of our robotic nervous system.

---

## Section Review Questions

1. A robot arm is commanded to move to 45° but settles at 43° and stays there. Is this more likely an open-loop or closed-loop system? If closed-loop, which PID term would you adjust to fix this?

2. Explain why a humanoid robot's knee joint might need different PID gains when standing versus when swinging during walking.

3. You increase Kp and the system starts oscillating. What are two different changes you could make to stabilize it while maintaining fast response?

4. Why might a PID controller with high Kd cause problems when using a low-resolution encoder? What practical solution would you implement?

---

## Actuators: The Muscles of Robots

Actuators convert electrical energy into mechanical motion. They are the "muscles" that bring our carefully designed URDF models to life. For humanoid robots, actuator selection profoundly impacts performance—the difference between a robot that walks gracefully and one that stumbles.

### Actuator Requirements for Humanoids

Humanoid robots demand exceptional actuator performance:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 HUMANOID ACTUATOR REQUIREMENTS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│   │   HIGH TORQUE   │  │   LOW WEIGHT    │  │  BACKDRIVABLE   │        │
│   │                 │  │                 │  │                 │        │
│   │   Support body  │  │  Every gram     │  │  Safe human     │        │
│   │   weight, lift  │  │  counts at      │  │  interaction,   │        │
│   │   objects       │  │  extremities    │  │  impact absorp. │        │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│   │   HIGH SPEED    │  │  PRECISE CTRL   │  │   EFFICIENT     │        │
│   │                 │  │                 │  │                 │        │
│   │   Dynamic       │  │  Sub-degree     │  │  Long battery   │        │
│   │   motions,      │  │  positioning,   │  │  life, low      │        │
│   │   fast reflexes │  │  smooth motion  │  │  heat           │        │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
│   Trade-offs are inevitable: high torque often means heavy,            │
│   high speed often means low torque, efficiency vs performance...      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### DC Motors (Brushed)

The simplest electric motor: current through a coil creates a magnetic field that interacts with permanent magnets to produce rotation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BRUSHED DC MOTOR                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                    ┌───────────────────┐                               │
│                    │    Permanent      │                               │
│                    │    Magnets        │                               │
│          ┌─────────┤   ┌───────┐       ├─────────┐                     │
│          │ N       │   │ Rotor │       │       S │                     │
│          │         │   │ Coil  │       │         │                     │
│          │         │   │   ↻   │       │         │                     │
│          │         │   └───────┘       │         │                     │
│          └─────────┤    Brushes        ├─────────┘                     │
│                    │    ═══════        │                               │
│                    │   Commutator      │                               │
│                    └───────────────────┘                               │
│                                                                         │
│   ⊕ Simple, inexpensive, easy to control                               │
│   ⊕ Linear torque-speed relationship                                   │
│   ⊖ Brushes wear out, create electrical noise                          │
│   ⊖ Lower efficiency (brush friction)                                  │
│   ⊖ Limited speed (brush bounce)                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Property | Typical Value | Notes |
|----------|---------------|-------|
| Efficiency | 60-75% | Brush friction losses |
| Torque density | Low-Medium | Limited by thermal issues |
| Speed range | 0-10,000 RPM | Brush limits max speed |
| Control complexity | Simple | Voltage = speed, current = torque |
| Maintenance | Periodic | Brush replacement needed |

**Humanoid applications**: Rarely used in modern humanoids due to brush wear and limited performance, but may appear in simple grippers or educational platforms.

### BLDC Motors (Brushless DC)

Brushless motors eliminate mechanical commutation by using electronic switching. The magnets are on the rotor, coils on the stator.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BRUSHLESS DC MOTOR                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                    ┌───────────────────┐                               │
│                    │   Stator Coils    │                               │
│                    │   A    B    C     │                               │
│          ┌─────────┤  ╲   │   ╱        ├─────────┐                     │
│          │ Coil A  │   ╲  │  ╱         │  Coil C │                     │
│          │         │    ╲ │ ╱          │         │                     │
│          │    ●────┼─────●─────────────┼────●    │                     │
│          │         │    ╱ │ ╲          │         │                     │
│          │ Coil B  │   ╱  │  ╲         │         │                     │
│          └─────────┤  ╱   │   ╲        ├─────────┘                     │
│                    │   Permanent       │                               │
│                    │   Magnet Rotor    │                               │
│                    └───────────────────┘                               │
│                             │                                          │
│                    ┌────────▼────────┐                                 │
│                    │  Motor Driver   │  ← Electronic commutation       │
│                    │  (3-phase PWM)  │                                 │
│                    └─────────────────┘                                 │
│                                                                         │
│   ⊕ High efficiency (85-95%)                                           │
│   ⊕ No brush wear, long life                                           │
│   ⊕ High speed capability                                              │
│   ⊕ Excellent torque-to-weight ratio                                   │
│   ⊖ Requires electronic commutation (motor driver)                     │
│   ⊖ More complex control                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Property | Typical Value | Notes |
|----------|---------------|-------|
| Efficiency | 85-95% | No brush losses |
| Torque density | Medium-High | Depends on design |
| Speed range | 0-100,000 RPM | No mechanical limits |
| Control complexity | Medium | Requires driver/encoder |
| Maintenance | Minimal | Bearings only |

**Why BLDC dominates modern robotics:**

The advantages of BLDC motors make them the default choice for robotic joints:

- **Efficiency**: Less heat, longer battery life
- **Reliability**: No brushes to wear out
- **Performance**: Higher speeds, better torque density
- **Precision**: Smooth commutation enables precise control

**Humanoid applications**: Arms, legs, hands—virtually every joint in modern humanoids uses some form of BLDC motor.

### Quasi-Direct Drive (QDD) Actuators

Traditional robot joints use high gear ratios (100:1 to 200:1) to amplify motor torque. This creates high output torque but sacrifices **backdrivability**—the ability for external forces to move the joint.

**Quasi-Direct Drive** actuators use low gear ratios (typically 6:1 to 10:1), preserving backdrivability while still providing useful torque amplification.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QUASI-DIRECT DRIVE (QDD)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   TRADITIONAL HIGH-RATIO              QUASI-DIRECT DRIVE                │
│   ┌─────────────────────┐             ┌─────────────────────┐          │
│   │                     │             │                     │          │
│   │  ┌───┐    ┌─────┐   │             │  ┌───┐    ┌─────┐   │          │
│   │  │ M │───►│100:1│───┼──► Joint    │  │ M │───►│ 8:1 │───┼──► Joint │
│   │  └───┘    │Gear │   │             │  └───┘    │Gear │   │          │
│   │           └─────┘   │             │  (larger) └─────┘   │          │
│   │                     │             │                     │          │
│   └─────────────────────┘             └─────────────────────┘          │
│                                                                         │
│   Torque: 0.5 Nm × 100 = 50 Nm       Torque: 5 Nm × 8 = 40 Nm         │
│   Backdrivable: NO                    Backdrivable: YES                │
│   Reflected inertia: HIGH             Reflected inertia: LOW           │
│   Impact response: RIGID              Impact response: COMPLIANT       │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  WHY BACKDRIVABILITY MATTERS FOR HUMANOIDS                      │  │
│   ├─────────────────────────────────────────────────────────────────┤  │
│   │  • Safe human interaction (robot gives way on contact)          │  │
│   │  • Impact absorption (falling doesn't break gearbox)            │  │
│   │  • Force sensing through motor current (no separate sensor)     │  │
│   │  • Natural compliance for walking/manipulation                  │  │
│   │  • Energy efficient (can use gravity, store energy in motion)   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key QDD characteristics:**

| Property | Traditional (100:1) | QDD (8:1) |
|----------|---------------------|-----------|
| Output torque | Very high | Moderate |
| Backdrivability | Poor | Excellent |
| Reflected inertia | High | Low |
| Bandwidth | Limited | High |
| Force sensing | Requires sensor | Via current |
| Efficiency | 60-80% | 85-95% |

**Modern QDD actuator designs:**

Leading humanoid robots use custom QDD actuators:

- **MIT Cheetah**: Pioneered QDD for legged robots
- **Boston Dynamics**: Proprietary high-performance QDD
- **Unitree**: Commercial QDD actuators for quadrupeds/humanoids
- **Tesla Optimus**: Custom linear and rotary QDD actuators

### Actuator Comparison for Humanoid Joints

Different joints have different requirements. Here's a typical allocation:

| Joint | Requirement | Preferred Actuator |
|-------|-------------|-------------------|
| Hip (stance) | High torque, backdrivable | QDD |
| Knee | High torque, fast motion | QDD |
| Ankle | Moderate torque, compliance | QDD |
| Shoulder | Moderate torque, backdrivable | QDD or geared BLDC |
| Elbow | Moderate torque, precision | Geared BLDC or QDD |
| Wrist | Low torque, high precision | Geared BLDC |
| Fingers | Low torque, compact | Small BLDC or tendon |

### Emerging Actuator Technologies

The field continues to evolve:

- **Series Elastic Actuators (SEA)**: Spring between motor and joint provides compliance and energy storage
- **Hydraulic actuators**: Highest power density (Boston Dynamics Atlas)
- **Artificial muscles**: Pneumatic, shape-memory alloys, electroactive polymers
- **Magnetic gears**: Contactless torque transmission, inherent compliance

---

## ros2_control: Bridging Software and Hardware

Knowing how to design a PID controller and select actuators is only part of the picture. We need a framework to connect high-level motion commands to low-level hardware. In ROS 2, this framework is **ros2_control**.

### The Control Problem in ROS 2

Consider the challenge:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE INTEGRATION CHALLENGE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   HIGH-LEVEL                                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  MoveIt Motion Planner: "Move arm to grasp position"            │  │
│   │  Navigation: "Walk to waypoint"                                 │  │
│   │  Behavior Trees: "Pick up object"                               │  │
│   └────────────────────────────┬────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│   MID-LEVEL                    ?                                        │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  How do we translate trajectories to joint commands?            │  │
│   │  How do we run control loops at 1kHz while ROS runs at 100Hz?   │  │
│   │  How do we support different hardware (sim, real, different     │  │
│   │  motor drivers) with the same code?                             │  │
│   └────────────────────────────┬────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│   LOW-LEVEL                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  Motor drivers: PWM signals, current commands                   │  │
│   │  Encoders: Position/velocity readings                           │  │
│   │  Force sensors: Contact forces                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**ros2_control** solves this by providing:

1. A standardized interface between controllers and hardware
2. Real-time capable execution
3. Hardware abstraction for portability
4. A library of common controllers

### ros2_control Architecture

The ros2_control framework consists of three main components:

1. **Controller Manager**
2. **Resource Manager**
3. **Hardware Interfaces**

Here is the detailed breakdown of each component:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ros2_control ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    CONTROLLER MANAGER                           │  │
│   │  • Loads, configures, starts/stops controllers                  │  │
│   │  • Manages controller lifecycle                                 │  │
│   │  • Runs the real-time control loop                              │  │
│   │  • Coordinates access to hardware resources                     │  │
│   └───────────────────────────┬─────────────────────────────────────┘  │
│                               │                                         │
│   ┌───────────────────────────▼─────────────────────────────────────┐  │
│   │                    RESOURCE MANAGER                             │  │
│   │  • Owns all hardware interface instances                        │  │
│   │  • Manages state (command/state) interfaces                     │  │
│   │  • Handles resource claiming (which controller owns which joint)│  │
│   │  • Provides hardware abstraction                                │  │
│   └───────────────────────────┬─────────────────────────────────────┘  │
│                               │                                         │
│   ┌───────────────────────────▼─────────────────────────────────────┐  │
│   │                   HARDWARE INTERFACES                           │  │
│   │  • Actual communication with motors, encoders, sensors          │  │
│   │  • Implements read() and write() for specific hardware          │  │
│   │  • Can be real hardware OR simulation                           │  │
│   │  • Loaded based on URDF <ros2_control> tags                     │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Three Main Components of ros2_control

#### 1. Controller Manager

The **Controller Manager** is the central coordinator:

- **Loads controllers** as plugins based on configuration
- **Manages lifecycle**: configure → activate → deactivate → cleanup
- **Executes the real-time loop** that calls controllers at fixed frequency
- **Handles controller switching**: seamlessly transition between controllers

```yaml
# Example controller_manager configuration
controller_manager:
  ros__parameters:
    update_rate: 500  # Hz - the real-time loop frequency

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    gripper_controller:
      type: position_controllers/GripperActionController
```

#### 2. Resource Manager

The **Resource Manager** handles hardware abstraction:

- **Owns hardware interfaces** loaded from URDF
- **Manages state interfaces** (reading sensor data)
- **Manages command interfaces** (sending actuator commands)
- **Handles resource claiming** (prevents two controllers from commanding same joint)

**Interface types:**

| Interface Type | Direction | Examples |
|----------------|-----------|----------|
| State | Hardware → Controller | position, velocity, effort, temperature |
| Command | Controller → Hardware | position, velocity, effort |

#### 3. Hardware Interfaces

**Hardware Interfaces** are the drivers that talk to actual hardware:

- **Implement the `SystemInterface` class** (or `ActuatorInterface`, `SensorInterface`)
- **`read()` method**: Get current state from hardware (encoders, sensors)
- **`write()` method**: Send commands to hardware (motor drivers)
- **Can represent real hardware or simulation**

```cpp
// Simplified hardware interface structure
class MyRobotHardware : public hardware_interface::SystemInterface
{
public:
  // Called once at startup
  CallbackReturn on_init(const HardwareInfo& info) override;

  // Called every control cycle to read sensors
  return_type read(const rclcpp::Time& time, const rclcpp::Duration& period) override;

  // Called every control cycle to write commands
  return_type write(const rclcpp::Time& time, const rclcpp::Duration& period) override;

private:
  std::vector<double> joint_positions_;
  std::vector<double> joint_velocities_;
  std::vector<double> joint_commands_;
};
```

### How ros2_control Works: The Control Loop

Here's what happens every control cycle (e.g., every 2ms at 500Hz):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ros2_control EXECUTION CYCLE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Time ──────────────────────────────────────────────────────────────►  │
│                                                                         │
│   │◄────────────── One control cycle (2ms @ 500Hz) ──────────────►│    │
│   │                                                                │    │
│   │  ┌──────────┐  ┌──────────────────┐  ┌──────────┐             │    │
│   │  │  READ    │  │    CONTROLLERS   │  │  WRITE   │             │    │
│   │  │          │  │                  │  │          │             │    │
│   │  │ Hardware │  │ JointTrajectory  │  │ Hardware │             │    │
│   │  │ reads    │─►│ PID computes     │─►│ sends    │             │    │
│   │  │ encoders │  │ new commands     │  │ to motors│             │    │
│   │  │          │  │                  │  │          │             │    │
│   │  └──────────┘  └──────────────────┘  └──────────┘             │    │
│   │      0.1ms          1.5ms               0.2ms                 │    │
│   │                                                                │    │
│   │──────────────────────────────────────────────────────────────►│    │
│                                                                         │
│   1. READ:  Hardware interface reads sensors, updates state interfaces  │
│   2. UPDATE: Each active controller computes new commands              │
│   3. WRITE: Hardware interface sends commands to actuators             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configuring ros2_control in URDF

Hardware interfaces are specified in the URDF using `<ros2_control>` tags:

```xml
<robot name="humanoid_arm">
  <!-- Standard URDF elements (links, joints) -->
  <link name="upper_arm">...</link>
  <joint name="shoulder" type="revolute">...</joint>
  <!-- ... more links and joints ... -->

  <!-- ros2_control configuration -->
  <ros2_control name="HumanoidArmSystem" type="system">

    <!-- Hardware plugin to load -->
    <hardware>
      <plugin>my_robot_hardware/MyRobotHardware</plugin>
      <param name="serial_port">/dev/ttyUSB0</param>
      <param name="baud_rate">1000000</param>
    </hardware>

    <!-- Joint interfaces -->
    <joint name="shoulder">
      <command_interface name="effort">
        <param name="min">-50.0</param>
        <param name="max">50.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="elbow">
      <command_interface name="effort">
        <param name="min">-30.0</param>
        <param name="max">30.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

  </ros2_control>
</robot>
```

### Common Controllers in ros2_control

ros2_control provides several ready-to-use controllers:

- **joint_state_broadcaster**: Publishes joint states to `/joint_states` topic
- **joint_trajectory_controller**: Follows trajectories from MoveIt or nav
- **forward_command_controller**: Passes commands directly to hardware
- **position_controllers/JointGroupPositionController**: Simple position control
- **velocity_controllers/JointGroupVelocityController**: Velocity control
- **effort_controllers/JointGroupEffortController**: Torque/force control
- **diff_drive_controller**: For differential drive mobile bases
- **gripper_action_controller**: For parallel jaw grippers

### Simulation vs Real Hardware

One of ros2_control's greatest strengths: **the same controllers work in simulation and on real hardware**. Only the hardware interface changes:

```
┌─────────────────────────────────────────────────────────────────────────┐
│               SAME CONTROLLERS, DIFFERENT HARDWARE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                     ┌─────────────────────────┐                        │
│                     │   Your Controllers      │                        │
│                     │   (JointTrajectory,     │                        │
│                     │    PID, etc.)           │                        │
│                     └───────────┬─────────────┘                        │
│                                 │                                       │
│              ┌──────────────────┼──────────────────┐                   │
│              │                  │                  │                   │
│              ▼                  ▼                  ▼                   │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐         │
│   │  Gazebo Plugin  │ │ Isaac Sim HW    │ │  Real Robot HW  │         │
│   │  Hardware       │ │ Interface       │ │  Interface      │         │
│   │  Interface      │ │                 │ │                 │         │
│   └────────┬────────┘ └────────┬────────┘ └────────┬────────┘         │
│            │                   │                   │                   │
│            ▼                   ▼                   ▼                   │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐         │
│   │     Gazebo      │ │   Isaac Sim     │ │  Motor Drivers  │         │
│   │   Simulation    │ │   Simulation    │ │  + Encoders     │         │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘         │
│                                                                         │
│   Development        Advanced sim        Production                    │
│   & testing          & ML training       deployment                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

This abstraction enables:
- Develop and test in simulation
- Transfer directly to real hardware
- Compare simulation and reality with identical controllers
- Train ML policies in simulation, deploy on hardware

---

## Section Summary

In this section, we covered the physical and software infrastructure for robot motion:

**Actuators:**
- **Brushed DC motors**: Simple but wear-prone; rarely used in modern humanoids
- **BLDC motors**: High efficiency, no brush wear; the workhorse of robotics
- **QDD actuators**: Low gear ratio preserves backdrivability for safe, compliant motion

**Actuator Selection:**
- High-torque joints (hips, knees) benefit from QDD for compliance and force sensing
- Precision joints (wrists, fingers) may use higher gear ratios
- Trade-offs between torque, speed, weight, backdrivability, and efficiency

**ros2_control Framework:**

The three main components of ros2_control are:

1. **Controller Manager**: Loads controllers, manages lifecycle, runs real-time loop
2. **Resource Manager**: Owns hardware interfaces, manages state/command interfaces, handles resource claiming
3. **Hardware Interfaces**: Implement actual hardware communication (read sensors, write commands)

**Key Benefits:**
- Standardized interface between controllers and hardware
- Same controllers work in simulation and on real hardware
- Real-time capable execution for high-frequency control
- Rich ecosystem of ready-to-use controllers

---

## Section Review Questions

1. Why are QDD (Quasi-Direct Drive) actuators preferred for humanoid leg joints over traditional high-ratio geared motors? List three specific advantages.

2. A robotics company is choosing between a 100:1 geared BLDC motor and a 9:1 QDD actuator for a robot arm that will work alongside humans. Which would you recommend and why?

3. In ros2_control, what is the difference between a "state interface" and a "command interface"? Give an example of each for a single joint.

4. Explain how ros2_control enables the same controller code to work in both Gazebo simulation and on real hardware. What component is responsible for this abstraction?

---

## Trajectory Planning: The Path to Smooth Motion

So far, we've discussed how to control individual joints (PID), what hardware moves them (actuators), and how software interfaces with hardware (ros2_control). But robots don't just hold positions—they need to move smoothly from one configuration to another. This is the domain of **trajectory planning**.

### What is a Trajectory?

A **trajectory** is more than just a path. It specifies not only *where* the robot goes, but *when* it arrives at each point—including position, velocity, and acceleration over time.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PATH vs TRAJECTORY                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   PATH (geometric only)           TRAJECTORY (time-parameterized)       │
│                                                                         │
│   Position                        Position                              │
│      ▲                               ▲                                  │
│      │     ●────────●                │     ●                            │
│      │    ╱          ╲               │    ╱ ╲                           │
│      │   ●            ●              │   ●   ╲                          │
│      │  ╱              ╲             │  ╱     ╲                         │
│      │ ●                ●            │ ●       ●─────●                  │
│      └──────────────────────►        └───────────────────────────► t    │
│         waypoints only                  position(t), velocity(t),       │
│         (no timing info)                acceleration(t) defined         │
│                                                                         │
│   "Go through these points"        "Be at this position at this time,  │
│                                     moving at this velocity"            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why Trajectory Planning Matters

Consider a humanoid robot reaching for a cup:

**Without trajectory planning:**
```
Command: "Move shoulder from 0° to 90°"
Result: Motor slams to full torque, jerky motion, cup knocked over
```

**With trajectory planning:**
```
Command: "Move shoulder from 0° to 90° over 2 seconds, smoothly"
Result: Graceful motion, cup safely grasped
```

The trajectory planner generates position, velocity, and acceleration profiles that:

- **Respect joint limits** (position, velocity, torque)
- **Avoid jerky motion** (smooth acceleration)
- **Coordinate multiple joints** (arm reaches while staying balanced)
- **Meet timing requirements** (arrive at goal in specified time)

### Velocity and Acceleration Profiles

The simplest trajectory types differ in how they handle velocity and acceleration:

#### Trapezoidal Velocity Profile

The most common profile in industrial robotics: accelerate, cruise at constant velocity, decelerate.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  TRAPEZOIDAL VELOCITY PROFILE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Velocity                                                              │
│      ▲           ┌─────────────────┐                                   │
│      │          ╱                   ╲      Vmax (cruise velocity)       │
│      │         ╱                     ╲                                  │
│      │        ╱                       ╲                                 │
│      │       ╱                         ╲                                │
│      │      ╱                           ╲                               │
│      └─────╱─────────────────────────────╲─────────────────────► t     │
│           t1          t2                 t3                             │
│        (accel)     (cruise)           (decel)                          │
│                                                                         │
│   Acceleration                                                          │
│      ▲                                                                  │
│      │  ┌────┐                                                         │
│      │  │    │                   ┌────┐                                │
│   ───┼──┴────┴───────────────────┴────┴─────────────────────────► t   │
│      │              │            │                                      │
│      │              └── zero ────┘                                      │
│                        (cruise)                                         │
│                                                                         │
│   ⊕ Simple to compute                                                  │
│   ⊕ Maximizes cruise time (efficient)                                  │
│   ⊖ Discontinuous acceleration (jerky at transitions)                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### S-Curve (Smooth) Profile

For smoother motion, the S-curve limits *jerk* (rate of change of acceleration):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      S-CURVE VELOCITY PROFILE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Velocity                                                              │
│      ▲           ╭─────────────────╮                                   │
│      │         ╱                     ╲     Smooth transitions           │
│      │        ╱                       ╲    (limited jerk)               │
│      │      ╱                           ╲                               │
│      │    ╱                               ╲                             │
│      │  ╱                                   ╲                           │
│      └─╱─────────────────────────────────────╲─────────────────► t     │
│                                                                         │
│   Acceleration                                                          │
│      ▲         ╭───╮                                                   │
│      │       ╱       ╲               ╭───╮                             │
│   ───┼──────╱─────────╲─────────────╱─────╲───────────────────► t     │
│      │                  ╲         ╱                                    │
│      │                    ╲─────╱                                      │
│      │                                                                  │
│                                                                         │
│   ⊕ Smooth acceleration (no discontinuities)                           │
│   ⊕ Reduced mechanical stress and vibration                            │
│   ⊕ Better for precise positioning                                     │
│   ⊖ Longer motion time for same peak velocity                          │
│   ⊖ More complex to compute                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Polynomial Trajectories

For even smoother motion, use polynomial functions that guarantee continuous derivatives:

**Cubic polynomial** (ensures continuous position and velocity):
```
q(t) = a₀ + a₁t + a₂t² + a₃t³
```

**Quintic polynomial** (ensures continuous position, velocity, and acceleration):
```
q(t) = a₀ + a₁t + a₂t² + a₃t³ + a₄t⁴ + a₅t⁵
```

The coefficients are computed from boundary conditions (start/end position, velocity, acceleration).

### Multi-Joint Trajectory Coordination

Humanoid robots must coordinate many joints simultaneously. The challenge: each joint has different distances to travel, but they should all finish together.

```
┌─────────────────────────────────────────────────────────────────────────┐
│              SYNCHRONIZED MULTI-JOINT TRAJECTORY                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Without synchronization:          With synchronization:               │
│                                                                         │
│   Joint 1 ──────●                   Joint 1 ────────────●              │
│   (short)       │ done early        (short)             │              │
│                 │                                       │ all finish   │
│   Joint 2 ──────────────●           Joint 2 ────────────● together     │
│   (medium)              │                               │              │
│                         │                               │              │
│   Joint 3 ────────────────────●     Joint 3 ────────────●              │
│   (long)                      │                         │              │
│   ──────────────────────────────►   ────────────────────►             │
│                            time                      time              │
│                                                                         │
│   Problem: Jerky, uncoordinated    Solution: Scale velocities so       │
│   arrival at goal                  all joints arrive simultaneously    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Synchronization approach:**
1. Compute the "slowest" joint (longest time to complete)
2. Scale all other joints to match that duration
3. All joints start and finish together

### Trajectory Planning in ROS 2

In ROS 2, trajectory planning typically flows through MoveIt or the joint_trajectory_controller:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 ROS 2 TRAJECTORY PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐  │
│   │   MoveIt    │     │  Trajectory │     │ joint_trajectory_       │  │
│   │   Motion    │────►│   Message   │────►│ controller              │  │
│   │   Planner   │     │             │     │                         │  │
│   └─────────────┘     └─────────────┘     └───────────┬─────────────┘  │
│         │                                             │                │
│         │ plans collision-free                        │ interpolates   │
│         │ path + time parameterization                │ and tracks     │
│         │                                             ▼                │
│         │                                    ┌─────────────────┐       │
│         │                                    │  Hardware via   │       │
│         │                                    │  ros2_control   │       │
│         │                                    └─────────────────┘       │
│         │                                                              │
│   ┌─────▼───────────────────────────────────────────────────────────┐  │
│   │  trajectory_msgs/JointTrajectory                                │  │
│   │  ┌─────────────────────────────────────────────────────────┐    │  │
│   │  │ joint_names: [shoulder, elbow, wrist]                   │    │  │
│   │  │ points:                                                 │    │  │
│   │  │   - time_from_start: 0.0                                │    │  │
│   │  │     positions: [0.0, 0.0, 0.0]                          │    │  │
│   │  │     velocities: [0.0, 0.0, 0.0]                         │    │  │
│   │  │   - time_from_start: 1.0                                │    │  │
│   │  │     positions: [0.5, 0.3, 0.2]                          │    │  │
│   │  │     velocities: [0.5, 0.3, 0.2]                         │    │  │
│   │  │   - time_from_start: 2.0                                │    │  │
│   │  │     positions: [1.0, 0.6, 0.4]                          │    │  │
│   │  │     velocities: [0.0, 0.0, 0.0]                         │    │  │
│   │  └─────────────────────────────────────────────────────────┘    │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

The `JointTrajectory` message contains timestamped waypoints. The controller interpolates between waypoints (often using splines) and runs PID control to track the interpolated setpoints.

---

## Inverse Dynamics: Forces Behind Motion

Trajectory planning tells us *where* to go and *when*. But to actually achieve that motion, we need to know *what forces* to apply. This is **inverse dynamics**.

### The Dynamics Problem

**Forward dynamics**: Given forces/torques, compute resulting motion
```
τ (torques) → Equations of Motion → q̈ (accelerations)
```

**Inverse dynamics**: Given desired motion, compute required forces/torques
```
q, q̇, q̈ (position, velocity, acceleration) → Equations of Motion → τ (torques)
```

For control, inverse dynamics is more useful: "I want this motion, what torque commands do I need?"

### Why Inverse Dynamics Matters

Consider a humanoid arm holding a 5kg object:

**Without inverse dynamics (PID only):**
```
PID sees error → applies corrective torque
But: gravity is pulling constantly
Result: PID fights gravity reactively, uses more energy, less precise
```

**With inverse dynamics (feedforward + PID):**
```
Inverse dynamics computes: "To hold this position against gravity,
I need τ_gravity = m × g × r"
Feedforward applies τ_gravity proactively
PID only handles small errors
Result: More efficient, more precise
```

### The Robot Dynamics Equation

The general equation of motion for a robot:

```
τ = M(q)q̈ + C(q, q̇)q̇ + g(q)
```

Where:
- **τ**: Joint torques (what we compute)
- **M(q)**: Mass/inertia matrix (depends on configuration)
- **q̈**: Joint accelerations (from trajectory)
- **C(q, q̇)**: Coriolis and centrifugal terms
- **g(q)**: Gravity torques

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INVERSE DYNAMICS COMPONENTS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   τ = M(q)q̈  +  C(q,q̇)q̇  +  g(q)                                       │
│       ──┬───    ────┬────    ──┬──                                     │
│         │           │          │                                        │
│         ▼           ▼          ▼                                        │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                               │
│   │ Inertia  │ │ Coriolis │ │ Gravity  │                               │
│   │          │ │ effects  │ │          │                               │
│   │ Torque   │ │          │ │ Torque   │                               │
│   │ to       │ │ Velocity │ │ to hold  │                               │
│   │ accel-   │ │ coupling │ │ against  │                               │
│   │ erate    │ │ between  │ │ gravity  │                               │
│   │ links    │ │ joints   │ │          │                               │
│   └──────────┘ └──────────┘ └──────────┘                               │
│                                                                         │
│   For a humanoid:                                                       │
│   • M(q): 30×30 matrix that changes with pose                          │
│   • C(q,q̇): Captures how moving one joint affects others               │
│   • g(q): Critical for balance—must counteract gravity                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Computed Torque Control

**Computed torque control** combines inverse dynamics with PID for high-performance trajectory tracking:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPUTED TORQUE CONTROL                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Desired trajectory: q_d, q̇_d, q̈_d                                    │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                                                                 │  │
│   │   q_d ──┬──────────────────────────────────┐                    │  │
│   │         │                                  │                    │  │
│   │         ▼                                  ▼                    │  │
│   │   ┌──────────┐    ┌───────────────┐  ┌──────────┐              │  │
│   │   │   PID    │    │   Inverse     │  │    +     │    ┌──────┐  │  │
│   │   │ Feedback │───►│   Dynamics    │─►│  Σ      │───►│Robot │  │  │
│   │   │          │    │  (feedfwd)    │  │         │    │      │  │  │
│   │   └──────────┘    └───────────────┘  └──────────┘    └──┬───┘  │  │
│   │         ▲                                               │      │  │
│   │         │                                               │      │  │
│   │   q ────┴───────────────────────────────────────────────┘      │  │
│   │   (measured)                                                   │  │
│   │                                                                 │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   τ = M(q)(q̈_d + Kp·e + Kd·ė) + C(q,q̇)q̇ + g(q)                        │
│       ─────────────────────────  ──────────────────                    │
│       Feedback linearization     Feedforward (gravity, dynamics)       │
│       (makes system linear)      (proactive compensation)              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Decouples the nonlinear dynamics
- PID operates on a linearized system
- Much better tracking performance
- Essential for dynamic humanoid motions

### Inverse Dynamics in Practice

Computing inverse dynamics requires:

1. **Accurate URDF** with correct inertial parameters
2. **Robot dynamics library** (KDL, Pinocchio, RBDL)
3. **Real-time computation** (can be expensive for 30+ DOF)

```python
# Example using Pinocchio library
import pinocchio as pin

# Load robot model from URDF
model = pin.buildModelFromUrdf("humanoid.urdf")
data = model.createData()

# Compute inverse dynamics
q = current_joint_positions      # Configuration
v = current_joint_velocities     # Velocity
a = desired_joint_accelerations  # From trajectory

tau = pin.rnea(model, data, q, v, a)  # Recursive Newton-Euler Algorithm
# tau now contains required joint torques
```

---

## Chapter Summary

This chapter covered the complete control stack for humanoid robot motion—from control theory to physical actuators to software frameworks.

### Control Theory Foundations

**Open-loop vs Closed-loop:**
- Open-loop control commands actuators without feedback—unsuitable for precise robotics
- Closed-loop control continuously measures and corrects errors—essential for humanoids
- The feedback loop runs at high frequency (100Hz-1kHz) to handle fast dynamics

**PID Control:**
- **Proportional (P)**: Output proportional to error—main driving force
- **Integral (I)**: Accumulates error over time—eliminates steady-state offset
- **Derivative (D)**: Responds to rate of change—dampens oscillations and overshoot
- Tuning involves balancing speed, stability, and precision
- Beyond basic PID: feedforward compensation, gain scheduling, cascaded control

### Actuators

**Motor types for humanoid robots:**
- **Brushed DC**: Simple but wear-prone—rarely used in modern designs
- **Brushless DC (BLDC)**: High efficiency, reliable, dominant in robotics
- **Quasi-Direct Drive (QDD)**: Low gear ratio preserves backdrivability for safe, compliant motion

**Actuator selection criteria:**
- Torque requirements (supporting body weight vs fine manipulation)
- Backdrivability needs (human safety, impact absorption)
- Weight constraints (especially at extremities)
- Efficiency for battery life

### ros2_control Framework

**The three main components:**
1. **Controller Manager**: Orchestrates controller lifecycle and real-time execution
2. **Resource Manager**: Manages hardware abstraction and resource allocation
3. **Hardware Interfaces**: Bridge between controllers and physical hardware

**Key benefits:**
- Same controllers work in simulation and on real hardware
- Standardized interfaces enable reusable, portable code
- Real-time capable for high-frequency control loops

### Trajectory Planning

**From path to motion:**
- Trajectories specify position, velocity, and acceleration over time
- Velocity profiles (trapezoidal, S-curve) balance speed and smoothness
- Multi-joint coordination ensures synchronized motion

**Profile trade-offs:**
- Trapezoidal: Simple, efficient, but jerky at transitions
- S-curve: Smooth, reduced vibration, but slower
- Polynomial: Maximum smoothness, complex to compute

### Inverse Dynamics

**Computing required forces:**
- Forward dynamics: forces → motion
- Inverse dynamics: desired motion → required forces
- The equation: τ = M(q)q̈ + C(q,q̇)q̇ + g(q)

**Computed torque control:**
- Combines feedforward (inverse dynamics) with feedback (PID)
- Linearizes the nonlinear robot dynamics
- Essential for precise, dynamic humanoid motion

---

## Chapter Review Questions

1. **PID Control**: A humanoid robot's elbow joint consistently undershoots its target position by 2° and stays there. Which PID term is likely insufficient, and explain why increasing it will help eliminate this steady-state error.

2. **Actuator Selection**: You're designing a humanoid robot that will work in a warehouse alongside human workers. Compare QDD actuators versus traditional high-ratio geared motors for the hip joints, discussing at least three factors (safety, performance, efficiency).

3. **ros2_control**: Explain the role of each of the three main components of ros2_control (Controller Manager, Resource Manager, Hardware Interface) in the context of a humanoid arm following a trajectory from MoveIt.

4. **Trajectory Planning**: A robot arm needs to move a joint from 0° to 90° in exactly 2 seconds. Compare trapezoidal and S-curve velocity profiles in terms of: (a) peak velocity required, (b) smoothness of motion, and (c) when you would choose each.

---

## Next Steps

With control fundamentals mastered, you're ready for more advanced topics:

**Chapter 4: Perception and Sensing**
- Camera systems and computer vision
- Force/torque sensing for manipulation
- IMUs and state estimation for balance

**Chapter 5: Motion Planning**
- Collision-free path planning with MoveIt
- Whole-body motion planning for humanoids
- Real-time replanning and obstacle avoidance

**Chapter 6: Walking and Balance**
- Zero Moment Point (ZMP) and balance criteria
- Gait generation and walking patterns
- Push recovery and robust locomotion

---

## Further Reading

- [ros2_control Documentation](https://control.ros.org/) - Official framework documentation
- [MoveIt 2 Tutorials](https://moveit.picknik.ai/) - Motion planning framework
- [Pinocchio](https://github.com/stack-of-tasks/pinocchio) - Fast rigid body dynamics library
- *Modern Robotics* by Lynch and Park - Comprehensive mechanics and control theory
- *Springer Handbook of Robotics* - Chapters on actuation and control
- [MIT Cheetah Papers](https://biomimetics.mit.edu/) - QDD actuator research and design