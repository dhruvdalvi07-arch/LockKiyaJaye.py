# LockKiyaJaye.py

A feature-rich, object-oriented command-line trivia game inspired by *Kaun Banega Crorepati* (and *Who Wants to Be a Millionaire?*). Built entirely in Python using standard libraries, it includes timed responses, dynamic prize ladders, multiple lifelines, and persistent leaderboard tracking.

---

## Features

- **Authentic 15-Level Prize Ladder:** Climb from ₹1,000 to the grand jackpot of ₹7,00,00,000 (7 Crore).
- **Safety Nets / Milestones:** Secure minimum prize thresholds at **Level 5 (₹10,000)** and **Level 10 (₹3,20,000)**.
- **Dynamic "Tik-Tiki" Timer:**
  - **Levels 1–5:** 30-second countdown.
  - **Levels 6–10:** 45-second countdown.
  - **Levels 11–15:** Unlimited time to deliberate.
- **5 Realistic Lifelines:**
  - **50:50:** Eliminates two incorrect options.
  - **Audience Poll:** Simulates weighted audience distribution visualized with ANSI bar charts.
  - **Ask the Expert:** Connects with an AI specialist who provides an option along with a confidence rating.
  - **Flip Question:** Replaces the current question with one from a reserve pool.
  - **Double Dip:** Grants two consecutive attempts to answer the current question (locks out the option to quit).
- **Persistent Leaderboard:** Saves game statistics (`kbc_leaderboard.json`), retaining the top 10 scores with player name, winnings, milestone, and timestamp.
- **Zero Third-Party Dependencies:** Runs on standard Python 3.8+ libraries (`threading`, `json`, `dataclasses`, `time`, `random`).

---

## Prize Structure

| Level | Prize Money | Milestone / Note |
| :--- | :--- | :--- |
| 1 | ₹1,000 | 30s Timer |
| 2 | ₹2,000 | 30s Timer |
| 3 | ₹3,000 | 30s Timer |
| 4 | ₹5,000 | 30s Timer |
| **5** | **₹10,000** | **Milestone 1 (Guaranteed)** |
| 6 | ₹20,000 | 45s Timer |
| 7 | ₹40,000 | 45s Timer |
| 8 | ₹80,000 | 45s Timer |
| 9 | ₹1,60,000 | 45s Timer |
| **10** | **₹3,20,000** | **Milestone 2 (Guaranteed)** |
| 11 | ₹6,40,000 | Unlimited Time |
| 12 | ₹12,50,000 | Unlimited Time |
| 13 | ₹25,00,000 | Unlimited Time |
| 14 | ₹50,00,000 | Unlimited Time |
| **15** | **₹7,00,00,000** | **Grand Jackpot (7 Crore)** |

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/dhruvdalvi07-arch/LockKiyaJaye.py.git](https://github.com/dhruvdalvi07-arch/LockKiyaJaye.py.git)
   cd LockKiyaJaye.py
