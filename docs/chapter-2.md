---
id: chapter-2
title: 'Chapter 2: Designing the Robot Body (URDF)'
sidebar_label: 'Chapter 2: URDF & Dynamics'
sidebar_position: 3
---

# Chapter 2: Designing the Robot Body

## Learning Objectives

By the end of this chapter, you will be able to:

- **Write** valid URDF XML to describe a robot's physical structure
- **Define** links with visual, collision, and inertial properties
- **Connect** links using appropriate joint types with proper limits and dynamics
- **Configure** transmissions to map actuators to joints for control
- **Validate** URDF files and visualize them in RViz
- **Apply** best practices for organizing complex humanoid robot descriptions

---

## Introduction: From Blueprint to Reality

In Chapter 1, we introduced URDF as the robot's "body plan"—an anatomical blueprint that defines physical structure. Now we roll up our sleeves and learn to write URDF ourselves.

Think of this chapter as learning architectural drafting for robots. Just as an architect must understand walls, doors, load-bearing structures, and building codes before designing a house, a roboticist must understand links, joints, physical properties, and URDF conventions before designing a robot. The difference? Our blueprints come to life in simulators and on real hardware.

### Why URDF Mastery Matters

For humanoid robots, URDF mastery is non-negotiable. Consider the complexity:

| Component | Typical Count | URDF Elements Required |
|-----------|---------------|------------------------|
| Torso segments | 2-3 | Links + joints |
| Arm links (per arm) | 4-5 | Links + joints + transmissions |
| Leg links (per leg) | 5-6 | Links + joints + transmissions |
| Hand fingers (per hand) | 15-20 | Links + joints |
| Head/neck | 2-3 | Links + joints |
| Sensors | 10+ | Links + fixed joints |
| **Total** | **60-80+** | **Hundreds of XML elements** |

A poorly structured URDF leads to simulation instability, incorrect motion planning, and dangerous real-world behavior. A well-structured URDF enables seamless development from simulation to deployment.

### URDF File Structure Overview

A URDF file is XML that describes a robot as a tree of rigid bodies connected by joints. Here's the high-level structure:

```xml
<?xml version="1.0"?>
<robot name="my_humanoid">

  <!-- Materials (colors/textures) -->
  <material name="blue">
    <color rgba="0.0 0.0 0.8 1.0"/>
  </material>

  <!-- Links (rigid bodies) -->
  <link name="base_link">
    <!-- visual, collision, inertial properties -->
  </link>

  <link name="torso">
    <!-- visual, collision, inertial properties -->
  </link>

  <!-- Joints (connections) -->
  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
  </joint>

  <!-- Transmissions (actuator mappings) -->
  <transmission name="torso_transmission">
    <!-- actuator to joint mapping -->
  </transmission>

</robot>
```

The `<robot>` element is the root, containing all links, joints, materials, and transmissions. The structure must form a valid tree—one root link with all other links connected through a chain of joints.

---

## Links: The Rigid Bodies

A **link** represents a single rigid body in your robot. In humanoid terms, think of links as the "bones"—the structural elements that don't deform during motion.

### Anatomy of a Link

Every link can specify three types of properties:

```xml
<link name="upper_arm">

  <!-- VISUAL: What the robot looks like -->
  <visual>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.05" length="0.3"/>
    </geometry>
    <material name="skin_tone"/>
  </visual>

  <!-- COLLISION: What participates in collision detection -->
  <collision>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.055" length="0.32"/>
    </geometry>
  </collision>

  <!-- INERTIAL: Mass and rotational properties for dynamics -->
  <inertial>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <mass value="2.5"/>
    <inertia ixx="0.02" ixy="0" ixz="0"
             iyy="0.02" iyz="0"
             izz="0.005"/>
  </inertial>

</link>
```

Let's examine each component in detail.

### Visual Properties

The `<visual>` element defines how the link appears in visualization tools (RViz) and simulators. It has no effect on physics—a link could be visually invisible but still participate in simulation.

```xml
<visual name="upper_arm_visual">
  <origin xyz="0 0 0.15" rpy="0 0 0"/>
  <geometry>
    <!-- Geometry options shown below -->
  </geometry>
  <material name="blue"/>
</visual>
```

**Origin**: The `<origin>` specifies where the visual geometry is placed relative to the link's coordinate frame. The `xyz` values are translation (meters), and `rpy` values are rotation in roll-pitch-yaw (radians).

**Geometry options**:

```xml
<!-- Primitive shapes -->
<geometry>
  <box size="0.1 0.2 0.3"/>           <!-- x, y, z dimensions -->
</geometry>

<geometry>
  <cylinder radius="0.05" length="0.3"/>
</geometry>

<geometry>
  <sphere radius="0.1"/>
</geometry>

<!-- Mesh from file (for complex shapes) -->
<geometry>
  <mesh filename="package://my_robot/meshes/upper_arm.stl" scale="1.0 1.0 1.0"/>
</geometry>
```

**Materials**: Define colors or textures for visual appearance:

```xml
<!-- Defined at robot level, referenced in visuals -->
<material name="skin_tone">
  <color rgba="0.96 0.80 0.69 1.0"/>  <!-- RGBA, values 0-1 -->
</material>

<material name="metal_gray">
  <color rgba="0.7 0.7 0.7 1.0"/>
</material>

<!-- Or with texture -->
<material name="carbon_fiber">
  <texture filename="package://my_robot/textures/carbon.png"/>
</material>
```

### Collision Properties

The `<collision>` element defines the geometry used for collision detection. This is critical for:

- **Motion planning**: Ensuring trajectories don't cause self-collision or environment collision
- **Physics simulation**: Detecting contacts and computing reaction forces
- **Safety systems**: Triggering emergency stops before dangerous contacts

```xml
<collision name="upper_arm_collision">
  <origin xyz="0 0 0.15" rpy="0 0 0"/>
  <geometry>
    <cylinder radius="0.055" length="0.32"/>
  </geometry>
</collision>
```

**Why collision geometry differs from visual geometry:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISUAL vs COLLISION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   VISUAL (detailed mesh)         COLLISION (simplified)        │
│                                                                 │
│   ╭──────────────────╮           ┌──────────────────┐          │
│   │  ╱╲    ╱╲    ╱╲  │           │                  │          │
│   │ ╱  ╲  ╱  ╲  ╱  ╲ │           │                  │          │
│   │╱    ╲╱    ╲╱    ╲│    →      │                  │          │
│   │╲    ╱╲    ╱╲    ╱│           │                  │          │
│   │ ╲  ╱  ╲  ╱  ╲  ╱ │           │                  │          │
│   │  ╲╱    ╲╱    ╲╱  │           └──────────────────┘          │
│   ╰──────────────────╯                                         │
│                                                                 │
│   50,000 triangles              6 faces (box)                  │
│   Beautiful rendering           Fast collision checks          │
│   Slow intersection tests       Slight over-approximation      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

For real-time performance, collision geometry should be as simple as possible while still capturing the essential shape. Common strategies:

1. **Primitive approximation**: Use boxes, cylinders, spheres
2. **Convex decomposition**: Break complex shapes into convex hulls
3. **Multiple collision bodies**: Combine several primitives per link

```xml
<!-- Multiple collision geometries for better approximation -->
<link name="torso">
  <collision name="torso_main">
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
    <geometry><box size="0.3 0.2 0.4"/></geometry>
  </collision>
  <collision name="torso_shoulder_left">
    <origin xyz="0 0.18 0.35" rpy="0 0 0"/>
    <geometry><sphere radius="0.08"/></geometry>
  </collision>
  <collision name="torso_shoulder_right">
    <origin xyz="0 -0.18 0.35" rpy="0 0 0"/>
    <geometry><sphere radius="0.08"/></geometry>
  </collision>
</link>
```

### Inertial Properties

The `<inertial>` element defines mass and rotational inertia—essential for dynamic simulation. Without accurate inertial properties, your simulated robot will behave unrealistically.

```xml
<inertial>
  <origin xyz="0 0 0.12" rpy="0 0 0"/>  <!-- Center of mass location -->
  <mass value="2.5"/>                    <!-- Mass in kg -->
  <inertia ixx="0.02" ixy="0" ixz="0"   <!-- Inertia tensor -->
           iyy="0.02" iyz="0"
           izz="0.005"/>
</inertial>
```

**Center of mass**: The `<origin>` specifies where the center of mass is located relative to the link frame. For a uniform-density cylinder centered at z=0.15, the CoM would also be at z=0.15.

**Inertia tensor**: The 3x3 symmetric matrix describing rotational inertia:

```
    ┌                    ┐
    │ ixx  ixy  ixz      │
I = │ ixy  iyy  iyz      │
    │ ixz  iyz  izz      │
    └                    ┘
```

For primitive shapes with uniform density, inertia can be calculated:

| Shape | Ixx, Iyy | Izz |
|-------|----------|-----|
| **Solid cylinder** (radius r, length h, mass m) | m(3r² + h²)/12 | mr²/2 |
| **Solid box** (dimensions x, y, z, mass m) | m(y² + z²)/12 | m(x² + y²)/12 |
| **Solid sphere** (radius r, mass m) | 2mr²/5 | 2mr²/5 |

For complex meshes, CAD software or tools like MeshLab can compute inertial properties.

### The Base Link

Every URDF requires a root link—typically called `base_link`. For humanoid robots, this is usually the pelvis or torso base:

```xml
<link name="base_link">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.25 0.3 0.15"/>
    </geometry>
    <material name="metal_gray"/>
  </visual>
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.26 0.31 0.16"/>
    </geometry>
  </collision>
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="8.0"/>
    <inertia ixx="0.1" ixy="0" ixz="0"
             iyy="0.08" iyz="0"
             izz="0.12"/>
  </inertial>
</link>
```

---

## Joints: The Connections

**Joints** define how links connect and move relative to each other. If links are the bones, joints are the articulations—shoulders, elbows, hips, knees.

### Joint Types

URDF supports six joint types, each with different degrees of freedom:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         URDF JOINT TYPES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FIXED (0 DOF)              REVOLUTE (1 DOF)         CONTINUOUS (1 DOF) │
│  ┌───┬───┐                  ┌───┐                    ┌───┐              │
│  │   │   │                  │   │ ←─╮                │   │ ↻            │
│  │ A │ B │  No motion       │ A │   │ Rotation       │ A │   Unlimited  │
│  │   │   │                  │   │ ←─╯ with limits    │   │   rotation   │
│  └───┴───┘                  └─┬─┘                    └─┬─┘              │
│                               │                        │                │
│                             ┌─┴─┐                    ┌─┴─┐              │
│                             │ B │                    │ B │              │
│                             └───┘                    └───┘              │
│                                                                         │
│  PRISMATIC (1 DOF)          FLOATING (6 DOF)         PLANAR (3 DOF)    │
│  ┌───┐                      ┌───┐                    ┌───┐              │
│  │ A │                      │ A │ ↕↔↻               │ A │ ↕↔↻          │
│  └─┬─┘  Linear              └───┘   Free 3D          └─┬─┘  XY plane   │
│    │↕   sliding                     movement           │    movement   │
│  ┌─┴─┐                      ┌───┐                    ┌─┴─┐              │
│  │ B │                      │ B │                    │ B │              │
│  └───┘                      └───┘                    └───┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**For humanoid robots:**
- **Revolute joints**: Elbows, knees, fingers, wrists—most humanoid joints
- **Continuous joints**: Wheels (if present), rotating sensors
- **Fixed joints**: Sensor mounts, decorative elements, rigidly attached components
- **Prismatic joints**: Telescoping elements, linear actuators
- **Floating joints**: The base link's connection to the world (in simulation)

### Anatomy of a Joint

```xml
<joint name="shoulder_pitch" type="revolute">

  <!-- Parent and child links -->
  <parent link="torso"/>
  <child link="upper_arm"/>

  <!-- Joint location and orientation -->
  <origin xyz="0 0.2 0.4" rpy="0 0 0"/>

  <!-- Axis of rotation/translation -->
  <axis xyz="0 1 0"/>

  <!-- Position limits (for revolute/prismatic) -->
  <limit lower="-2.0" upper="2.0"
         effort="100.0" velocity="2.0"/>

  <!-- Dynamic properties -->
  <dynamics damping="0.5" friction="0.1"/>

</joint>
```

Let's examine each element:

### Parent and Child

Every joint connects exactly two links:

```xml
<parent link="torso"/>      <!-- The link closer to the root -->
<child link="upper_arm"/>   <!-- The link further from the root -->
```

The child link's frame is positioned relative to the parent link's frame based on the joint's `<origin>`.

### Origin

The `<origin>` specifies where the joint is located in the **parent link's frame**:

```xml
<origin xyz="0 0.2 0.4" rpy="0 0 0"/>
```

This means: "The joint frame is 0.2m in Y and 0.4m in Z from the parent link's origin, with no rotation."

```
           Parent Link (torso)
           ┌────────────────────┐
           │       origin       │
           │         ↓          │
           │    xyz="0 0 0"     │
           │                    │
           │         ★ ←─────── Joint origin at xyz="0 0.2 0.4"
           │                    │   relative to parent
           └────────────────────┘
                     │
                     │ (joint)
                     │
           ┌────────────────────┐
           │    Child Link      │
           │   (upper_arm)      │
           │                    │
           │  Child's origin    │
           │  is at joint       │
           └────────────────────┘
```

### Axis

The `<axis>` defines the direction of rotation (revolute/continuous) or translation (prismatic):

```xml
<axis xyz="0 1 0"/>  <!-- Rotation around the Y axis -->
```

Common axis configurations:

| Axis | Joint Motion |
|------|-------------|
| `xyz="1 0 0"` | Roll (rotation around X) |
| `xyz="0 1 0"` | Pitch (rotation around Y) |
| `xyz="0 0 1"` | Yaw (rotation around Z) |
| `xyz="0 0 1"` | Vertical linear motion (prismatic) |

### Limits

The `<limit>` element constrains joint motion:

```xml
<limit lower="-2.0"      <!-- Minimum position (rad or m) -->
       upper="2.0"       <!-- Maximum position (rad or m) -->
       effort="100.0"    <!-- Maximum force/torque (N or Nm) -->
       velocity="2.0"/>  <!-- Maximum velocity (rad/s or m/s) -->
```

**For humanoid joints**, realistic limits are crucial:

| Joint | Typical Lower | Typical Upper | Notes |
|-------|---------------|---------------|-------|
| Shoulder pitch | -π | π/2 | Can't rotate arm behind back fully |
| Elbow | 0 | 2.5 rad | Only bends one direction |
| Hip pitch | -π/2 | π/2 | Walking range |
| Knee | 0 | 2.6 rad | Only bends backward |
| Ankle pitch | -0.7 | 0.7 | Limited by foot structure |

### Dynamics

The `<dynamics>` element specifies damping and friction:

```xml
<dynamics damping="0.5"    <!-- Viscous damping (Nm·s/rad) -->
          friction="0.1"/> <!-- Coulomb friction (Nm) -->
```

- **Damping**: Resistance proportional to velocity (like moving through honey)
- **Friction**: Constant resistance to motion (like stiction)

These affect simulation behavior and controller tuning. Start with small values and adjust based on simulation results.

### Joint Examples for Humanoid Robots

**Shoulder joint (3 DOF in reality, modeled as 3 revolute joints):**

```xml
<!-- Shoulder roll: rotation around X (forward axis) -->
<joint name="left_shoulder_roll" type="revolute">
  <parent link="torso"/>
  <child link="left_shoulder_link"/>
  <origin xyz="0 0.2 0.4" rpy="0 0 0"/>
  <axis xyz="1 0 0"/>
  <limit lower="-0.5" upper="3.14" effort="80" velocity="3.0"/>
  <dynamics damping="0.3" friction="0.1"/>
</joint>

<!-- Shoulder pitch: rotation around Y (lateral axis) -->
<joint name="left_shoulder_pitch" type="revolute">
  <parent link="left_shoulder_link"/>
  <child link="left_upper_arm"/>
  <origin xyz="0 0.05 0" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-2.0" upper="2.0" effort="80" velocity="3.0"/>
  <dynamics damping="0.3" friction="0.1"/>
</joint>

<!-- Shoulder yaw: rotation around Z (vertical axis) -->
<joint name="left_shoulder_yaw" type="revolute">
  <parent link="left_upper_arm"/>
  <child link="left_upper_arm_rotated"/>
  <origin xyz="0 0 -0.15" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.5" upper="1.5" effort="60" velocity="3.0"/>
  <dynamics damping="0.2" friction="0.1"/>
</joint>
```

**Elbow joint (1 DOF):**

```xml
<joint name="left_elbow" type="revolute">
  <parent link="left_upper_arm_rotated"/>
  <child link="left_forearm"/>
  <origin xyz="0 0 -0.3" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="0" upper="2.5" effort="60" velocity="4.0"/>
  <dynamics damping="0.2" friction="0.05"/>
</joint>
```

**Fixed joint (for sensor mounting):**

```xml
<joint name="head_camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.1" rpy="0 0.2 0"/>
  <!-- No axis, limits, or dynamics needed for fixed joints -->
</joint>
```

---

## Transmissions: Connecting Actuators to Joints

Real robots have **actuators** (motors) that drive **joints**. The relationship between them isn't always one-to-one. **Transmissions** define how actuator effort translates to joint motion.

### Why Transmissions Matter

Consider these real-world scenarios:

1. **Gear reduction**: A motor spins fast with low torque; gears convert this to slow movement with high torque
2. **Belt/chain drives**: The motor isn't colocated with the joint
3. **Differential drives**: Two motors work together to control two joints
4. **Tendon systems**: Cables route motor force through complex paths (common in humanoid hands)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ACTUATOR TO JOINT MAPPING                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DIRECT DRIVE              GEAR REDUCTION           TENDON SYSTEM      │
│                                                                         │
│   ┌─────┐                   ┌─────┐                  ┌─────┐           │
│   │Motor│                   │Motor│                  │Motor│           │
│   └──┬──┘                   └──┬──┘                  └──┬──┘           │
│      │                         │                        │              │
│      │ 1:1                     │                     ~~~│~~~ cables    │
│      │                      ╭──┴──╮                     │              │
│      │                      │Gears│ 100:1           ┌──┴──┐           │
│      │                      ╰──┬──╯                 │Spool│           │
│      │                         │                    └──┬──┘           │
│   ┌──┴──┐                   ┌──┴──┐                 ┌──┴──┐           │
│   │Joint│                   │Joint│                 │Joint│           │
│   └─────┘                   └─────┘                 └─────┘           │
│                                                                         │
│   τ_joint = τ_motor        τ_joint = 100·τ_motor   Complex mapping    │
│   ω_joint = ω_motor        ω_joint = ω_motor/100   via Jacobian       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Transmission Syntax

```xml
<transmission name="left_elbow_transmission">

  <!-- Transmission type -->
  <type>transmission_interface/SimpleTransmission</type>

  <!-- Which joint this transmission drives -->
  <joint name="left_elbow">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>

  <!-- The actuator providing force -->
  <actuator name="left_elbow_motor">
    <mechanicalReduction>100</mechanicalReduction>  <!-- Gear ratio -->
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </actuator>

</transmission>
```

### Key Transmission Elements

**Type**: Specifies the transmission model:

| Type | Description |
|------|-------------|
| `SimpleTransmission` | Single actuator to single joint with gear ratio |
| `DifferentialTransmission` | Two actuators driving two joints (differential) |
| `FourBarLinkageTransmission` | Mechanical linkage common in legs |

**Joint reference**: Which joint the transmission drives:

```xml
<joint name="left_elbow">
  <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
</joint>
```

**Hardware interfaces** define how controllers interact with the joint:

| Interface | Control Mode | Units |
|-----------|-------------|-------|
| `EffortJointInterface` | Torque/force control | Nm or N |
| `VelocityJointInterface` | Velocity control | rad/s or m/s |
| `PositionJointInterface` | Position control | rad or m |

**Actuator**: The motor driving the joint:

```xml
<actuator name="left_elbow_motor">
  <mechanicalReduction>100</mechanicalReduction>
  <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
</actuator>
```

The `mechanicalReduction` is the gear ratio. A value of 100 means:
- Motor torque × 100 = Joint torque
- Motor velocity ÷ 100 = Joint velocity

### Transmission Examples for Humanoid Robots

**High-torque leg joint with gear reduction:**

```xml
<transmission name="left_hip_pitch_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_hip_pitch">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_hip_pitch_motor">
    <mechanicalReduction>160</mechanicalReduction>
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </actuator>
</transmission>
```

**Direct-drive arm joint (for backdrivability and force sensing):**

```xml
<transmission name="left_shoulder_pitch_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_shoulder_pitch">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_shoulder_pitch_motor">
    <mechanicalReduction>1</mechanicalReduction>  <!-- Direct drive -->
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </actuator>
</transmission>
```

**Position-controlled gripper:**

```xml
<transmission name="left_gripper_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_gripper_finger">
    <hardwareInterface>hardware_interface/PositionJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_gripper_motor">
    <mechanicalReduction>50</mechanicalReduction>
    <hardwareInterface>hardware_interface/PositionJointInterface</hardwareInterface>
  </actuator>
</transmission>
```

### Transmissions and ros2_control

In ROS 2, transmissions work with the **ros2_control** framework. The URDF transmission definitions are read by the hardware interface, which then:

1. Reads actuator state (position, velocity, effort)
2. Applies transmission math to compute joint state
3. Accepts joint commands from controllers
4. Applies inverse transmission math to compute actuator commands

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ros2_control FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────┐    joint     ┌──────────────┐    actuator   ┌────────┐  │
│  │Controller │───commands──►│ Transmission │───commands───►│Hardware│  │
│  │           │              │    Math      │               │        │  │
│  │  (PID,    │◄───state─────│   (×ratio,   │◄───state──────│(motors,│  │
│  │   MPC)    │    joint     │    ÷ratio)   │   actuator    │sensors)│  │
│  └───────────┘              └──────────────┘               └────────┘  │
│                                                                         │
│  Joint space                                        Actuator space     │
│  (what planners see)                                (what hardware is) │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Putting It Together: A Simple Arm

Let's combine links, joints, and transmissions into a complete 2-DOF arm:

```xml
<?xml version="1.0"?>
<robot name="simple_arm">

  <!-- Materials -->
  <material name="gray">
    <color rgba="0.7 0.7 0.7 1.0"/>
  </material>
  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>

  <!-- Base (fixed to world) -->
  <link name="base_link">
    <visual>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.02"/>
    </inertial>
  </link>

  <!-- Upper arm -->
  <link name="upper_arm">
    <visual>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <geometry><cylinder radius="0.04" length="0.3"/></geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <geometry><cylinder radius="0.045" length="0.32"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.017" ixy="0" ixz="0" iyy="0.017" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Forearm -->
  <link name="forearm">
    <visual>
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <geometry><cylinder radius="0.035" length="0.25"/></geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <geometry><cylinder radius="0.04" length="0.27"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.0008"/>
    </inertial>
  </link>

  <!-- Shoulder joint -->
  <joint name="shoulder" type="revolute">
    <parent link="base_link"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0.025" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="2.0"/>
    <dynamics damping="0.5" friction="0.1"/>
  </joint>

  <!-- Elbow joint -->
  <joint name="elbow" type="revolute">
    <parent link="upper_arm"/>
    <child link="forearm"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="2.5" effort="30" velocity="2.5"/>
    <dynamics damping="0.3" friction="0.05"/>
  </joint>

  <!-- Transmissions -->
  <transmission name="shoulder_transmission">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="shoulder">
      <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="shoulder_motor">
      <mechanicalReduction>100</mechanicalReduction>
      <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    </actuator>
  </transmission>

  <transmission name="elbow_transmission">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="elbow">
      <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="elbow_motor">
      <mechanicalReduction>80</mechanicalReduction>
      <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    </actuator>
  </transmission>

</robot>
```

This URDF defines:
- A fixed base
- Two arm links with full visual, collision, and inertial properties
- Two revolute joints with realistic limits
- Two transmissions with gear reduction for torque amplification

---

## Section Summary

In this section, we've covered the fundamental building blocks of URDF:

**Links** define the rigid bodies of your robot:
- Visual geometry for appearance
- Collision geometry for physics and planning
- Inertial properties for dynamics simulation

**Joints** define the connections between links:
- Six joint types for different motion capabilities
- Origin, axis, limits, and dynamics parameters
- Parent-child relationships forming a kinematic tree

**Transmissions** map actuators to joints:
- Gear ratios for torque/speed tradeoffs
- Hardware interfaces for different control modes
- Integration with ros2_control framework

In the next section, we'll explore how to add sensors to your URDF, work with Gazebo plugins for simulation, and use Xacro to manage complex robot descriptions efficiently.

---

## Section Review Questions

1. Why might you use different geometries for a link's visual and collision properties? Give an example where this distinction matters.

2. A humanoid robot's knee joint only bends in one direction (like a human knee). What joint type would you use, and how would you set the limits?

3. If a motor has a gear ratio of 100:1, and the motor produces 0.5 Nm of torque at 3000 RPM, what is the resulting joint torque and velocity?

4. Explain why transmissions are important for ros2_control. What happens if you omit them from your URDF?

---

## Kinematics: The Mathematics of Motion

Understanding how joint angles relate to end-effector position is fundamental to robot control. This relationship is captured by **kinematics**—the study of motion without considering forces.

### Forward Kinematics: From Angles to Position

**Forward kinematics (FK)** answers the question: *"Given the angles of all joints, where is the end-effector?"*

For a humanoid robot reaching out its arm, forward kinematics computes the hand position from the shoulder, elbow, and wrist joint angles.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FORWARD KINEMATICS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   INPUT: Joint Angles              OUTPUT: End-Effector Pose            │
│                                                                         │
│   θ₁ = 45°  (shoulder)                    ┌─────────────────┐          │
│   θ₂ = 30°  (elbow)        ────────►      │  x = 0.52 m     │          │
│   θ₃ = -15° (wrist)            FK         │  y = 0.31 m     │          │
│                                           │  z = 0.85 m     │          │
│   ┌───┐                                   │  orientation... │          │
│   │ θ │  Joint                            └─────────────────┘          │
│   └───┘  Space                               Cartesian Space           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**How it works:**

Each joint and link in URDF defines a transformation—a combination of rotation and translation. Forward kinematics chains these transformations together:

```
T_base_to_hand = T_base_to_shoulder × T_shoulder_to_upper_arm ×
                 T_upper_arm_to_forearm × T_forearm_to_hand
```

Each transformation `T` is a 4×4 matrix encoding both rotation and translation:

```
    ┌                         ┐
    │  R₁₁  R₁₂  R₁₃  │  tx   │
T = │  R₂₁  R₂₂  R₂₃  │  ty   │    R = 3×3 rotation matrix
    │  R₃₁  R₃₂  R₃₃  │  tz   │    t = translation vector
    │   0    0    0   │   1   │
    └                         ┘
```

The URDF provides the **fixed** transformations (link lengths, joint positions), while the **variable** parts depend on current joint angles.

**Forward kinematics is always solvable**—given joint values, there's exactly one end-effector pose. This makes FK computationally straightforward: just multiply the transformation matrices.

### Inverse Kinematics: From Position to Angles

**Inverse kinematics (IK)** answers the opposite question: *"Given a desired end-effector position, what joint angles achieve it?"*

This is what robots actually need for tasks: "Move your hand to grasp that cup" requires computing the joint angles that place the hand at the cup's location.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      INVERSE KINEMATICS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   INPUT: Desired Pose              OUTPUT: Joint Angles                 │
│                                                                         │
│   ┌─────────────────┐                    θ₁ = 45°  (shoulder)          │
│   │  x = 0.52 m     │      ────────►     θ₂ = 30°  (elbow)             │
│   │  y = 0.31 m     │          IK        θ₃ = -15° (wrist)             │
│   │  z = 0.85 m     │                                                   │
│   │  orientation... │                    ┌───┐                          │
│   └─────────────────┘                    │ θ │  Joint                   │
│      Cartesian Space                     └───┘  Space                   │
│                                                                         │
│   CHALLENGES:                                                           │
│   • May have NO solution (target out of reach)                          │
│   • May have MULTIPLE solutions (elbow up vs down)                      │
│   • May have INFINITE solutions (redundant robots)                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**IK challenges:**

1. **No solution**: The target is outside the robot's workspace (too far to reach)
2. **Multiple solutions**: The same hand position can be achieved with "elbow up" or "elbow down"
3. **Infinite solutions**: A 7-DOF arm reaching a 6-DOF pose has a free parameter (redundancy)
4. **Singularities**: Configurations where the robot loses degrees of freedom

**IK solution methods:**

| Method | Description | Pros | Cons |
|--------|-------------|------|------|
| **Analytical** | Closed-form equations | Fast, exact | Only for specific geometries |
| **Numerical (Jacobian)** | Iterative optimization | General purpose | May not converge, local minima |
| **Learning-based** | Neural networks | Handles complex cases | Requires training data |

For humanoid robots, IK is computed continuously—every time you want the robot to reach somewhere, an IK solver determines the joint commands.

### Kinematics and URDF

URDF provides all the information needed for kinematic calculations:

- **Link lengths** from visual/collision geometry origins
- **Joint positions** from `<origin>` elements
- **Joint axes** from `<axis>` elements
- **Joint limits** constraining valid solutions

Libraries like **KDL (Kinematics and Dynamics Library)** and **MoveIt** parse URDF files and automatically build kinematic models for FK and IK computation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    URDF → KINEMATIC MODEL                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   URDF File                        Kinematic Chain                      │
│   ┌─────────────────┐              ┌─────────────────┐                 │
│   │ <link name="A"> │              │                 │                 │
│   │ <joint to="B">  │  ────────►   │  A ──○── B ──○── C               │
│   │ <link name="B"> │   parser     │      θ₁     θ₂                   │
│   │ <joint to="C">  │              │                 │                 │
│   │ <link name="C"> │              │  FK(θ₁,θ₂) → pose_C              │
│   └─────────────────┘              │  IK(pose_C) → θ₁,θ₂              │
│                                    └─────────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Joint Types in Detail

We introduced joint types earlier; now let's examine each in depth with practical XML examples.

### Revolute Joints

**Revolute joints** rotate around a single axis within defined limits. They are the most common joint type in humanoid robots—elbows, knees, fingers, and most shoulder/hip axes.

```xml
<joint name="elbow_joint" type="revolute">
  <parent link="upper_arm"/>
  <child link="forearm"/>
  <origin xyz="0 0 -0.3" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="0.0" upper="2.5" effort="50.0" velocity="3.14"/>
  <dynamics damping="0.5" friction="0.1"/>
</joint>
```

**Key characteristics:**
- Single degree of freedom (rotation)
- **Requires `<limit>`** with lower/upper bounds (radians)
- Axis defines rotation direction (right-hand rule)

**Physical analogy:** A door hinge that can only open so far.

```
         axis xyz="0 1 0"
              │
              │  (rotation around Y)
              ▼
        ┌─────────┐
        │         │
   ─────┤  Joint  ├─────
        │         │
        └─────────┘
             ↻
        lower=0 ──► upper=2.5 rad
```

### Continuous Joints

**Continuous joints** rotate around a single axis with no limits—they can spin forever in either direction.

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="chassis"/>
  <child link="wheel"/>
  <origin xyz="0.15 0.1 0" rpy="-1.5708 0 0"/>
  <axis xyz="0 0 1"/>
  <dynamics damping="0.1" friction="0.05"/>
</joint>
```

**Key characteristics:**
- Single degree of freedom (unlimited rotation)
- **No position limits** (but effort/velocity limits still apply)
- Common for wheels, rotating sensors, wrists that need full rotation

**Physical analogy:** A bicycle wheel on its axle.

**When to use continuous vs revolute:**

| Use Continuous | Use Revolute |
|----------------|--------------|
| Wheels | Elbows, knees |
| Rotating LIDAR mounts | Fingers |
| Wrists needing >360° | Shoulder pitch/roll |
| Conveyor rollers | Hip joints |

### Prismatic Joints

**Prismatic joints** translate (slide) along a single axis, like a drawer or telescope.

```xml
<joint name="lift_joint" type="prismatic">
  <parent link="base"/>
  <child link="platform"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="0.0" upper="0.5" effort="100.0" velocity="0.2"/>
  <dynamics damping="1.0" friction="0.5"/>
</joint>
```

**Key characteristics:**
- Single degree of freedom (translation)
- **Limits in meters** (not radians)
- Axis defines sliding direction

**Physical analogy:** A drawer sliding in and out.

```
        axis xyz="0 0 1"
              │
              │  (translation along Z)
              ▼
        ┌─────────┐
        │         │  ↕ slides up/down
   ─────┤  Joint  ├─────
        │         │
        └─────────┘

        lower=0m ──► upper=0.5m
```

**Humanoid applications:**
- Torso lift mechanisms
- Telescoping limbs
- Linear actuators for specialized grippers

### Fixed Joints

**Fixed joints** rigidly connect two links with no relative motion. They're structural, not kinematic.

```xml
<joint name="camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.08" rpy="0 0.1 0"/>
</joint>
```

**Key characteristics:**
- Zero degrees of freedom
- **No axis, limits, or dynamics** needed
- Used for sensors, decorative elements, structural connections

**Physical analogy:** A welded connection or bolted mount.

**Common uses in humanoid robots:**

| Component | Parent Link | Purpose |
|-----------|-------------|---------|
| Camera | Head | Vision sensor mounting |
| IMU | Torso | Inertial measurement |
| Force/torque sensor | Wrist | Contact sensing |
| Cosmetic shell | Structure | Appearance |
| Battery pack | Torso | Power storage |

### Joint Type Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JOINT TYPE COMPARISON                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   TYPE        DOF   MOTION          LIMITS      TYPICAL USE             │
│   ─────────────────────────────────────────────────────────────────     │
│   revolute    1     rotation        required    elbows, knees           │
│   continuous  1     rotation        none        wheels, wrists          │
│   prismatic   1     translation     required    lifts, telescopes       │
│   fixed       0     none            N/A         sensor mounts           │
│   floating    6     free 3D         none        mobile base (sim)       │
│   planar      3     XY + rotation   none        holonomic base (sim)    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Complete XML Example: A Simple Robotic Arm

Let's build a complete, minimal URDF for a two-link arm with one revolute joint. This example demonstrates the essential structure without overwhelming complexity.

### The Robot Description

We'll create:
- A **base** fixed to the world
- An **upper arm** link
- A single **revolute joint** connecting them

```
                    ┌─────────────┐
                    │  upper_arm  │
                    │             │
                    │  (link 2)   │
                    │             │
                    └──────┬──────┘
                           │
                    ═══════╪═══════  ← shoulder_joint (revolute)
                           │           rotates around Y axis
                    ┌──────┴──────┐
                    │             │
                    │  base_link  │
                    │             │
                    │  (link 1)   │
                    │             │
                    └─────────────┘
                         ═══
                       (world)
```

### The Complete URDF

```xml
<?xml version="1.0"?>
<!--
  Simple Two-Link Arm URDF
  A minimal example demonstrating links and a revolute joint.
-->
<robot name="simple_two_link_arm">

  <!-- ==================== MATERIALS ==================== -->
  <!-- Define colors for visual appearance -->

  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>

  <material name="orange">
    <color rgba="0.9 0.5 0.1 1.0"/>
  </material>

  <!-- ==================== LINK 1: BASE ==================== -->
  <!-- The base link is typically fixed to the world -->

  <link name="base_link">

    <!-- Visual: What you see in RViz/Gazebo -->
    <visual>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <!-- Collision: Used for physics and planning -->
    <collision>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.1"/>
      </geometry>
    </collision>

    <!-- Inertial: Mass properties for dynamics -->
    <inertial>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <mass value="5.0"/>
      <inertia
        ixx="0.015" ixy="0.0" ixz="0.0"
        iyy="0.015" iyz="0.0"
        izz="0.025"/>
    </inertial>

  </link>

  <!-- ==================== LINK 2: UPPER ARM ==================== -->
  <!-- The moving link that rotates relative to the base -->

  <link name="upper_arm">

    <!-- Visual: Cylinder representing the arm segment -->
    <visual>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.4"/>
      </geometry>
      <material name="orange"/>
    </visual>

    <!-- Collision: Slightly larger for safety margin -->
    <collision>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.045" length="0.42"/>
      </geometry>
    </collision>

    <!-- Inertial: Properties for a solid cylinder -->
    <inertial>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia
        ixx="0.029" ixy="0.0" ixz="0.0"
        iyy="0.029" iyz="0.0"
        izz="0.0016"/>
    </inertial>

  </link>

  <!-- ==================== JOINT: SHOULDER ==================== -->
  <!-- Revolute joint connecting base to upper arm -->

  <joint name="shoulder_joint" type="revolute">

    <!-- Parent-child relationship -->
    <parent link="base_link"/>
    <child link="upper_arm"/>

    <!-- Joint position: top of base link -->
    <origin xyz="0 0 0.1" rpy="0 0 0"/>

    <!-- Rotation axis: Y-axis (pitch motion) -->
    <axis xyz="0 1 0"/>

    <!-- Motion constraints -->
    <limit
      lower="-1.5708"
      upper="1.5708"
      effort="50.0"
      velocity="1.0"/>

    <!-- Dynamic properties -->
    <dynamics damping="0.5" friction="0.1"/>

  </joint>

</robot>
```

### Understanding the XML Structure

**1. XML Declaration and Robot Element**

```xml
<?xml version="1.0"?>
<robot name="simple_two_link_arm">
  <!-- All content here -->
</robot>
```

Every URDF starts with the XML declaration and a root `<robot>` element with a unique name.

**2. Materials Section**

```xml
<material name="blue">
  <color rgba="0.2 0.2 0.8 1.0"/>
</material>
```

Materials are defined once and referenced by name in visual elements. The RGBA values range from 0.0 to 1.0 (red, green, blue, alpha).

**3. Link Structure**

Each link follows the pattern:

```xml
<link name="unique_name">
  <visual>...</visual>       <!-- Appearance -->
  <collision>...</collision> <!-- Physics boundary -->
  <inertial>...</inertial>   <!-- Mass properties -->
</link>
```

**4. Joint Structure**

The joint connects parent to child:

```xml
<joint name="unique_name" type="revolute">
  <parent link="base_link"/>      <!-- Closer to root -->
  <child link="upper_arm"/>       <!-- Further from root -->
  <origin xyz="x y z" rpy="r p y"/>  <!-- Position in parent frame -->
  <axis xyz="x y z"/>             <!-- Rotation/translation direction -->
  <limit lower="..." upper="..." effort="..." velocity="..."/>
  <dynamics damping="..." friction="..."/>
</joint>
```

### Validating Your URDF

Before using a URDF, always validate it:

```bash
# Install the URDF tools
sudo apt install liburdfdom-tools

# Check URDF syntax
check_urdf simple_arm.urdf

# Visualize the kinematic tree
urdf_to_graphiz simple_arm.urdf
```

**Common validation errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| "Link not found" | Typo in parent/child name | Check spelling exactly |
| "Multiple roots" | More than one link with no parent | Ensure single root |
| "Loop detected" | Kinematic loop in structure | URDF must be a tree |
| "Missing inertial" | Link has no mass properties | Add `<inertial>` element |

### Visualizing in RViz

To view your URDF in RViz:

```bash
# Launch RViz with URDF display
ros2 launch urdf_tutorial display.launch.py model:=/path/to/simple_arm.urdf
```

You should see the robot with:
- Blue cylindrical base
- Orange cylindrical arm
- A joint you can manipulate with the joint_state_publisher GUI

---

## Extending the Example: Adding a Second Joint

Let's extend our simple arm to include a forearm and elbow joint:

```xml
<!-- Add this after the upper_arm link -->

<!-- ==================== LINK 3: FOREARM ==================== -->
<link name="forearm">
  <visual>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.03" length="0.3"/>
    </geometry>
    <material name="orange"/>
  </visual>
  <collision>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.035" length="0.32"/>
    </geometry>
  </collision>
  <inertial>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <mass value="1.0"/>
    <inertia
      ixx="0.008" ixy="0.0" ixz="0.0"
      iyy="0.008" iyz="0.0"
      izz="0.0005"/>
  </inertial>
</link>

<!-- ==================== JOINT: ELBOW ==================== -->
<joint name="elbow_joint" type="revolute">
  <parent link="upper_arm"/>
  <child link="forearm"/>
  <origin xyz="0 0 0.4" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit
    lower="0.0"
    upper="2.6"
    effort="30.0"
    velocity="1.5"/>
  <dynamics damping="0.3" friction="0.05"/>
</joint>
```

Now forward kinematics computes the forearm tip position from both joint angles:

```
pose_tip = FK(θ_shoulder, θ_elbow)
```

And inverse kinematics finds both angles to reach a target:

```
(θ_shoulder, θ_elbow) = IK(target_pose)
```

---

## Section Summary

In this section, we explored the mathematical foundations and practical XML structure of URDF:

**Kinematics:**
- **Forward kinematics** computes end-effector pose from joint angles (always solvable)
- **Inverse kinematics** computes joint angles from desired pose (may have zero, one, or many solutions)
- URDF provides all geometric information needed for kinematic calculations

**Joint Types:**
- **Revolute**: Bounded rotation—elbows, knees, fingers
- **Continuous**: Unlimited rotation—wheels, some wrists
- **Prismatic**: Linear sliding—lifts, telescopes
- **Fixed**: No motion—sensor mounts, structural connections

**URDF XML Structure:**
- `<robot>` root element containing all definitions
- `<material>` for visual appearance
- `<link>` with visual, collision, and inertial properties
- `<joint>` connecting parent to child with type-specific parameters

---

## Section Review Questions

1. A humanoid robot's hand is at position (0.5, 0.3, 0.8) meters. Is this a forward kinematics or inverse kinematics problem? Explain.

2. Why might inverse kinematics have multiple solutions for the same target position? Give a specific example with a humanoid arm.

3. You need to model a robot wrist that can rotate continuously for cable winding. Should you use a revolute or continuous joint? What would change in the URDF?

4. Write the URDF XML for a fixed joint that mounts a camera (`camera_link`) to a robot's head (`head_link`), positioned 5cm forward and 3cm up, tilted down by 15 degrees.

---

## Visual vs Collision: The Dual Geometry System

Every link in URDF can define two separate geometries: **visual** for appearance and **collision** for physics. Understanding why these are separate—and how to use them effectively—is crucial for building robots that both look realistic and simulate efficiently.

### Why Separate Visual and Collision?

Consider a humanoid robot's hand with detailed finger geometry:

```
┌─────────────────────────────────────────────────────────────────────────┐
│              VISUAL vs COLLISION GEOMETRY                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   VISUAL MESH (for rendering)          COLLISION MESH (for physics)    │
│                                                                         │
│   ╭─────────────────────╮              ┌─────────────────────┐         │
│   │ ╭───╮ ╭───╮ ╭───╮   │              │                     │         │
│   │ │   │ │   │ │   │   │              │                     │         │
│   │ │   │ │   │ │   │   │              │                     │         │
│   │ ╰───╯ ╰───╯ ╰───╯   │              │                     │         │
│   │    ╭───╮ ╭───╮      │              │                     │         │
│   │    │   │ │   │      │     ───►     │                     │         │
│   │    │   │ │   │      │              │                     │         │
│   │    ╰───╯ ╰───╯      │              │                     │         │
│   │  ╭───────────────╮  │              │                     │         │
│   │  │               │  │              └─────────────────────┘         │
│   ╰──┴───────────────┴──╯                                              │
│                                                                         │
│   150,000 triangles                    Single box primitive            │
│   Every knuckle, nail detail           Fast collision detection        │
│   Renders beautifully                  Rough approximation OK          │
│   Slow for physics                     Real-time capable               │
│                                                                         │
│   USE FOR:                             USE FOR:                        │
│   • RViz visualization                 • Gazebo/Isaac physics          │
│   • Marketing renders                  • MoveIt motion planning        │
│   • Digital twin displays              • Safety monitoring             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Performance impact:**

| Mesh Complexity | Collision Check Time | Suitable For |
|-----------------|---------------------|--------------|
| 100 triangles | ~0.01 ms | Real-time control (1kHz) |
| 1,000 triangles | ~0.1 ms | Motion planning |
| 10,000 triangles | ~1 ms | Offline analysis |
| 100,000 triangles | ~10+ ms | Visualization only |

For a humanoid with 60+ links, using detailed visual meshes for collision would make real-time simulation impossible.

### Visual Geometry in Depth

The `<visual>` element defines what you see in visualization tools:

```xml
<link name="forearm">
  <visual name="forearm_visual">
    <!-- Position and orientation relative to link frame -->
    <origin xyz="0 0 0.15" rpy="0 0 0"/>

    <!-- The actual geometry -->
    <geometry>
      <mesh filename="package://humanoid_description/meshes/forearm.dae"
            scale="1.0 1.0 1.0"/>
    </geometry>

    <!-- Appearance -->
    <material name="skin">
      <color rgba="0.96 0.80 0.69 1.0"/>
    </material>
  </visual>
</link>
```

**Supported geometry types:**

```xml
<!-- Primitives (fast to render, always available) -->
<geometry><box size="0.1 0.2 0.3"/></geometry>
<geometry><cylinder radius="0.05" length="0.2"/></geometry>
<geometry><sphere radius="0.08"/></geometry>

<!-- Mesh files (detailed appearance) -->
<geometry>
  <mesh filename="package://my_robot/meshes/arm.stl"/>
</geometry>
<geometry>
  <mesh filename="package://my_robot/meshes/arm.dae" scale="0.001 0.001 0.001"/>
</geometry>
```

**Mesh file formats:**

| Format | Features | Best For |
|--------|----------|----------|
| `.stl` | Geometry only | Simple parts, 3D prints |
| `.dae` (Collada) | Geometry + materials + textures | Detailed robots |
| `.obj` | Geometry + materials | CAD exports |

**Multiple visuals per link:**

A single link can have multiple visual elements for complex appearances:

```xml
<link name="upper_arm">
  <!-- Main arm structure -->
  <visual name="arm_shell">
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry><cylinder radius="0.05" length="0.3"/></geometry>
    <material name="plastic_white"/>
  </visual>

  <!-- Decorative stripe -->
  <visual name="arm_stripe">
    <origin xyz="0.051 0 0.15" rpy="0 0 0"/>
    <geometry><box size="0.002 0.02 0.25"/></geometry>
    <material name="accent_blue"/>
  </visual>

  <!-- Joint cover -->
  <visual name="shoulder_cover">
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry><sphere radius="0.06"/></geometry>
    <material name="plastic_gray"/>
  </visual>
</link>
```

### Collision Geometry in Depth

The `<collision>` element defines the shape used for physics simulation and motion planning:

```xml
<link name="forearm">
  <collision name="forearm_collision">
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <!-- Simplified geometry for fast computation -->
      <cylinder radius="0.055" length="0.32"/>
    </geometry>
  </collision>
</link>
```

**Collision geometry strategies:**

**1. Primitive Bounding**
Use a single primitive that fully contains the visual geometry:

```xml
<!-- Visual: detailed mesh -->
<visual>
  <geometry><mesh filename="package://robot/meshes/hand_detailed.dae"/></geometry>
</visual>

<!-- Collision: simple box -->
<collision>
  <geometry><box size="0.12 0.08 0.15"/></geometry>
</collision>
```

**2. Primitive Composition**
Combine multiple primitives for better approximation:

```xml
<link name="torso">
  <!-- Main body -->
  <collision name="torso_main">
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
    <geometry><box size="0.3 0.2 0.4"/></geometry>
  </collision>

  <!-- Left shoulder bulge -->
  <collision name="shoulder_left">
    <origin xyz="0 0.18 0.38" rpy="0 0 0"/>
    <geometry><sphere radius="0.08"/></geometry>
  </collision>

  <!-- Right shoulder bulge -->
  <collision name="shoulder_right">
    <origin xyz="0 -0.18 0.38" rpy="0 0 0"/>
    <geometry><sphere radius="0.08"/></geometry>
  </collision>
</link>
```

**3. Convex Hull Decomposition**
For complex shapes, decompose into convex hulls using tools like V-HACD:

```xml
<collision name="complex_part_hull_0">
  <geometry><mesh filename="package://robot/collision/part_hull_0.stl"/></geometry>
</collision>
<collision name="complex_part_hull_1">
  <geometry><mesh filename="package://robot/collision/part_hull_1.stl"/></geometry>
</collision>
<!-- ... more hulls ... -->
```

**Collision margin considerations:**

Make collision geometry slightly larger than visual geometry for safety:

```
┌─────────────────────────────────────────────────┐
│           COLLISION MARGIN                      │
├─────────────────────────────────────────────────┤
│                                                 │
│         Collision boundary                      │
│         ┌─────────────────────┐                │
│         │                     │                │
│         │   Visual geometry   │                │
│         │   ┌─────────────┐   │                │
│         │   │             │   │ ← 5mm margin   │
│         │   │             │   │   each side    │
│         │   └─────────────┘   │                │
│         │                     │                │
│         └─────────────────────┘                │
│                                                 │
│   Prevents visual interpenetration             │
│   Accounts for sensor/control uncertainty      │
│                                                 │
└─────────────────────────────────────────────────┘
```

```xml
<!-- Visual: exact size -->
<visual>
  <geometry><cylinder radius="0.050" length="0.300"/></geometry>
</visual>

<!-- Collision: 5mm larger radius, 10mm longer -->
<collision>
  <geometry><cylinder radius="0.055" length="0.310"/></geometry>
</collision>
```

---

## Inertial Properties: Physics Simulation Foundations

The `<inertial>` element defines mass properties essential for dynamic simulation. Without accurate inertial properties, physics engines like **Gazebo** and **Isaac Sim** cannot correctly simulate how your robot moves, balances, and responds to forces.

### Why Inertial Properties Matter

Consider what happens during simulation without correct inertial data:

| Missing/Wrong Property | Simulation Effect |
|-----------------------|-------------------|
| No mass | Link treated as massless; unrealistic dynamics |
| Wrong mass | Incorrect accelerations; balance failure |
| Wrong center of mass | Robot tips over unexpectedly |
| Wrong inertia tensor | Incorrect rotational behavior; wobbling |

For humanoid robots, **balance depends critically on accurate mass distribution**. A simulated humanoid won't walk if its inertial properties don't match reality.

### Anatomy of the Inertial Element

```xml
<link name="upper_arm">
  <inertial>
    <!-- Center of mass location relative to link origin -->
    <origin xyz="0 0 0.15" rpy="0 0 0"/>

    <!-- Total mass in kilograms -->
    <mass value="2.5"/>

    <!-- Inertia tensor (symmetric 3x3 matrix) -->
    <inertia
      ixx="0.025" ixy="0.0"   ixz="0.0"
                  iyy="0.025" iyz="0.0"
                              izz="0.003"/>
  </inertial>
</link>
```

### Center of Mass (CoM)

The `<origin>` within `<inertial>` specifies where the center of mass is located:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CENTER OF MASS PLACEMENT                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Link Origin at joint               Center of mass offset              │
│        │                                                                │
│        ▼                             <origin xyz="0 0 0.15"/>          │
│   ┌────●────────────────────┐                                          │
│   │                         │        CoM is 0.15m along Z from         │
│   │                         │        the link's origin                 │
│   │          ⊕ ←── CoM      │                                          │
│   │                         │        For uniform cylinder:             │
│   │                         │        CoM at geometric center           │
│   │                         │                                          │
│   └─────────────────────────┘        For non-uniform parts:            │
│                                      CoM from CAD or measurement       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Finding the center of mass:**

1. **Uniform primitives**: CoM is at the geometric center
2. **CAD models**: Most CAD software calculates CoM automatically
3. **Physical measurement**: Balance the actual part on a point
4. **Composite bodies**: Weighted average of component CoMs

### Mass

The `<mass>` element specifies total mass in kilograms:

```xml
<mass value="2.5"/>  <!-- 2.5 kg -->
```

**Typical humanoid link masses:**

| Link | Mass Range | Notes |
|------|-----------|-------|
| Head | 3-5 kg | Includes sensors, cameras |
| Torso | 15-25 kg | Heaviest; contains electronics |
| Upper arm | 1.5-3 kg | Per arm |
| Forearm | 1-2 kg | Per arm |
| Hand | 0.3-0.8 kg | Per hand |
| Thigh | 4-8 kg | Per leg |
| Shin | 2-4 kg | Per leg |
| Foot | 1-2 kg | Per foot |
| **Total** | **40-80 kg** | Full humanoid |

### Inertia Tensor

The inertia tensor describes how mass is distributed and affects rotational dynamics. It's a symmetric 3×3 matrix:

```
        ┌                    ┐
        │ Ixx   Ixy   Ixz    │
  I  =  │ Ixy   Iyy   Iyz    │
        │ Ixz   Iyz   Izz    │
        └                    ┘
```

In URDF, you specify six unique values (since Ixy=Iyx, etc.):

```xml
<inertia
  ixx="0.025" ixy="0.0"   ixz="0.0"
              iyy="0.025" iyz="0.0"
                          izz="0.003"/>
```

**Understanding inertia components:**

- **Ixx, Iyy, Izz**: Moments of inertia about each axis (always positive)
- **Ixy, Ixz, Iyz**: Products of inertia (can be negative; zero for symmetric objects aligned with axes)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INERTIA TENSOR INTUITION                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   High Ixx = Hard to rotate around X axis                              │
│                                                                         │
│         Y                              Y                                │
│         │    Izz small                 │    Izz large                  │
│         │    (easy to spin)            │    (hard to spin)             │
│         │                              │                                │
│    ─────┼───── X                  ─────┼───── X                        │
│         │   ╱                          │                                │
│         │  ╱ Z                         │  ╱ Z                          │
│        ╱│                             ╱│                                │
│       ╱ │                            ╱ │                                │
│         ●  Thin rod                 ●━━━●  Disk (like a wheel)         │
│         │  along Z                     │                                │
│         │                              │                                │
│                                                                         │
│   Rod: Izz ≈ 0, Ixx = Iyy = mL²/12                                     │
│   Disk: Izz = mr²/2, Ixx = Iyy = mr²/4                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Calculating Inertia for Common Shapes

**Solid rectangular box** (dimensions x, y, z; mass m):

```
Ixx = m(y² + z²)/12
Iyy = m(x² + z²)/12
Izz = m(x² + y²)/12
Ixy = Ixz = Iyz = 0
```

**Solid cylinder** (radius r, length h along Z; mass m):

```
Ixx = Iyy = m(3r² + h²)/12
Izz = mr²/2
Ixy = Ixz = Iyz = 0
```

**Solid sphere** (radius r; mass m):

```
Ixx = Iyy = Izz = 2mr²/5
Ixy = Ixz = Iyz = 0
```

### Example: Complete Link with Physics Properties

Here's a realistic upper arm link for a humanoid:

```xml
<link name="left_upper_arm">

  <!-- VISUAL: Detailed mesh for appearance -->
  <visual name="upper_arm_visual">
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <mesh filename="package://humanoid/meshes/visual/upper_arm.dae"/>
    </geometry>
    <material name="robot_skin"/>
  </visual>

  <!-- COLLISION: Simplified capsule approximation -->
  <collision name="upper_arm_collision">
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.05" length="0.28"/>
    </geometry>
  </collision>

  <!-- Spherical cap at shoulder end -->
  <collision name="upper_arm_shoulder_cap">
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.055"/>
    </geometry>
  </collision>

  <!-- Spherical cap at elbow end -->
  <collision name="upper_arm_elbow_cap">
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.045"/>
    </geometry>
  </collision>

  <!-- INERTIAL: Physics properties from CAD -->
  <inertial>
    <origin xyz="0 0.005 -0.14" rpy="0 0 0"/>  <!-- Slightly off-center CoM -->
    <mass value="2.1"/>  <!-- 2.1 kg -->
    <inertia
      ixx="0.0196"  ixy="0.0001"  ixz="0.0"
                    iyy="0.0189"  iyz="0.0003"
                                  izz="0.0028"/>
  </inertial>

</link>
```

### Tools for Computing Inertial Properties

**From CAD software:**
- SolidWorks: Evaluate → Mass Properties
- Fusion 360: Inspect → Component Properties
- FreeCAD: Part → Check Geometry

**From mesh files:**
```bash
# Using MeshLab
meshlab model.stl
# Filters → Quality Measures → Compute Geometric Measures

# Using trimesh (Python)
python -c "
import trimesh
mesh = trimesh.load('model.stl')
print(f'Volume: {mesh.volume}')
print(f'Center of mass: {mesh.center_mass}')
print(f'Inertia tensor:\n{mesh.moment_inertia}')
"
```

**From URDF (estimate from primitives):**
```bash
# Using the urdf_inertia_calculator package
ros2 run urdf_inertia_calculator calculate_inertia --urdf robot.urdf
```

### Isaac Sim Considerations

NVIDIA Isaac Sim uses PhysX, which has specific requirements for inertial properties:

**1. Minimum inertia values:**
```xml
<!-- Avoid very small inertia values that cause instability -->
<inertia ixx="0.001" .../>  <!-- Minimum ~0.001 for stability -->
```

**2. Inertia scaling:**
Isaac Sim may require tuning inertia for stable simulation:
```python
# In Isaac Sim Python API
prim.GetAttribute("physics:diagonalInertia").Set(Gf.Vec3f(0.01, 0.01, 0.005))
```

**3. Mass ratios:**
Adjacent links shouldn't have extreme mass ratios:
```
# Good: masses within 10x of each other
torso: 20 kg, arm: 2.5 kg  (ratio = 8x) ✓

# Problematic: extreme ratios cause instability
torso: 20 kg, finger: 0.01 kg  (ratio = 2000x) ✗
```

---

## Putting It All Together: A Physics-Ready Link

Here's a complete example showing visual, collision, and inertial properties working together:

```xml
<?xml version="1.0"?>
<robot name="physics_example">

  <material name="aluminum">
    <color rgba="0.8 0.8 0.85 1.0"/>
  </material>

  <link name="robot_forearm">

    <!--
      VISUAL: High-detail mesh for realistic rendering
      - Used by RViz, Gazebo GUI, Isaac Sim viewport
      - No impact on physics simulation speed
    -->
    <visual name="forearm_shell">
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://robot/meshes/forearm_visual.dae"
              scale="0.001 0.001 0.001"/>
      </geometry>
      <material name="aluminum"/>
    </visual>

    <!--
      COLLISION: Simplified geometry for fast physics
      - Used by Gazebo physics, Isaac Sim PhysX, MoveIt planning
      - Multiple primitives approximate the shape
    -->

    <!-- Main forearm cylinder -->
    <collision name="forearm_main">
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.23"/>
      </geometry>
    </collision>

    <!-- Wrist bulge -->
    <collision name="forearm_wrist">
      <origin xyz="0 0 0.24" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.035"/>
      </geometry>
    </collision>

    <!-- Elbow connection -->
    <collision name="forearm_elbow">
      <origin xyz="0 0 0.01" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.042"/>
      </geometry>
    </collision>

    <!--
      INERTIAL: Mass properties for dynamics
      - Used by physics engines for F=ma, torque calculations
      - Critical for balance, manipulation, locomotion
    -->
    <inertial>
      <!-- Center of mass slightly toward elbow (denser motors there) -->
      <origin xyz="0 0 0.11" rpy="0 0 0"/>

      <!-- Total mass including internal components -->
      <mass value="1.8"/>

      <!-- Inertia tensor computed from CAD model -->
      <inertia
        ixx="0.0098"  ixy="0.0"     ixz="0.0"
                      iyy="0.0095"  iyz="0.0"
                                    izz="0.0012"/>
    </inertial>

  </link>

</robot>
```

---

## Chapter Summary

This chapter covered the complete process of designing robot bodies using URDF, from basic structure to physics-ready models.

### Links and Geometry

**Links** are the rigid bodies that make up your robot. Each link can define:

- **Visual geometry**: High-detail meshes or primitives for realistic appearance in visualization tools and simulators. Visual geometry has no impact on physics performance—use detailed meshes freely for good-looking robots.

- **Collision geometry**: Simplified shapes used for physics simulation and motion planning. Keep collision geometry simple (primitives or low-poly meshes) to maintain real-time performance. Use multiple primitives to approximate complex shapes while staying computationally efficient.

- **Inertial properties**: Mass, center of mass, and inertia tensor required for dynamic simulation. Accurate inertial properties are essential for realistic physics—without them, your robot won't balance, walk, or manipulate objects correctly.

### Joints and Kinematics

**Joints** connect links and define their relative motion:

- **Revolute joints** provide bounded rotation for elbows, knees, and most humanoid articulations
- **Continuous joints** provide unlimited rotation for wheels and some wrists
- **Prismatic joints** provide linear motion for lifts and telescoping mechanisms
- **Fixed joints** rigidly connect links for sensor mounts and structural elements

**Kinematics** describes the relationship between joint angles and end-effector positions:

- **Forward kinematics** computes where the end-effector is given joint angles (always solvable)
- **Inverse kinematics** computes what joint angles achieve a desired position (may have zero, one, or many solutions)

### Transmissions and Control

**Transmissions** map actuators to joints, accounting for:

- Gear ratios that trade speed for torque
- Different hardware interfaces (effort, velocity, position control)
- Integration with ros2_control for real-time control

### The Complete Picture

A well-designed URDF serves as the single source of truth for your robot:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    URDF IN THE ROBOT ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           URDF FILE                                     │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                     │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │
│   │   Visual    │    │  Collision  │    │  Inertial   │               │
│   │  Geometry   │    │  Geometry   │    │ Properties  │               │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘               │
│          │                  │                   │                      │
│          ▼                  ▼                   ▼                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │
│   │    RViz     │    │   MoveIt    │    │   Gazebo    │               │
│   │ Visualization│    │  Planning   │    │  Isaac Sim  │               │
│   └─────────────┘    └─────────────┘    └─────────────┘               │
│                                                                         │
│   Same URDF → Consistent behavior across all tools                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Chapter Review Questions

1. **Visual vs Collision Geometry**: A humanoid robot's hand has intricate finger geometry with 50,000 triangles in the visual mesh. Explain why you would NOT use this mesh for collision detection, and describe two strategies for creating appropriate collision geometry.

2. **Inertial Properties**: A robot simulation shows the torso tilting unexpectedly during walking. The visual appearance looks correct. Which inertial property is most likely misconfigured, and how would you diagnose and fix it?

3. **Complete Link Design**: You're adding a new sensor module (a 3D camera) to a humanoid robot's head. The camera weighs 0.3 kg and has dimensions 10cm × 3cm × 3cm. Write the complete URDF `<link>` element including visual (box primitive), collision (box with 5mm margin), and inertial properties (assume uniform density).

4. **Physics Simulation**: Explain why physics engines like Isaac Sim require accurate inertia tensors. What would happen if you set all inertia values to a very small number (e.g., 0.0001) for every link?

---

## Next Steps

With URDF fundamentals mastered, you're ready to tackle more advanced topics:

**Chapter 3: Simulation Environments**
- Setting up Gazebo and Isaac Sim
- Adding sensors (cameras, IMUs, force/torque)
- Physics tuning for realistic behavior

**Chapter 4: Motion Planning with MoveIt**
- Configuring MoveIt for your URDF
- Collision-aware trajectory planning
- Integration with perception systems

**Chapter 5: Control Systems**
- ros2_control architecture
- PID tuning for joint control
- Whole-body control for humanoids

---

## Further Reading

- [URDF XML Specification](http://wiki.ros.org/urdf/XML) - Complete reference for all URDF elements
- [SDF Format](http://sdformat.org/) - Simulation Description Format used by Gazebo
- [Isaac Sim URDF Importer](https://docs.omniverse.nvidia.com/isaacsim/latest/features/environment_setup/ext_omni_isaac_urdf.html) - Importing URDF into Isaac Sim
- [MoveIt URDF Setup](https://moveit.picknik.ai/main/doc/examples/urdf_srdf/urdf_srdf_tutorial.html) - Configuring URDF for motion planning
- *Robot Modeling and Control* by Spong, Hutchinson, and Vidyasagar - Comprehensive kinematics and dynamics theory
- *Springer Handbook of Robotics* - Chapter on robot modeling and simulation
