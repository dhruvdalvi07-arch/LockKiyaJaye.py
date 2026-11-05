import os
import sys
import json
import time
import random
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

# ==============================================================================
# ANSI STYLING UTILITIES
# ==============================================================================
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"


# ==============================================================================
# NON-BLOCKING TIMED INPUT (CROSS-PLATFORM THREADING)
# ==============================================================================
class TimedInput:
    """Collects user input within a specified timeout using a daemon thread."""
    def __init__(self):
        self.input_value: Optional[str] = None
        self.timed_out: bool = False

    def _reader(self, prompt: str):
        try:
            self.input_value = input(prompt)
        except (EOFError, KeyboardInterrupt):
            self.input_value = None

    def get(self, prompt: str, timeout_sec: Optional[int]) -> Tuple[Optional[str], bool]:
        if timeout_sec is None:
            # Unlimited time (Level 11+)
            try:
                res = input(prompt)
                return res, False
            except (EOFError, KeyboardInterrupt):
                return None, False

        self.input_value = None
        self.timed_out = False

        thread = threading.Thread(target=self._reader, args=(prompt,), daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)

        if thread.is_alive():
            self.timed_out = True
            return None, True

        return self.input_value, False


# ==============================================================================
# DATA MODELS
# ==============================================================================
@dataclass
class Question:
    text: str
    options: Dict[str, str]
    correct_option: str
    explanation: str


@dataclass
class ScoreRecord:
    player_name: str
    prize_won: int
    level_reached: int
    lifelines_used: int
    timestamp: str


# ==============================================================================
# QUESTION REPOSITORY & SEED DATA
# ==============================================================================
DEFAULT_QUESTION_BANK = {
    "tier_1": [
        {
            "text": "Which planet is commonly referred to as the 'Red Planet'?",
            "options": {"A": "Venus", "B": "Mars", "C": "Jupiter", "D": "Saturn"},
            "correct_option": "B",
            "explanation": "Mars appears reddish due to ubiquitous iron oxide on its surface."
        },
        {
            "text": "In Python, which function converts an iterable into an enumerated index-value pair?",
            "options": {"A": "index()", "B": "pair()", "C": "enumerate()", "D": "zip()"},
            "correct_option": "C",
            "explanation": "enumerate() yields tuples of (index, item) during iteration."
        },
        {
            "text": "What is the capital city of Australia?",
            "options": {"A": "Sydney", "B": "Melbourne", "C": "Canberra", "D": "Perth"},
            "correct_option": "C",
            "explanation": "Canberra was chosen as the compromise capital in 1908."
        },
        {
            "text": "Which basic data structure functions strictly on a First-In, First-Out (FIFO) basis?",
            "options": {"A": "Stack", "B": "Queue", "C": "Binary Tree", "D": "Graph"},
            "correct_option": "B",
            "explanation": "Queues pop elements in the order they were inserted."
        },
        {
            "text": "Who is credited with the discovery of penicillin in 1928?",
            "options": {"A": "Alexander Fleming", "B": "Louis Pasteur", "C": "Edward Jenner", "D": "Robert Koch"},
            "correct_option": "A",
            "explanation": "Sir Alexander Fleming discovered antibacterial properties of penicillium mold."
        },
        {
            "text": "Which gas do plants absorb from the atmosphere for photosynthesis?",
            "options": {"A": "Oxygen", "B": "Nitrogen", "C": "Carbon Dioxide", "D": "Argon"},
            "correct_option": "C",
            "explanation": "Plants utilize carbon dioxide, water, and sunlight to synthesize glucose."
        }
    ],
    "tier_2": [
        {
            "text": "What is the standard IANA port number reserved for encrypted HTTPS web traffic?",
            "options": {"A": "80", "B": "22", "C": "443", "D": "8080"},
            "correct_option": "C",
            "explanation": "TCP port 443 is universally standardized for HTTPS/TLS traffic."
        },
        {
            "text": "Which chemical element holds the atomic number 79 and the Latin symbol 'Au'?",
            "options": {"A": "Silver", "B": "Gold", "C": "Platinum", "D": "Copper"},
            "correct_option": "B",
            "explanation": "Au derives from 'aurum', the Latin word denoting gold."
        },
        {
            "text": "Who established the laws of planetary motion, showing orbits are elliptical?",
            "options": {"A": "Johannes Kepler", "B": "Galileo Galilei", "C": "Isaac Newton", "D": "Nicolaus Copernicus"},
            "correct_option": "A",
            "explanation": "Kepler's First Law published in 1609 established elliptical planetary paths."
        },
        {
            "text": "Which Indian physicist was awarded the Nobel Prize in 1930 for light scattering?",
            "options": {"A": "Homi Bhabha", "B": "C.V. Raman", "C": "S. Chandrasekhar", "D": "S.N. Bose"},
            "correct_option": "B",
            "explanation": "Sir C.V. Raman's discovery is celebrated in India as National Science Day."
        },
        {
            "text": "In computer algorithms, which sorting algorithm has an average time complexity of O(n log n)?",
            "options": {"A": "Bubble Sort", "B": "Merge Sort", "C": "Insertion Sort", "D": "Selection Sort"},
            "correct_option": "B",
            "explanation": "Merge sort relies on divide-and-conquer to guarantee O(n log n) efficiency."
        },
        {
            "text": "Which peace treaty concluded the state of war between Germany and the Allied Powers in 1919?",
            "options": {"A": "Treaty of Paris", "B": "Treaty of Versailles", "C": "Treaty of Ghent", "D": "Brest-Litovsk"},
            "correct_option": "B",
            "explanation": "The Treaty of Versailles formally resolved the conflict of World War I."
        }
    ],
    "tier_3": [
        {
            "text": "In distributed architecture, what does Brewer's CAP theorem claim cannot be achieved simultaneously with Partition Tolerance?",
            "options": {"A": "Consistency & Performance", "B": "Consistency & Availability", "C": "Atomicity & Durability", "D": "Latency & Throughput"},
            "correct_option": "B",
            "explanation": "A distributed system can guarantee at most two: Consistency, Availability, Partition tolerance."
        },
        {
            "text": "Who was the first woman to be awarded the prestigious Fields Medal in Mathematics (2014)?",
            "options": {"A": "Maryam Mirzakhani", "B": "Emmy Noether", "C": "Ada Lovelace", "D": "Karen Uhlenbeck"},
            "correct_option": "A",
            "explanation": "Maryam Mirzakhani was awarded for contributions to Riemann surfaces and dynamics."
        },
        {
            "text": "What is the deepest verified bathymetric location inside the Mariana Trench?",
            "options": {"A": "Milwaukee Deep", "B": "Challenger Deep", "C": "Tonga Trench", "D": "Java Deep"},
            "correct_option": "B",
            "explanation": "Challenger Deep reaches approximately 10,994 meters below sea level."
        },
        {
            "text": "Which cellular component in the mammalian immune system directly secretes antibodies?",
            "options": {"A": "Cytotoxic T-Cells", "B": "Plasma B-Cells", "C": "Erythrocytes", "D": "Neutrophils"},
            "correct_option": "B",
            "explanation": "Differentiated B-lymphocytes (plasma cells) synthesize and secrete antibodies."
        },
        {
            "text": "Which Austro-American logician proved that axiomatic arithmetic cannot demonstrate its own consistency?",
            "options": {"A": "Kurt Gödel", "B": "Ludwig Wittgenstein", "C": "Rudolf Carnap", "D": "Alfred Tarski"},
            "correct_option": "A",
            "explanation": "Gödel's Incompleteness Theorems (1931) changed foundational mathematics."
        }
    ],
    "flip_pool": [
        {
            "text": "What is the capital city of Canada?",
            "options": {"A": "Toronto", "B": "Vancouver", "C": "Ottawa", "D": "Montreal"},
            "correct_option": "C",
            "explanation": "Ottawa was designated the capital by Queen Victoria in 1857."
        },
        {
            "text": "What unit measures electrical resistance in the International System of Units (SI)?",
            "options": {"A": "Watt", "B": "Ohm", "C": "Joule", "D": "Farad"},
            "correct_option": "B",
            "explanation": "The Ohm (Ω) is the SI unit representing electrical resistance."
        }
    ]
}


# ==============================================================================
# LEADERBOARD MANAGER
# ==============================================================================
class Leaderboard:
    FILE_PATH = "kbc_leaderboard.json"

    @classmethod
    def save(cls, record: ScoreRecord):
        scores = cls.load_raw()
        scores.append(asdict(record))
        # Sort descending by prize won
        scores.sort(key=lambda x: x["prize_won"], reverse=True)
        try:
            with open(cls.FILE_PATH, "w") as f:
                json.dump(scores[:10], f, indent=2)
        except IOError:
            pass

    @classmethod
    def load_raw(cls) -> List[dict]:
        if not os.path.exists(cls.FILE_PATH):
            return []
        try:
            with open(cls.FILE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @classmethod
    def display(cls):
        scores = cls.load_raw()
        print(f"\n{Style.BOLD}{Style.CYAN}=== ALL-TIME TOP 10 HALL OF FAME ==={Style.RESET}")
        if not scores:
            print("No records yet. Be the first to win!")
            return
        print(f"{'Rank':<5} {'Contestant':<18} {'Prize Won':<16} {'Milestone':<12} {'Date'}")
        print("-" * 65)
        for i, row in enumerate(scores, 1):
            date_str = row['timestamp'].split(" ")[0]
            print(f"{i:<5} {row['player_name'][:16]:<18} ₹{row['prize_won']:<15,} Q{row['level_reached']:<11} {date_str}")
        print("-" * 65)


# ==============================================================================
# LIFELINE ENGINE
# ==============================================================================
class LifelineEngine:
    def __init__(self):
        self.state = {
            "50:50": True,
            "Audience Poll": True,
            "Ask the Expert": True,
            "Flip Question": True,
            "Double Dip": True,
        }
        self.total_used = 0

    def is_available(self, name: str) -> bool:
        return self.state.get(name, False)

    def use(self, name: str):
        self.state[name] = False
        self.total_used += 1

    def list_available(self) -> List[str]:
        return [k for k, v in self.state.items() if v]


# ==============================================================================
# MAIN KBC GAME CLASS
# ==============================================================================
class KBCGameEngine:
    PRIZE_LADDER = [
        1_000, 2_000, 3_000, 5_000, 10_000,          # Levels 1-5 (Safe 1: ₹10,000)
        20_000, 40_000, 80_000, 160_000, 320_000,    # Levels 6-10 (Safe 2: ₹3,20,000)
        640_000, 1_250_000, 2_500_000, 5_000_000, 70_000_000 # Levels 11-15 (Jackpot)
    ]

    SAFETY_THRESHOLDS = {
        5: 10_000,
        10: 320_000,
        15: 70_000_000
    }

    def __init__(self, player_name: str):
        self.player_name = player_name
        self.current_idx = 0
        self.guaranteed_amount = 0
        self.lifelines = LifelineEngine()
        self.timed_input = TimedInput()
        self.flip_deck = [Question(**q) for q in DEFAULT_QUESTION_BANK["flip_pool"]]
        self.ladder_questions: List[Question] = self._prepare_ladder()

    def _prepare_ladder(self) -> List[Question]:
        """Samples questions across tiers to create a random game track."""
        t1 = [Question(**q) for q in DEFAULT_QUESTION_BANK["tier_1"]]
        t2 = [Question(**q) for q in DEFAULT_QUESTION_BANK["tier_2"]]
        t3 = [Question(**q) for q in DEFAULT_QUESTION_BANK["tier_3"]]

        random.shuffle(t1)
        random.shuffle(t2)
        random.shuffle(t3)

        # 5 from Tier 1, 5 from Tier 2, 5 from Tier 3
        return t1[:5] + t2[:5] + t3[:5]

    @staticmethod
    def _clear():
        os.system("cls" if os.name == "nt" else "clear")

    def _get_time_limit(self) -> Optional[int]:
        """Returns countdown seconds or None for unlimited."""
        if self.current_idx < 5:
            return 30
        elif self.current_idx < 10:
            return 45
        return None  # Hot seat level 11+ has no timer

    def _render_ui(self, question: Question, eliminated_keys: List[str], double_dip_active: bool):
        self._clear()
        prize = self.PRIZE_LADDER[self.current_idx]
        limit = self._get_time_limit()
        timer_text = f"{Style.RED}{limit}s limit{Style.RESET}" if limit else f"{Style.GREEN}Unlimited{Style.RESET}"

        print(f"{Style.BOLD}{Style.BLUE}=" * 68)
        print(f"  KAUN BANEGA CROREPATI  |  Contestant: {self.player_name}")
        print("=" * 68 + f"{Style.RESET}")
        print(f" Question: {Style.BOLD}{self.current_idx + 1} of 15{Style.RESET} | For: {Style.YELLOW}₹{prize:,}{Style.RESET}")
        print(f" Guaranteed: {Style.GREEN}₹{self.guaranteed_amount:,}{Style.RESET} | Clock: {timer_text}")
        if double_dip_active:
            print(f" {Style.MAGENTA}[ACTIVE LIFELINE: DOUBLE DIP ENGAGED - 2 ATTEMPTS]{Style.RESET}")
        print("-" * 68)

        print(f"\n{Style.BOLD}Q: {question.text}{Style.RESET}\n")
        for key in ["A", "B", "C", "D"]:
            if key in eliminated_keys:
                print(f"  {Style.RED}[{key}] --------------------------{Style.RESET}")
            else:
                print(f"  {Style.CYAN}[{key}]{Style.RESET} {question.options[key]}")
        print("-" * 68)

    # --------------------------------------------------------------------------
    # LIFELINE ACTIONS
    # --------------------------------------------------------------------------
    def _run_50_50(self, question: Question) -> List[str]:
        wrongs = [k for k in question.options.keys() if k != question.correct_option]
        hidden = random.sample(wrongs, 2)
        print(f"\n{Style.GREEN}[50:50] Two incorrect answers eliminated!{Style.RESET}")
        time.sleep(1)
        return hidden

    def _run_poll(self, question: Question, eliminated: List[str]):
        print(f"\n{Style.YELLOW}The studio audience is voting now...{Style.RESET}")
        time.sleep(1.2)
        valid = [k for k in question.options.keys() if k not in eliminated]
        correct = question.correct_option

        # Weight decreases slightly with higher tiers
        target_pct = max(42, 85 - (self.current_idx * 3))
        remaining = 100 - target_pct

        votes = {k: (target_pct if k == correct else 0) for k in valid}
        other_keys = [k for k in valid if k != correct]

        if other_keys:
            allocs = [random.randint(1, 100) for _ in other_keys]
            total_alloc = sum(allocs)
            for k, val in zip(other_keys, allocs):
                votes[k] = round((val / total_alloc) * remaining)

        diff = 100 - sum(votes.values())
        votes[correct] += diff

        print(f"\n{Style.BOLD}--- AUDIENCE POLL RESULTS ---{Style.RESET}")
        for k in ["A", "B", "C", "D"]:
            pct = votes.get(k, 0)
            bar = "█" * (pct // 4)
            print(f"  [{k}] {pct:3d}% | {Style.GREEN}{bar}{Style.RESET}")
        print("-" * 29)

    def _run_expert(self, question: Question, eliminated: List[str]):
        print(f"\n{Style.CYAN}Calling up the subject specialist...{Style.RESET}")
        time.sleep(1.5)
        valid = [k for k in question.options.keys() if k not in eliminated]
        chance = max(65, 95 - (self.current_idx * 2))

        if random.randint(1, 100) <= chance or question.correct_option not in valid:
            pick = question.correct_option
            conf = random.randint(85, 99)
        else:
            wrong_picks = [k for k in valid if k != question.correct_option]
            pick = random.choice(wrong_picks) if wrong_picks else question.correct_option
            conf = random.randint(50, 70)

        print(f"\n{Style.BOLD}Expert:{Style.RESET} 'I am {conf}% confident the answer is "
              f"{Style.YELLOW}[{pick}] {question.options[pick]}{Style.RESET}'.")

    # --------------------------------------------------------------------------
    # TURN LOOP
    # --------------------------------------------------------------------------
    def play_question(self, question: Question) -> Tuple[bool, bool]:
        """
        Returns: (passed: bool, player_quit: bool)
        """
        eliminated_keys: List[str] = []
        double_dip = False
        double_dip_attempts_left = 2

        while True:
            self._render_ui(question, eliminated_keys, double_dip)
            limit = self._get_time_limit()

            available_ll = self.lifelines.list_available()
            menu = f"[A/B/C/D] Select Answer"
            if available_ll and not double_dip:
                menu += f" | [L] Lifelines ({len(available_ll)})"
            if not double_dip:
                menu += " | [Q] Quit"
            print(menu)

            prompt = f"\nEnter your move ({limit}s clock): " if limit else "\nEnter your move: "
            choice, timed_out = self.timed_input.get(prompt, limit)

            if timed_out:
                print(f"\n\n{Style.RED}{Style.BOLD}⏰ TIME IS UP! The clock has stopped.{Style.RESET}")
                time.sleep(1.5)
                return False, False

            if not choice:
                continue

            choice = choice.strip().upper()

            # Quitting
            if choice == "Q" and not double_dip:
                confirm = input(f"{Style.YELLOW}Are you sure you want to walk away? (Y/N): {Style.RESET}").strip().upper()
                if confirm == "Y":
                    return False, True
                continue

            # Lifelines Menu
            elif choice == "L" and available_ll and not double_dip:
                print(f"\n{Style.BOLD}Available Lifelines:{Style.RESET}")
                for idx, name in enumerate(available_ll, 1):
                    print(f"  {idx}. {name}")
                print("  0. Cancel & Back")

                sub_choice = input("Select: ").strip()
                if not sub_choice.isdigit() or int(sub_choice) not in range(1, len(available_ll) + 1):
                    continue

                chosen_name = available_ll[int(sub_choice) - 1]
                self.lifelines.use(chosen_name)

                if chosen_name == "50:50":
                    eliminated_keys = self._run_50_50(question)
                elif chosen_name == "Audience Poll":
                    self._run_poll(question, eliminated_keys)
                elif chosen_name == "Ask the Expert":
                    self._run_expert(question, eliminated_keys)
                elif chosen_name == "Flip Question":
                    print(f"\n{Style.MAGENTA}Flipping current question...{Style.RESET}")
                    time.sleep(1)
                    if self.flip_deck:
                        question = self.flip_deck.pop(0)
                        eliminated_keys = []
                elif chosen_name == "Double Dip":
                    double_dip = True
                    print(f"\n{Style.MAGENTA}Double Dip activated. You must answer twice if the first is incorrect. Quitting disabled.{Style.RESET}")

                input(f"\nPress {Style.BOLD}[Enter]{Style.RESET} to resume...")
                continue

            # Answer Selection
            elif choice in ["A", "B", "C", "D"]:
                if choice in eliminated_keys:
                    print(f"\n{Style.RED}[!] That choice was already eliminated.{Style.RESET}")
                    time.sleep(1)
                    continue

                # Confirm answer
                confirm = input(f"Lock option [{choice}]: {question.options[choice]}? (Y/N): ").strip().upper()
                if confirm != "Y":
                    continue

                print(f"\n{Style.YELLOW}Locking in option [{choice}]...{Style.RESET}")
                time.sleep(1.2)

                if choice == question.correct_option:
                    won = self.PRIZE_LADDER[self.current_idx]
                    print(f"\n{Style.GREEN}{Style.BOLD}✔ CORRECT! You have won ₹{won:,}!{Style.RESET}")
                    print(f"Note: {question.explanation}")

                    # Check Milestone
                    step = self.current_idx + 1
                    if step in self.SAFETY_THRESHOLDS:
                        self.guaranteed_amount = self.SAFETY_THRESHOLDS[step]
                        print(f"{Style.YELLOW}★ Milestone Reached! Guaranteed Take-home: ₹{self.guaranteed_amount:,}{Style.RESET}")

                    input(f"\nPress {Style.BOLD}[Enter]{Style.RESET} to proceed...")
                    return True, False
                else:
                    if double_dip and double_dip_attempts_left > 1:
                        double_dip_attempts_left -= 1
                        eliminated_keys.append(choice)
                        print(f"\n{Style.RED}✘ INCORRECT! But Double Dip affords you 1 remaining attempt.{Style.RESET}")
                        input(f"Press {Style.BOLD}[Enter]{Style.RESET} to try again...")
                        continue

                    print(f"\n{Style.RED}{Style.BOLD}✘ INCORRECT!{Style.RESET}")
                    print(f"The right answer was {Style.GREEN}[{question.correct_option}] {question.options[question.correct_option]}{Style.RESET}")
                    print(f"Note: {question.explanation}")
                    time.sleep(1.5)
                    return False, False
            else:
                print("Invalid input.")
                time.sleep(0.5)

    # --------------------------------------------------------------------------
    # ENTRYPOINT
    # --------------------------------------------------------------------------
    def start(self):
        final_takehome = 0

        for idx in range(len(self.ladder_questions)):
            self.current_idx = idx
            question = self.ladder_questions[idx]

            passed, player_quit = self.play_question(question)

            if player_quit:
                final_takehome = self.PRIZE_LADDER[idx - 1] if idx > 0 else 0
                print(f"\n{Style.CYAN}You voluntarily retired from the game.{Style.RESET}")
                break

            if not passed:
                final_takehome = self.guaranteed_amount
                print(f"\n{Style.RED}You are eliminated from the hot seat.{Style.RESET}")
                break
        else:
            # If the loop finishes without breaking: all 15 cleared
            final_takehome = self.PRIZE_LADDER[-1]
            self._clear()
            print(f"{Style.BOLD}{Style.GREEN}*" * 68)
            print(f"  OUTSTANDING ACHIEVEMENT! YOU CLEARED ALL 15 QUESTIONS!")
            print(f"  {self.player_name.upper()} WINS THE GRAND JACKPOT: ₹{final_takehome:,}")
            print("*" * 68 + f"{Style.RESET}")

        print(f"\n{Style.BOLD}Final Winnings: ₹{final_takehome:,}{Style.RESET}")

        # Save to Leaderboard
        record = ScoreRecord(
            player_name=self.player_name,
            prize_won=final_takehome,
            level_reached=self.current_idx + (1 if final_takehome == self.PRIZE_LADDER[-1] else 0),
            lifelines_used=self.lifelines.total_used,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        Leaderboard.save(record)
        Leaderboard.display()


# ==============================================================================
# RUN SCRIPT
# ==============================================================================
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{Style.BOLD}{Style.YELLOW}=====================================================")
    print("   WELCOME TO PYCRORE: ADVANCED MCQ ENGINE")
    print(f"====================================================={Style.RESET}")
    name = input("Enter Contestant Name: ").strip() or "Player 1"

    engine = KBCGameEngine(player_name=name)
    engine.start()
