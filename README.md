# 🤖 AI-Based Autonomous Navigation System

<div align="center">

### Smart Path Planning | Dynamic Obstacle Avoidance | Computer Vision

A Python-based robotics simulation demonstrating autonomous navigation,
A* path planning, obstacle avoidance, and YOLO object detection.

🎬 **[Watch the Project Demonstration on YouTube](https://youtu.be/DoCU9v2J9Dk)**

</div>

---

---

## 1. Project Overview

This project demonstrates an AI-based autonomous navigation system using Python.
A simulated mobile robot navigates a two-dimensional grid containing obstacles
and attempts to reach a target destination.

The project demonstrates A* path planning, robot movement, obstacle handling,
route recalculation, visualization, and navigation performance measurement.

A separate live-camera program uses YOLO object detection to identify objects
in a webcam feed.

**Important:** Live-camera detection is a separate program. It is not currently
connected to the simulated robot as a complete real-time navigation system.

---

## 2. Features

- A* path-planning algorithm
- Autonomous robot movement in a grid environment
- Static obstacle avoidance
- Manual obstacle insertion
- Route recalculation when the next position is blocked
- Pygame-based simulation and visualization
- Robot position and navigation status display
- Navigation performance metrics
- Automated tests using pytest
- Live webcam object detection using YOLO
- Object labels and bounding boxes
- Center-region warnings for detected objects

---

## 3. Technologies Used

- Python 3.11
- Pygame
- pytest
- Ultralytics YOLO
- OpenCV
- Git and GitHub

---

## 4. Project Structure

```text
ai autonomous navigation/
├── simulation/
│   ├── __init__.py
│   ├── environment.py
│   └── robot.py
├── src/
│   ├── ai_navigation.py
│   ├── metrics.py
│   ├── navigation.py
│   ├── object_detection.py
│   └── path_planning.py
├── tests/
├── screenshot/
│   ├── navigation dashboard.png
│   ├── navigation obstacle.png
│   ├── live camera detection.png
│   └── test passed.png
├── camera_test.py
├── live_object_detection.py
├── path_planning.py
├── visual_simulation.py
├── requirements.txt
├── README.md
├── .gitignore
└── 1010.mp4
```

**Note:** The project structure above describes the main project files and
screenshots. Additional files may be present in the repository.

YOLO model weights are stored locally and are not included in the repository.

---

## 5. Requirements

- Python 3.11
- A computer capable of running Pygame
- A webcam for live object detection
- Internet access may be required to install Python packages and download
  YOLO model weights if they are not already available locally

The virtual simulation does not require a physical robot or GPU.

---

## 6. Installation

Open a terminal in the project directory.

### Step 1: Check Python

```powershell
py -3.11 --version
```

### Step 2: Install dependencies

```powershell
py -3.11 -m pip install -r requirements.txt
```

Wait for the installation to finish.

---

## 7. Run the Virtual Simulation

Run the following command from the project directory:

```powershell
py -3.11 visual_simulation.py
```

The simulation displays a grid, robot, destination, obstacles, planned route,
and navigation information.

### Simulation Controls

| Key | Action |
|---|---|
| D | Run object detection on the configured image and add demonstration obstacles |
| O | Add a manual obstacle |
| R | Reset the simulation |
| SPACE | Pause or resume the simulation |
| Close window | Exit the simulation |

The image used by the D key must exist at the image path configured in
`visual_simulation.py`.

The obstacles added after image detection are demonstration obstacles.
They are not mapped to the actual locations of objects in the image.

---

## 8. Run Live Camera Object Detection

Connect a webcam and run:

```powershell
py -3.11 live_object_detection.py
```

The program uses YOLO to detect objects in the webcam feed. Detected objects
are displayed with bounding boxes and labels.

The program also displays a warning when objects are detected in the center
region of the image.

Press **Q** to exit the camera program.

The center-region warning is based on image position. It does not measure
physical distance or guarantee collision avoidance.

**Note:** The camera detection program operates separately from the virtual
navigation simulation.

---

## 9. Run Automated Tests

Run the tests from the project directory:

```powershell
py -3.11 -m pytest -v
```

The project previously reported 13 passing tests in the development
environment.

Run the command above to verify the current version.

---

## 10. Navigation Algorithm

The simulation uses the A* path-planning algorithm to search for a route
between the robot's starting position and the destination.

The robot follows the calculated path through walkable grid cells.

When the next position becomes blocked, the simulation attempts to calculate
a new route.

If no route can be found, the simulation reports that no path is available.

---

## 11. Limitations

- The robot is simulated in a two-dimensional grid.
- The live-camera detector is separate from the virtual simulation.
- Camera detections are not currently converted into accurately localized
  grid obstacles.
- The center-region warning does not estimate object distance.
- YOLO may misclassify objects or fail to detect them.
- No physical robot or motor-control integration is included in the current
  simulation workflow.

---

## 12. Future Improvements

- Connect camera detections to the navigation environment.
- Estimate object distance using suitable sensors or computer-vision methods.
- Map detected obstacles to appropriate grid positions.
- Improve dynamic path planning and obstacle avoidance.
- Add additional navigation metrics and visual reports.
- Integrate suitable sensors and motor controls for a physical robot.
- Evaluate detection and navigation performance in different environments.

---

## 13. Safety and Scope

This project is a software simulation and demonstration of object detection.
It should not be considered a safety-certified autonomous navigation system.

A real robot would require additional sensing, control, testing, and safety
mechanisms before operating around people.

---

## 14. Author

**Name:** Pranab Das

**Project Title:** AI-Based Autonomous Navigation System

**Program / Organization:** IIP(INDIAN INSTITUTE OF PLACEMENT)

**College Department:** Commerce

**Educational Qualification:** Bachelor of Commerce (B.Com),
Gauhati Commerce College

**GitHub Repository:** [AI Autonomous Navigation](https://github.com/mepranab/Ai-autonomous-navigation)

---

## 15. Project Screenshots

### 15.1 Autonomous Navigation Dashboard

The dashboard displays the robot's position, planned route, destination,
obstacles, and navigation performance metrics.

![Navigation Dashboard](screenshot/navigation%20dashboard.png)

### 15.2 Robot Navigation and Obstacle Avoidance

The simulation demonstrates path planning and obstacle avoidance.

![Navigation Obstacle](screenshot/navigation%20obstacle.png)

### 15.3 Live Camera Object Detection

The separate camera detection program uses YOLO and OpenCV to identify
objects and display bounding boxes.

![Live Camera Detection](screenshot/live%20camera%20detection.png)

### 15.4 Automated Test Results

The recorded test run completed with 13 passing tests.

![Automated Test Results](screenshot/test%20passed.png)

---

## 16. Project Demonstration Video

Watch the AI-Based Autonomous Navigation System in action.

▶️ **[Watch the Project Demo on YouTube](https://youtu.be/DoCU9v2J9Dk)**

The demonstration video showcases the project interface and navigation
workflow.

The original video is also available in the repository as `1010.mp4`.

---

## 17. Acknowledgement

This project was developed as part of a learning experience in Python
programming, autonomous navigation concepts, path planning, simulation,
and computer vision.

---

<div align="center">

**AI-Based Autonomous Navigation System**

*Learning • Building • Testing • Improving*

</div>