import tkinter as tk
from tkinter import messagebox
import random
import math

# ---------------- CONFIG ----------------
WIDTH = 600
HEIGHT = 600
BOX_SIZE = 20
INITIAL_SPEED = 120  # Moderate starting speed (higher value = slower)
MIN_SPEED = 40  # Maximum speed (lower value = faster)
LEVEL_THRESHOLD = 5  # Points needed to advance to next level

# Badge system configuration
BADGE_LEVELS = {
    2: {"name": "Bronze", "color": "#CD7F32", "emoji": "🥉"},
    4: {"name": "Silver", "color": "#C0C0C0", "emoji": "🥈"},
    6: {"name": "Gold", "color": "#FFD700", "emoji": "🥇"},
    8: {"name": "Platinum", "color": "#E5E4E2", "emoji": "💎"},
    10: {"name": "Diamond", "color": "#B9F2FF", "emoji": "💠"},
    12: {"name": "Master", "color": "#9C27B0", "emoji": "🏆"},
    14: {"name": "Legendary", "color": "#FF5722", "emoji": "🔥"},
    16: {"name": "Mythic", "color": "#673AB7", "emoji": "⚡"},
    18: {"name": "Eternal", "color": "#3F51B5", "emoji": "🌟"},
    20: {"name": "Divine", "color": "#F44336", "emoji": "👑"}
}

# ---------------- GAME WINDOW ----------------
root = tk.Tk()
root.title("Snake Game - Professional Edition")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

# Global variables
direction = "Right"
snake = [(300, 300), (280, 300), (260, 300)]
food = None
score = 0
high_score = 0
level = 1
running = False
paused = False
game_started = False
speed = INITIAL_SPEED
smooth_move_counter = 0
smooth_move_threshold = 3  # How many sub-steps for smooth movement
achieved_badges = []  # Store achieved badges
badge_notification = None  # Current badge notification

# Create frames for different screens
main_frame = tk.Frame(root, bg="#1a1a1a")
game_frame = tk.Frame(root, bg="#1a1a1a")
settings_frame = tk.Frame(root, bg="#1a1a1a")
achievements_frame = tk.Frame(root, bg="#1a1a1a")

# ---------------- BADGE FUNCTIONS ----------------
def check_badge_achievement():
    global badge_notification
    
    # Check if the current level has a badge
    if level in BADGE_LEVELS and level not in [b["level"] for b in achieved_badges]:
        badge_info = BADGE_LEVELS[level]
        new_badge = {"level": level, "name": badge_info["name"], "color": badge_info["color"], "emoji": badge_info["emoji"]}
        achieved_badges.append(new_badge)
        
        # Show badge notification
        show_badge_notification(new_badge)
        
        # Higher priority badges (higher levels) have longer display time
        priority = level // 2  # Priority increases with level
        display_time = 3000 + (priority * 500)  # Base 3 seconds + 0.5 seconds per priority level
        
        # Schedule hiding the notification
        root.after(display_time, hide_badge_notification)

def show_badge_notification(badge):
    global badge_notification
    
    # Hide any existing notification
    if badge_notification:
        hide_badge_notification()
    
    # Create a new notification frame
    badge_notification = tk.Frame(game_frame, bg=badge["color"], relief=tk.RAISED, borderwidth=3)
    badge_notification.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Badge emoji (larger for higher priority badges)
    emoji_size = 24 + (badge["level"] // 4) * 4  # Larger emoji for higher level badges
    emoji_label = tk.Label(
        badge_notification, 
        text=badge["emoji"], 
        font=("Arial", emoji_size),
        bg=badge["color"]
    )
    emoji_label.pack(pady=5)
    
    # Congrats text
    congrats_label = tk.Label(
        badge_notification, 
        text="CONGRATS!", 
        font=("Arial", 16, "bold"),
        bg=badge["color"],
        fg="white"
    )
    congrats_label.pack()
    
    # Badge achievement text
    text_label = tk.Label(
        badge_notification, 
        text=f"You have achieved {badge['name']} badge for level {badge['level']}!", 
        font=("Arial", 12),
        bg=badge["color"],
        fg="white",
        wraplength=250
    )
    text_label.pack(padx=10, pady=5)
    
    # Add a subtle animation effect
    animate_badge_notification()

def animate_badge_notification():
    if not badge_notification:
        return
    
    # Simple pulsing animation
    current_width = badge_notification.winfo_width()
    current_height = badge_notification.winfo_height()
    
    if current_width > 1:  # Make sure the widget is rendered
        new_width = current_width + 2
        new_height = current_height + 1
        
        # Limit the size
        if new_width < 320:
            badge_notification.place(relx=0.5, rely=0.5, anchor=tk.CENTER, 
                                    width=new_width, height=new_height)
            root.after(50, lambda: animate_badge_notification())

def hide_badge_notification():
    global badge_notification
    
    if badge_notification:
        badge_notification.destroy()
        badge_notification = None

# ---------------- MAIN MENU ----------------
def show_main_menu():
    global game_started, running, paused, level, speed, achieved_badges
    
    game_started = False
    running = False
    paused = False
    level = 1
    speed = INITIAL_SPEED
    achieved_badges = []
    
    # Hide other frames
    game_frame.pack_forget()
    settings_frame.pack_forget()
    achievements_frame.pack_forget()
    
    # Show main menu
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Clear main frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # Title
    title = tk.Label(
        main_frame, 
        text="SNAKE GAME", 
        font=("Arial", 36, "bold"),
        fg="#4CAF50",
        bg="#1a1a1a"
    )
    title.pack(pady=50)
    
    # High score
    high_score_label = tk.Label(
        main_frame, 
        text=f"High Score: {high_score}", 
        font=("Arial", 16),
        fg="white",
        bg="#1a1a1a"
    )
    high_score_label.pack(pady=10)
    
    # Buttons
    start_btn = tk.Button(
        main_frame, 
        text="START GAME", 
        font=("Arial", 16),
        bg="#4CAF50",
        fg="white",
        width=15,
        height=2,
        command=start_game
    )
    start_btn.pack(pady=10)
    
    achievements_btn = tk.Button(
        main_frame, 
        text="ACHIEVEMENTS", 
        font=("Arial", 16),
        bg="#9C27B0",
        fg="white",
        width=15,
        height=2,
        command=show_achievements
    )
    achievements_btn.pack(pady=10)
    
    settings_btn = tk.Button(
        main_frame, 
        text="SETTINGS", 
        font=("Arial", 16),
        bg="#2196F3",
        fg="white",
        width=15,
        height=2,
        command=show_settings
    )
    settings_btn.pack(pady=10)
    
    exit_btn = tk.Button(
        main_frame, 
        text="EXIT", 
        font=("Arial", 16),
        bg="#F44336",
        fg="white",
        width=15,
        height=2,
        command=root.quit
    )
    exit_btn.pack(pady=10)

# ---------------- ACHIEVEMENTS SCREEN ----------------
def show_achievements():
    # Hide other frames
    main_frame.pack_forget()
    game_frame.pack_forget()
    settings_frame.pack_forget()
    
    # Show achievements frame
    achievements_frame.pack(fill=tk.BOTH, expand=True)
    
    # Clear achievements frame
    for widget in achievements_frame.winfo_children():
        widget.destroy()
    
    # Title
    title = tk.Label(
        achievements_frame, 
        text="ACHIEVEMENTS", 
        font=("Arial", 30, "bold"),
        fg="#9C27B0",
        bg="#1a1a1a"
    )
    title.pack(pady=20)
    
    # Create scrollable frame for badges
    canvas = tk.Canvas(achievements_frame, bg="#1a1a1a", highlightthickness=0)
    scrollbar = tk.Scrollbar(achievements_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Display all badges
    for level_num, badge_info in BADGE_LEVELS.items():
        # Check if badge is achieved
        is_achieved = level_num in [b["level"] for b in achieved_badges]
        
        # Badge frame
        badge_frame = tk.Frame(
            scrollable_frame, 
            bg=badge_info["color"] if is_achieved else "#333333",
            relief=tk.RAISED if is_achieved else tk.SUNKEN,
            borderwidth=2
        )
        badge_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Badge emoji
        emoji_label = tk.Label(
            badge_frame, 
            text=badge_info["emoji"], 
            font=("Arial", 24),
            bg=badge_info["color"] if is_achieved else "#333333",
            fg="white" if is_achieved else "#666666"
        )
        emoji_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Badge info
        info_frame = tk.Frame(badge_frame, bg=badge_info["color"] if is_achieved else "#333333")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Badge name
        name_label = tk.Label(
            info_frame, 
            text=badge_info["name"], 
            font=("Arial", 16, "bold"),
            bg=badge_info["color"] if is_achieved else "#333333",
            fg="white" if is_achieved else "#666666",
            anchor="w"
        )
        name_label.pack(fill=tk.X)
        
        # Badge requirement
        req_label = tk.Label(
            info_frame, 
            text=f"Reach Level {level_num}", 
            font=("Arial", 12),
            bg=badge_info["color"] if is_achieved else "#333333",
            fg="white" if is_achieved else "#666666",
            anchor="w"
        )
        req_label.pack(fill=tk.X)
        
        # Status
        status_label = tk.Label(
            info_frame, 
            text="✓ ACHIEVED" if is_achieved else "LOCKED", 
            font=("Arial", 12, "bold"),
            bg=badge_info["color"] if is_achieved else "#333333",
            fg="white" if is_achieved else "#666666",
            anchor="e"
        )
        status_label.pack(fill=tk.X, pady=5)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Back button
    back_btn = tk.Button(
        achievements_frame, 
        text="BACK", 
        font=("Arial", 14),
        bg="#9E9E9E",
        fg="white",
        width=10,
        command=show_main_menu
    )
    back_btn.pack(pady=20)

# ---------------- SETTINGS MENU ----------------
def show_settings():
    # Hide other frames
    main_frame.pack_forget()
    game_frame.pack_forget()
    achievements_frame.pack_forget()
    
    # Show settings frame
    settings_frame.pack(fill=tk.BOTH, expand=True)
    
    # Clear settings frame
    for widget in settings_frame.winfo_children():
        widget.destroy()
    
    # Title
    title = tk.Label(
        settings_frame, 
        text="SETTINGS", 
        font=("Arial", 30, "bold"),
        fg="#2196F3",
        bg="#1a1a1a"
    )
    title.pack(pady=30)
    
    # Speed setting
    speed_frame = tk.Frame(settings_frame, bg="#1a1a1a")
    speed_frame.pack(pady=20)
    
    tk.Label(
        speed_frame, 
        text="Initial Game Speed:", 
        font=("Arial", 14),
        fg="white",
        bg="#1a1a1a"
    ).pack(side=tk.LEFT, padx=10)
    
    speed_var = tk.IntVar(value=INITIAL_SPEED)
    
    def update_initial_speed(val):
        global INITIAL_SPEED
        INITIAL_SPEED = int(val)
    
    speed_scale = tk.Scale(
        speed_frame,
        from_=80,
        to=160,
        orient=tk.HORIZONTAL,
        variable=speed_var,
        command=update_initial_speed,
        bg="#1a1a1a",
        fg="white",
        highlightthickness=0,
        length=200
    )
    speed_scale.pack(side=tk.LEFT)
    
    # Labels for speed
    speed_labels = tk.Frame(settings_frame, bg="#1a1a1a")
    speed_labels.pack()
    
    tk.Label(
        speed_labels, 
        text="Fast", 
        font=("Arial", 10),
        fg="white",
        bg="#1a1a1a"
    ).pack(side=tk.LEFT, padx=30)
    
    tk.Label(
        speed_labels, 
        text="Slow", 
        font=("Arial", 10),
        fg="white",
        bg="#1a1a1a"
    ).pack(side=tk.LEFT, padx=30)
    
    # Back button
    back_btn = tk.Button(
        settings_frame, 
        text="BACK", 
        font=("Arial", 14),
        bg="#9E9E9E",
        fg="white",
        width=10,
        command=show_main_menu
    )
    back_btn.pack(pady=30)

# ---------------- GAME SCREEN ----------------
def start_game():
    global snake, direction, food, score, running, paused, game_started, level, speed, smooth_move_counter, achieved_badges
    
    # Reset game state
    snake = [(300, 300), (280, 300), (260, 300)]
    direction = "Right"
    score = 0
    level = 1
    speed = INITIAL_SPEED
    running = True
    paused = False
    game_started = True
    smooth_move_counter = 0
    achieved_badges = []
    
    # Hide other frames
    main_frame.pack_forget()
    settings_frame.pack_forget()
    achievements_frame.pack_forget()
    
    # Show game frame
    game_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create canvas if it doesn't exist
    if not hasattr(game_frame, 'canvas'):
        game_frame.canvas = tk.Canvas(
            game_frame, 
            width=WIDTH, 
            height=HEIGHT, 
            bg="#111111",
            highlightthickness=2,
            highlightbackground="#333333"
        )
        game_frame.canvas.pack(pady=10)
        
        # Score and level frame
        score_frame = tk.Frame(game_frame, bg="#1a1a1a")
        score_frame.pack()
        
        # Score label
        game_frame.score_label = tk.Label(
            score_frame, 
            text=f"Score: {score}", 
            font=("Arial", 14),
            fg="white",
            bg="#1a1a1a"
        )
        game_frame.score_label.pack(side=tk.LEFT, padx=20)
        
        # Level label
        game_frame.level_label = tk.Label(
            score_frame, 
            text=f"Level: {level}", 
            font=("Arial", 14),
            fg="#FFC107",
            bg="#1a1a1a"
        )
        game_frame.level_label.pack(side=tk.LEFT, padx=20)
        
        # Current badge label (if any)
        game_frame.badge_label = tk.Label(
            score_frame, 
            text="", 
            font=("Arial", 14),
            fg="#9C27B0",
            bg="#1a1a1a"
        )
        game_frame.badge_label.pack(side=tk.LEFT, padx=20)
        
        # Pause button
        game_frame.pause_btn = tk.Button(
            game_frame, 
            text="PAUSE", 
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            width=10,
            command=toggle_pause
        )
        game_frame.pause_btn.pack(pady=5)
    
    # Create food and start game
    create_food()
    draw_objects()
    move_snake()

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        game_frame.pause_btn.config(text="RESUME")
        show_pause_menu()
    else:
        game_frame.pause_btn.config(text="PAUSE")
        move_snake()

def show_pause_menu():
    # Create pause menu
    pause_menu = tk.Toplevel(root)
    pause_menu.title("Game Paused")
    pause_menu.geometry("300x300")
    pause_menu.configure(bg="#1a1a1a")
    pause_menu.transient(root)
    pause_menu.grab_set()
    
    # Center the window
    pause_menu.update_idletasks()
    x = (pause_menu.winfo_screenwidth() // 2) - (pause_menu.winfo_width() // 2)
    y = (pause_menu.winfo_screenheight() // 2) - (pause_menu.winfo_height() // 2)
    pause_menu.geometry(f"+{x}+{y}")
    
    # Title
    title = tk.Label(
        pause_menu, 
        text="GAME PAUSED", 
        font=("Arial", 20, "bold"),
        fg="#FF9800",
        bg="#1a1a1a"
    )
    title.pack(pady=20)
    
    # Resume button
    resume_btn = tk.Button(
        pause_menu, 
        text="RESUME", 
        font=("Arial", 14),
        bg="#4CAF50",
        fg="white",
        width=15,
        command=lambda: [pause_menu.destroy(), toggle_pause()]
    )
    resume_btn.pack(pady=10)
    
    # Achievements button
    achievements_btn = tk.Button(
        pause_menu, 
        text="ACHIEVEMENTS", 
        font=("Arial", 14),
        bg="#9C27B0",
        fg="white",
        width=15,
        command=lambda: [pause_menu.destroy(), show_achievements()]
    )
    achievements_btn.pack(pady=10)
    
    # Settings button
    settings_btn = tk.Button(
        pause_menu, 
        text="SETTINGS", 
        font=("Arial", 14),
        bg="#2196F3",
        fg="white",
        width=15,
        command=lambda: [pause_menu.destroy(), show_settings()]
    )
    settings_btn.pack(pady=10)
    
    # Main menu button
    menu_btn = tk.Button(
        pause_menu, 
        text="MAIN MENU", 
        font=("Arial", 14),
        bg="#9E9E9E",
        fg="white",
        width=15,
        command=lambda: [pause_menu.destroy(), show_main_menu()]
    )
    menu_btn.pack(pady=10)
    
    # Exit button
    exit_btn = tk.Button(
        pause_menu, 
        text="EXIT", 
        font=("Arial", 14),
        bg="#F44336",
        fg="white",
        width=15,
        command=root.quit
    )
    exit_btn.pack(pady=10)

# ---------------- GAME FUNCTIONS ----------------
def create_food():
    global food
    while True:
        x = random.randrange(0, WIDTH, BOX_SIZE)
        y = random.randrange(0, HEIGHT, BOX_SIZE)
        food = (x, y)
        if food not in snake:  # Make sure food doesn't spawn on snake
            break

def draw_objects():
    game_frame.canvas.delete("all")
    
    # Draw grid (optional visual enhancement)
    for i in range(0, WIDTH, BOX_SIZE):
        game_frame.canvas.create_line(i, 0, i, HEIGHT, fill="#222222", width=1)
    for i in range(0, HEIGHT, BOX_SIZE):
        game_frame.canvas.create_line(0, i, WIDTH, i, fill="#222222", width=1)
    
    # Draw food with pulsing effect
    fx, fy = food
    pulse = abs(math.sin(smooth_move_counter * 0.1)) * 2  # Pulsing effect
    game_frame.canvas.create_oval(
        fx + 2 - pulse, fy + 2 - pulse, 
        fx + BOX_SIZE - 2 + pulse, fy + BOX_SIZE - 2 + pulse, 
        fill="#F44336", outline="#FF5252", width=2
    )
    
    # Draw snake with smooth segments
    for i, (x, y) in enumerate(snake):
        if i == 0:  # Head
            # Add gradient effect to head
            game_frame.canvas.create_rectangle(
                x, y, x + BOX_SIZE, y + BOX_SIZE, 
                fill="#4CAF50", outline="#81C784", width=2
            )
            # Eyes with animation
            eye_size = 3 + abs(math.sin(smooth_move_counter * 0.2))
            if direction == "Right":
                game_frame.canvas.create_oval(x + 12, y + 6, x + 12 + eye_size, y + 6 + eye_size, fill="white")
                game_frame.canvas.create_oval(x + 12, y + 12, x + 12 + eye_size, y + 12 + eye_size, fill="white")
            elif direction == "Left":
                game_frame.canvas.create_oval(x + 4 - eye_size, y + 6, x + 4, y + 6 + eye_size, fill="white")
                game_frame.canvas.create_oval(x + 4 - eye_size, y + 12, x + 4, y + 12 + eye_size, fill="white")
            elif direction == "Up":
                game_frame.canvas.create_oval(x + 6, y + 4 - eye_size, x + 6 + eye_size, y + 4, fill="white")
                game_frame.canvas.create_oval(x + 12, y + 4 - eye_size, x + 12 + eye_size, y + 4, fill="white")
            else:  # Down
                game_frame.canvas.create_oval(x + 6, y + 12, x + 6 + eye_size, y + 12 + eye_size, fill="white")
                game_frame.canvas.create_oval(x + 12, y + 12, x + 12 + eye_size, y + 12 + eye_size, fill="white")
        else:  # Body with gradient
            color_intensity = max(0.4, 1.0 - (i / len(snake)) * 0.5)  # Fade effect
            green_value = int(187 * color_intensity)  # 187 is the green component of #66BB6A
            color = f"#{int(102 * color_intensity):02x}{green_value:02x}{int(106 * color_intensity):02x}"
            
            game_frame.canvas.create_rectangle(
                x, y, x + BOX_SIZE, y + BOX_SIZE, 
                fill=color, outline="#81C784", width=1
            )
    
    # Update score and level
    game_frame.score_label.config(text=f"Score: {score}")
    game_frame.level_label.config(text=f"Level: {level}")
    
    # Update current badge if any
    if achieved_badges:
        latest_badge = achieved_badges[-1]
        game_frame.badge_label.config(text=f"{latest_badge['emoji']} {latest_badge['name']}")
    else:
        game_frame.badge_label.config(text="")

def update_level():
    global level, speed
    new_level = (score // LEVEL_THRESHOLD) + 1
    if new_level > level:
        level = new_level
        # Increase speed (decrease the delay) with each level
        speed = max(MIN_SPEED, INITIAL_SPEED - (level - 1) * 15)
        # Show level up notification
        game_frame.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text=f"LEVEL {level}!",
            fill="#FFC107",
            font=("Arial", 24, "bold"),
            tags="levelup"
        )
        # Remove the level up text after a short time
        root.after(1500, lambda: game_frame.canvas.delete("levelup"))
        
        # Check for badge achievement
        check_badge_achievement()

def move_snake():
    global running, score, high_score, paused, smooth_move_counter
    
    if not running or paused:
        return
    
    smooth_move_counter += 1
    
    # Only move the snake every few frames for smoother animation
    if smooth_move_counter % smooth_move_threshold != 0:
        draw_objects()
        root.after(speed // smooth_move_threshold, move_snake)
        return
    
    head_x, head_y = snake[0]
    
    if direction == "Up":
        new_head = (head_x, head_y - BOX_SIZE)
    elif direction == "Down":
        new_head = (head_x, head_y + BOX_SIZE)
    elif direction == "Left":
        new_head = (head_x - BOX_SIZE, head_y)
    else:
        new_head = (head_x + BOX_SIZE, head_y)
    
    # Wall collision
    if (
        new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT or
        new_head in snake
    ):
        game_over()
        return
    
    snake.insert(0, new_head)
    
    # Food collision
    if new_head == food:
        score += 1
        if score > high_score:
            high_score = score
        update_level()  # Check for level up
        create_food()
    else:
        snake.pop()
    
    draw_objects()
    root.after(speed // smooth_move_threshold, move_snake)

def change_direction(new_dir):
    global direction
    opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
    if new_dir != opposite.get(direction):
        direction = new_dir

def game_over():
    global running
    
    running = False
    
    # Create game over dialog
    game_over_dialog = tk.Toplevel(root)
    game_over_dialog.title("Game Over")
    game_over_dialog.geometry("350x350")
    game_over_dialog.configure(bg="#1a1a1a")
    game_over_dialog.transient(root)
    game_over_dialog.grab_set()
    
    # Center the window
    game_over_dialog.update_idletasks()
    x = (game_over_dialog.winfo_screenwidth() // 2) - (game_over_dialog.winfo_width() // 2)
    y = (game_over_dialog.winfo_screenheight() // 2) - (game_over_dialog.winfo_height() // 2)
    game_over_dialog.geometry(f"+{x}+{y}")
    
    # Title
    title = tk.Label(
        game_over_dialog, 
        text="GAME OVER", 
        font=("Arial", 20, "bold"),
        fg="#F44336",
        bg="#1a1a1a"
    )
    title.pack(pady=20)
    
    # Score
    score_label = tk.Label(
        game_over_dialog, 
        text=f"Score: {score}", 
        font=("Arial", 14),
        fg="white",
        bg="#1a1a1a"
    )
    score_label.pack(pady=5)
    
    # Level
    level_label = tk.Label(
        game_over_dialog, 
        text=f"Level Reached: {level}", 
        font=("Arial", 14),
        fg="#FFC107",
        bg="#1a1a1a"
    )
    level_label.pack(pady=5)
    
    # Highest badge achieved
    if achieved_badges:
        highest_badge = achieved_badges[-1]
        badge_label = tk.Label(
            game_over_dialog, 
            text=f"Highest Badge: {highest_badge['emoji']} {highest_badge['name']}", 
            font=("Arial", 14),
            fg=highest_badge["color"],
            bg="#1a1a1a"
        )
        badge_label.pack(pady=5)
    
    # High score
    high_score_label = tk.Label(
        game_over_dialog, 
        text=f"High Score: {high_score}", 
        font=("Arial", 14),
        fg="#4CAF50",
        bg="#1a1a1a"
    )
    high_score_label.pack(pady=5)
    
    # Buttons
    button_frame = tk.Frame(game_over_dialog, bg="#1a1a1a")
    button_frame.pack(pady=20)
    
    play_again_btn = tk.Button(
        button_frame, 
        text="PLAY AGAIN", 
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        command=lambda: [game_over_dialog.destroy(), start_game()]
    )
    play_again_btn.pack(side=tk.LEFT, padx=10)
    
    achievements_btn = tk.Button(
        button_frame, 
        text="ACHIEVEMENTS", 
        font=("Arial", 12),
        bg="#9C27B0",
        fg="white",
        command=lambda: [game_over_dialog.destroy(), show_achievements()]
    )
    achievements_btn.pack(side=tk.LEFT, padx=10)
    
    menu_btn = tk.Button(
        button_frame, 
        text="MAIN MENU", 
        font=("Arial", 12),
        bg="#9E9E9E",
        fg="white",
        command=lambda: [game_over_dialog.destroy(), show_main_menu()]
    )
    menu_btn.pack(side=tk.LEFT, padx=10)

# ---------------- CONTROLS ----------------
root.bind("<Up>", lambda e: change_direction("Up"))
root.bind("<Down>", lambda e: change_direction("Down"))
root.bind("<Left>", lambda e: change_direction("Left"))
root.bind("<Right>", lambda e: change_direction("Right"))
root.bind("<Escape>", lambda e: toggle_pause() if game_started else None)

# ---------------- START APP ----------------
show_main_menu()
root.mainloop()
