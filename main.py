"""
AnywhereDr — Main Application
AI-Powered Medical Consultation System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import threading
from datetime import datetime

from config import (
    APP_NAME, APP_TAGLINE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WIDTH, MIN_HEIGHT, COLORS, FONTS, BODY_PARTS, FOLLOWUP_QUESTIONS,
    MEDICAL_DISCLAIMER, REPORTS_DIR
)
from ai_engine import get_diagnosis
from report_generator import save_report, format_text_report


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def make_frame(parent, **kwargs):
    defaults = {"bg": COLORS["bg_primary"]}
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def make_label(parent, text, font=None, fg=None, bg=None, **kwargs):
    return tk.Label(
        parent, text=text,
        font=font or FONTS["body"],
        fg=fg or COLORS["text_primary"],
        bg=bg or COLORS["bg_primary"],
        **kwargs
    )


def make_scrollable_frame(parent, bg=None):
    """Returns (outer_frame, canvas, inner_frame) — pack outer_frame."""
    bg = bg or COLORS["bg_primary"]
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(e):
        canvas.itemconfig(inner_id, width=e.width)

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    inner.bind("<Configure>", _on_inner_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    return outer, canvas, inner


class StyledButton(tk.Frame):
    """
    A custom button with gradient-like appearance, hover, and press effects.
    """
    def __init__(self, parent, text, command=None, style="primary",
                 width=None, font=None, icon="", **kwargs):
        bg = parent.cget("bg") if hasattr(parent, "cget") else COLORS["bg_primary"]
        super().__init__(parent, bg=bg, cursor="hand2")

        styles = {
            "primary":  (COLORS["accent"],           COLORS["accent_dark"],    "#000000"),
            "secondary":(COLORS["accent_secondary"],  COLORS["accent_sec_dark"], "#ffffff"),
            "danger":   (COLORS["danger"],            "#cc2222",                "#ffffff"),
            "ghost":    (COLORS["bg_card_hover"],     COLORS["bg_card"],        COLORS["text_primary"]),
            "outline":  (COLORS["bg_card"],           COLORS["bg_card_hover"],  COLORS["accent"]),
        }
        self._color, self._hover, self._text_color = styles.get(style, styles["primary"])
        self._command = command

        self._btn = tk.Label(
            self,
            text=f"{icon}  {text}" if icon else text,
            font=font or FONTS["button"],
            fg=self._text_color,
            bg=self._color,
            cursor="hand2",
            padx=20, pady=10,
            relief="flat",
        )
        if width:
            self._btn.config(width=width)
        self._btn.pack(fill="both", expand=True)

        self._btn.bind("<Enter>",   self._on_enter)
        self._btn.bind("<Leave>",   self._on_leave)
        self._btn.bind("<Button-1>", self._on_press)
        self._btn.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Button-1>",     self._on_press)

    def _on_enter(self, e):
        self._btn.config(bg=self._hover)

    def _on_leave(self, e):
        self._btn.config(bg=self._color)

    def _on_press(self, e):
        self._btn.config(relief="sunken")
        if self._command:
            self.after(100, self._command)

    def _on_release(self, e):
        self._btn.config(relief="flat")

    def config_state(self, state):
        """Enable or disable the button."""
        if state == "disabled":
            self._btn.config(bg=COLORS["text_muted"], fg=COLORS["bg_card"],
                             cursor="arrow")
            self._btn.unbind("<Button-1>")
            self.unbind("<Button-1>")
        else:
            self._btn.config(bg=self._color, fg=self._text_color, cursor="hand2")
            self._btn.bind("<Button-1>", self._on_press)
            self.bind("<Button-1>", self._on_press)


class Card(tk.Frame):
    """A styled card container."""
    def __init__(self, parent, **kwargs):
        bg = kwargs.pop("bg", COLORS["bg_card"])
        hlbg = kwargs.pop("highlightbackground", COLORS["border"])
        super().__init__(parent, bg=bg,
                         relief="flat",
                         highlightthickness=1,
                         highlightbackground=hlbg,
                         **kwargs)


class SectionHeader(tk.Frame):
    """A labeled section divider with accent line."""
    def __init__(self, parent, title, icon="", **kwargs):
        bg = kwargs.pop("bg", COLORS["bg_primary"])
        super().__init__(parent, bg=bg, **kwargs)

        row = tk.Frame(self, bg=bg)
        row.pack(fill="x", pady=(0, 4))

        if icon:
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 16),
                     fg=COLORS["accent"], bg=bg).pack(side="left", padx=(0, 8))

        tk.Label(row, text=title, font=FONTS["title_md"],
                 fg=COLORS["text_white"], bg=bg).pack(side="left")

        # Accent underline
        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill="x", pady=(0, 2))


# ══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════════════════════════════

class WelcomeScreen(tk.Frame):
    """
    Screen 0 — Welcome / Landing page
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller = controller
        self._build()

    def _build(self):
        # ── Top accent bar ─────────────────────────────────────────────────
        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        # ── Scrollable content ─────────────────────────────────────────────
        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=60)

        # ── Hero section ───────────────────────────────────────────────────
        hero = tk.Frame(inner, bg=COLORS["bg_primary"])
        hero.pack(fill="x", pady=(50, 30))

        tk.Label(hero, text="🏥", font=("Segoe UI Emoji", 64),
                 bg=COLORS["bg_primary"], fg=COLORS["accent"]).pack()
        tk.Label(hero, text="Anywhere Dr",
                 font=("Segoe UI", 38, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg_primary"]).pack(pady=(8, 4))
        tk.Label(hero, text="AI-Powered Medical Consultation",
                 font=("Segoe UI", 14),
                 fg=COLORS["text_secondary"], bg=COLORS["bg_primary"]).pack()

        # Divider
        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=30)

        # ── Feature cards row ──────────────────────────────────────────────
        features_row = tk.Frame(inner, bg=COLORS["bg_primary"])
        features_row.pack(fill="x", pady=(0, 30))

        features = [
            ("🩺", "Symptom Analysis",    "Select from 80+ symptoms across 10 body systems"),
            ("🤖", "AI Diagnosis",         "Powered by GPT-4o for accurate assessments"),
            ("📋", "Medical Report",       "Download your full consultation report"),
            ("🔒", "Private & Secure",     "No data stored — your health data stays private"),
        ]

        for icon, title, desc in features:
            card = Card(features_row, padx=16, pady=18)
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 28),
                     fg=COLORS["accent"], bg=COLORS["bg_card"]).pack(pady=(0, 8))
            tk.Label(card, text=title, font=FONTS["title_sm"],
                     fg=COLORS["text_white"], bg=COLORS["bg_card"]).pack(pady=(0, 4))
            tk.Label(card, text=desc, font=FONTS["small"],
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     wraplength=160, justify="center").pack()

        # ── How it works ───────────────────────────────────────────────────
        SectionHeader(inner, "How It Works", icon="✨",
                      bg=COLORS["bg_primary"]).pack(fill="x", pady=(10, 20))

        steps_frame = tk.Frame(inner, bg=COLORS["bg_primary"])
        steps_frame.pack(fill="x", pady=(0, 20))

        steps = [
            ("1", "Enter Details",   "Provide your name, age, and gender"),
            ("2", "Pick Body Area",  "Select which area(s) are affected"),
            ("3", "Choose Symptoms", "Check the symptoms you're experiencing"),
            ("4", "Answer Questions","Brief medical history questions"),
            ("5", "Get Diagnosis",   "AI analyzes and provides consultation"),
        ]

        for num, title, desc in steps:
            row = tk.Frame(steps_frame, bg=COLORS["bg_secondary"],
                           relief="flat", pady=12, padx=16)
            row.pack(fill="x", pady=4)

            # Number badge
            badge = tk.Label(row, text=num, font=("Segoe UI", 13, "bold"),
                             fg="#000000", bg=COLORS["accent"],
                             width=3, relief="flat")
            badge.pack(side="left", padx=(0, 16))

            info = tk.Frame(row, bg=COLORS["bg_secondary"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=title, font=FONTS["body_bold"],
                     fg=COLORS["text_white"], bg=COLORS["bg_secondary"],
                     anchor="w").pack(fill="x")
            tk.Label(info, text=desc, font=FONTS["small"],
                     fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"],
                     anchor="w").pack(fill="x")

        # ── Disclaimer ─────────────────────────────────────────────────────
        disc_card = Card(inner, padx=20, pady=16)
        disc_card.pack(fill="x", pady=(10, 20))
        tk.Label(disc_card, text="⚠️  Medical Disclaimer",
                 font=FONTS["title_sm"], fg=COLORS["warning"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))
        tk.Label(disc_card,
                 text=("This app is for informational purposes only and does NOT replace "
                       "professional medical advice. Always consult a qualified doctor "
                       "for any health concerns. In emergencies, call emergency services."),
                 font=FONTS["small"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], wraplength=700, justify="left").pack(anchor="w")

        # ── Start Button ───────────────────────────────────────────────────
        btn_frame = tk.Frame(inner, bg=COLORS["bg_primary"])
        btn_frame.pack(pady=(10, 40))

        btn = StyledButton(btn_frame,
                           text="Start Consultation",
                           icon="▶",
                           command=lambda: self.controller.show_screen("registration"),
                           style="primary",
                           font=("Segoe UI", 13, "bold"))
        btn.pack(ipadx=20, ipady=6)

        tk.Label(inner,
                 text=f"{APP_NAME} v{APP_VERSION}  —  For demonstration purposes only",
                 font=FONTS["small"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_primary"]).pack(pady=(0, 20))


class RegistrationScreen(tk.Frame):
    """
    Screen 1 — Patient Registration
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller = controller
        self._build()

    def _build(self):
        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=60, pady=30)

        # ── Title ──────────────────────────────────────────────────────────
        tk.Label(inner, text="Patient Registration",
                 font=FONTS["title_lg"], fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Please enter your details to begin the consultation",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 20))

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 24))

        # ── Form Card ──────────────────────────────────────────────────────
        card = Card(inner, padx=30, pady=28)
        card.pack(fill="x")

        SectionHeader(card, "Personal Information", icon="👤",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 20))

        # ── Name Field ────────────────────────────────────────────────────
        tk.Label(card, text="Full Name *",
                 font=FONTS["label"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], anchor="w").pack(fill="x")

        self.name_var = tk.StringVar()
        name_entry = tk.Entry(card, textvariable=self.name_var,
                              font=FONTS["body"],
                              bg=COLORS["bg_input"],
                              fg=COLORS["text_primary"],
                              insertbackground=COLORS["accent"],
                              relief="flat",
                              bd=0)
        name_entry.pack(fill="x", pady=(4, 16), ipady=10)
        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 16))

        # ── Age & Gender Row ──────────────────────────────────────────────
        row = tk.Frame(card, bg=COLORS["bg_card"])
        row.pack(fill="x")

        # Age
        age_frame = tk.Frame(row, bg=COLORS["bg_card"])
        age_frame.pack(side="left", fill="x", expand=True, padx=(0, 16))

        tk.Label(age_frame, text="Age *",
                 font=FONTS["label"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], anchor="w").pack(fill="x")
        self.age_var = tk.StringVar()
        age_entry = tk.Entry(age_frame, textvariable=self.age_var,
                             font=FONTS["body"],
                             bg=COLORS["bg_input"],
                             fg=COLORS["text_primary"],
                             insertbackground=COLORS["accent"],
                             relief="flat", bd=0, width=12)
        age_entry.pack(fill="x", pady=(4, 0), ipady=10)
        tk.Frame(age_frame, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 0))

        # Gender
        gender_frame = tk.Frame(row, bg=COLORS["bg_card"])
        gender_frame.pack(side="left", fill="x", expand=True)

        tk.Label(gender_frame, text="Gender *",
                 font=FONTS["label"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], anchor="w").pack(fill="x")

        self.gender_var = tk.StringVar(value="")
        gender_options = ["Male", "Female", "Other", "Prefer not to say"]

        gender_inner = tk.Frame(gender_frame, bg=COLORS["bg_card"])
        gender_inner.pack(fill="x", pady=(4, 0))

        for g in gender_options:
            rb = tk.Radiobutton(
                gender_inner, text=g,
                variable=self.gender_var, value=g,
                font=FONTS["body"],
                fg=COLORS["text_primary"],
                bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_input"],
                activeforeground=COLORS["accent"],
                activebackground=COLORS["bg_card"],
                cursor="hand2",
            )
            rb.pack(side="left", padx=(0, 12))

        # ── Error label ───────────────────────────────────────────────────
        self.error_var = tk.StringVar()
        tk.Label(card, textvariable=self.error_var,
                 font=FONTS["small"], fg=COLORS["danger"],
                 bg=COLORS["bg_card"]).pack(pady=(16, 0))

        # ── Navigation ────────────────────────────────────────────────────
        nav = tk.Frame(inner, bg=COLORS["bg_primary"])
        nav.pack(fill="x", pady=(24, 0))

        StyledButton(nav, "← Back", style="ghost",
                     command=lambda: self.controller.show_screen("welcome")).pack(side="left")
        StyledButton(nav, "Next: Select Body Area →", style="primary",
                     command=self._validate_and_next).pack(side="right")

    def _validate_and_next(self):
        name = self.name_var.get().strip()
        age  = self.age_var.get().strip()
        gender = self.gender_var.get()

        if not name:
            self.error_var.set("⚠  Please enter your name.")
            return
        if not age or not age.isdigit() or not (1 <= int(age) <= 120):
            self.error_var.set("⚠  Please enter a valid age (1–120).")
            return
        if not gender:
            self.error_var.set("⚠  Please select a gender.")
            return

        self.error_var.set("")
        self.controller.patient_data["name"]   = name
        self.controller.patient_data["age"]    = age
        self.controller.patient_data["gender"] = gender
        self.controller.show_screen("body_part")


class BodyPartScreen(tk.Frame):
    """
    Screen 2 — Body Part Selection
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller = controller
        self.selected   = set()
        self._cards     = {}
        self._build()

    def _build(self):
        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=40, pady=30)

        tk.Label(inner, text="Select Affected Body Area(s)",
                 font=FONTS["title_lg"], fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Choose all areas where you are experiencing symptoms (select up to 3)",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 20))

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 20))

        # Grid of body part cards
        grid = tk.Frame(inner, bg=COLORS["bg_primary"])
        grid.pack(fill="x")

        body_parts = list(BODY_PARTS.keys())
        cols = 4
        for i, part_name in enumerate(body_parts):
            row_idx = i // cols
            col_idx = i % cols

            card_frame = tk.Frame(grid, bg=COLORS["bg_card"],
                                  relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=COLORS["border"],
                                  cursor="hand2", padx=12, pady=14)
            card_frame.grid(row=row_idx, column=col_idx,
                            padx=6, pady=6, sticky="nsew")
            grid.columnconfigure(col_idx, weight=1)

            icon = BODY_PARTS[part_name]["icon"]
            symptom_count = len(BODY_PARTS[part_name]["symptoms"])

            tk.Label(card_frame, text=icon,
                     font=("Segoe UI Emoji", 28),
                     bg=COLORS["bg_card"],
                     fg=COLORS["accent"]).pack()

            # Strip the icon from part_name for display
            display_name = part_name.split(" ", 1)[1] if " " in part_name else part_name
            tk.Label(card_frame, text=display_name,
                     font=FONTS["title_sm"],
                     fg=COLORS["text_white"],
                     bg=COLORS["bg_card"],
                     wraplength=130).pack(pady=(4, 2))

            tk.Label(card_frame, text=f"{symptom_count} symptoms",
                     font=FONTS["small"],
                     fg=COLORS["text_muted"],
                     bg=COLORS["bg_card"]).pack()

            # Checkmark overlay label
            check_lbl = tk.Label(card_frame, text="",
                                  font=FONTS["title_sm"],
                                  fg=COLORS["accent"],
                                  bg=COLORS["bg_card"])
            check_lbl.pack()

            self._cards[part_name] = (card_frame, check_lbl)

            # Bind clicks
            for w in [card_frame] + card_frame.winfo_children():
                w.bind("<Button-1>", lambda e, p=part_name: self._toggle(p))
            card_frame.bind("<Enter>", lambda e, c=card_frame: self._hover(c, True))
            card_frame.bind("<Leave>", lambda e, c=card_frame: self._hover(c, False))

        # Error & Navigation
        self.error_var = tk.StringVar()
        tk.Label(inner, textvariable=self.error_var,
                 font=FONTS["small"], fg=COLORS["danger"],
                 bg=COLORS["bg_primary"]).pack(pady=(16, 0))

        nav = tk.Frame(inner, bg=COLORS["bg_primary"])
        nav.pack(fill="x", pady=(12, 0))
        StyledButton(nav, "← Back", style="ghost",
                     command=lambda: self.controller.show_screen("registration")).pack(side="left")
        StyledButton(nav, "Next: Select Symptoms →", style="primary",
                     command=self._validate_and_next).pack(side="right")

    def _toggle(self, part_name):
        card_frame, check_lbl = self._cards[part_name]
        if part_name in self.selected:
            self.selected.discard(part_name)
            card_frame.config(bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"])
            self._update_children_bg(card_frame, COLORS["bg_card"])
            check_lbl.config(text="")
        else:
            if len(self.selected) >= 3:
                self.error_var.set("⚠  Maximum 3 body areas. Deselect one first.")
                return
            self.selected.add(part_name)
            card_frame.config(bg=COLORS["bg_card_hover"],
                               highlightbackground=COLORS["accent"])
            self._update_children_bg(card_frame, COLORS["bg_card_hover"])
            check_lbl.config(text="✓ Selected")
        self.error_var.set("")

    def _update_children_bg(self, widget, color):
        for child in widget.winfo_children():
            try:
                child.config(bg=color)
            except Exception:
                pass

    def _hover(self, card_frame, entering):
        part_name = next((k for k, v in self._cards.items() if v[0] == card_frame), None)
        if part_name and part_name not in self.selected:
            bg = COLORS["bg_card_hover"] if entering else COLORS["bg_card"]
            card_frame.config(bg=bg)
            self._update_children_bg(card_frame, bg)

    def _validate_and_next(self):
        if not self.selected:
            self.error_var.set("⚠  Please select at least one body area.")
            return
        self.error_var.set("")
        self.controller.selected_parts = list(self.selected)
        self.controller.show_screen("symptoms")


class SymptomScreen(tk.Frame):
    """
    Screen 3 — Symptom Selection
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller  = controller
        self.check_vars  = {}   # symptom -> BooleanVar
        self._built_for  = None
        self._build_placeholder()

    def _build_placeholder(self):
        self._placeholder = tk.Label(self, text="Loading symptoms...",
                                      font=FONTS["body"],
                                      fg=COLORS["text_muted"],
                                      bg=COLORS["bg_primary"])
        self._placeholder.pack(expand=True)

    def refresh(self):
        """Rebuild the screen based on currently selected body parts."""
        parts = self.controller.selected_parts
        if parts == self._built_for:
            return
        self._built_for = list(parts) if parts else []

        # Clear
        for w in self.winfo_children():
            w.destroy()
        self.check_vars.clear()

        self._build_content()

    def _build_content(self):
        parts = self.controller.selected_parts or []

        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=50, pady=30)

        tk.Label(inner, text="Select Your Symptoms",
                 font=FONTS["title_lg"], fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Check all symptoms you are currently experiencing",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 20))
        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 20))

        # Build a section for each selected part
        for part_name in parts:
            if part_name not in BODY_PARTS:
                continue
            part_data = BODY_PARTS[part_name]
            symptoms  = part_data["symptoms"]

            section = Card(inner, padx=20, pady=16)
            section.pack(fill="x", pady=(0, 14))

            SectionHeader(section, part_name, bg=COLORS["bg_card"]).pack(fill="x",
                                                                           pady=(0, 12))

            cols_frame = tk.Frame(section, bg=COLORS["bg_card"])
            cols_frame.pack(fill="x")

            # Two-column layout
            left_col  = tk.Frame(cols_frame, bg=COLORS["bg_card"])
            right_col = tk.Frame(cols_frame, bg=COLORS["bg_card"])
            left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))
            right_col.pack(side="left", fill="both", expand=True)

            for idx, symptom in enumerate(symptoms):
                col = left_col if idx % 2 == 0 else right_col
                var = tk.BooleanVar(value=False)
                self.check_vars[symptom] = var

                cb_frame = tk.Frame(col, bg=COLORS["bg_card"], cursor="hand2")
                cb_frame.pack(fill="x", pady=3)

                cb = tk.Checkbutton(
                    cb_frame,
                    text=f"  {symptom}",
                    variable=var,
                    font=FONTS["body"],
                    fg=COLORS["text_primary"],
                    bg=COLORS["bg_card"],
                    selectcolor=COLORS["bg_input"],
                    activeforeground=COLORS["accent"],
                    activebackground=COLORS["bg_card"],
                    cursor="hand2",
                    anchor="w",
                )
                cb.pack(fill="x")

        # Counter
        counter_frame = tk.Frame(inner, bg=COLORS["bg_secondary"], pady=8, padx=14)
        counter_frame.pack(fill="x", pady=(8, 0))
        self.counter_label = tk.Label(counter_frame, text="0 symptoms selected",
                                       font=FONTS["body_bold"],
                                       fg=COLORS["accent"],
                                       bg=COLORS["bg_secondary"])
        self.counter_label.pack(side="left")

        # Update counter on check
        for var in self.check_vars.values():
            var.trace_add("write", self._update_counter)

        # Error & Nav
        self.error_var = tk.StringVar()
        tk.Label(inner, textvariable=self.error_var,
                 font=FONTS["small"], fg=COLORS["danger"],
                 bg=COLORS["bg_primary"]).pack(pady=(14, 0))

        nav = tk.Frame(inner, bg=COLORS["bg_primary"])
        nav.pack(fill="x", pady=(12, 0))
        StyledButton(nav, "← Back", style="ghost",
                     command=lambda: self.controller.show_screen("body_part")).pack(side="left")
        StyledButton(nav, "Next: Medical Questions →", style="primary",
                     command=self._validate_and_next).pack(side="right")

    def _update_counter(self, *args):
        count = sum(1 for v in self.check_vars.values() if v.get())
        self.counter_label.config(text=f"{count} symptom{'s' if count != 1 else ''} selected")

    def _validate_and_next(self):
        selected = [s for s, v in self.check_vars.items() if v.get()]
        if len(selected) < 1:
            self.error_var.set("⚠  Please select at least one symptom.")
            return
        self.error_var.set("")
        self.controller.selected_symptoms = selected
        self.controller.show_screen("followup")


class FollowUpScreen(tk.Frame):
    """
    Screen 4 — Follow-up Medical Questions
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller  = controller
        self.answer_vars = {}
        self._build()

    def _build(self):
        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=50, pady=30)

        tk.Label(inner, text="Medical History",
                 font=FONTS["title_lg"], fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(inner,
                 text="Please answer these questions to help the AI provide a more accurate assessment",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"],
                 wraplength=720).pack(anchor="w", pady=(0, 20))
        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 20))

        for q_data in FOLLOWUP_QUESTIONS:
            q_id   = q_data["id"]
            q_text = q_data["question"]
            opts   = q_data["options"]

            card = Card(inner, padx=20, pady=16)
            card.pack(fill="x", pady=(0, 12))

            tk.Label(card, text=q_text,
                     font=FONTS["body_bold"],
                     fg=COLORS["text_white"],
                     bg=COLORS["bg_card"],
                     anchor="w", wraplength=680).pack(fill="x", pady=(0, 10))

            var = tk.StringVar(value="")
            self.answer_vars[q_id] = var

            opts_frame = tk.Frame(card, bg=COLORS["bg_card"])
            opts_frame.pack(fill="x")

            for i, opt in enumerate(opts):
                col = tk.Frame(opts_frame, bg=COLORS["bg_card"])
                col.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=2)
                opts_frame.columnconfigure(0, weight=1)
                opts_frame.columnconfigure(1, weight=1)

                rb = tk.Radiobutton(
                    col, text=opt,
                    variable=var, value=opt,
                    font=FONTS["body"],
                    fg=COLORS["text_primary"],
                    bg=COLORS["bg_card"],
                    selectcolor=COLORS["bg_input"],
                    activeforeground=COLORS["accent"],
                    activebackground=COLORS["bg_card"],
                    cursor="hand2", anchor="w",
                )
                rb.pack(anchor="w")

        # Error & Nav
        self.error_var = tk.StringVar()
        tk.Label(inner, textvariable=self.error_var,
                 font=FONTS["small"], fg=COLORS["danger"],
                 bg=COLORS["bg_primary"]).pack(pady=(14, 0))

        nav = tk.Frame(inner, bg=COLORS["bg_primary"])
        nav.pack(fill="x", pady=(12, 0))
        StyledButton(nav, "← Back", style="ghost",
                     command=lambda: self.controller.show_screen("symptoms")).pack(side="left")
        StyledButton(nav, "🤖  Get AI Diagnosis", style="primary",
                     command=self._validate_and_next).pack(side="right")

    def _validate_and_next(self):
        unanswered = [qid for qid, var in self.answer_vars.items() if not var.get()]
        if unanswered:
            self.error_var.set("⚠  Please answer all questions before continuing.")
            return
        self.error_var.set("")
        self.controller.followup_answers = {
            qid: var.get() for qid, var in self.answer_vars.items()
        }
        self.controller.show_screen("analyzing")


class AnalyzingScreen(tk.Frame):
    """
    Screen 5 — AI Analysis Loading Screen
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller  = controller
        self._anim_step  = 0
        self._anim_after = None
        self._build()

    def _build(self):
        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        center = tk.Frame(self, bg=COLORS["bg_primary"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="🤖",
                 font=("Segoe UI Emoji", 64),
                 bg=COLORS["bg_primary"],
                 fg=COLORS["accent"]).pack(pady=(0, 16))

        tk.Label(center, text="AI Analysis in Progress",
                 font=FONTS["title_lg"],
                 fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(pady=(0, 8))

        # Patient summary
        name = self.controller.patient_data.get("name", "Patient")
        parts = ", ".join(self.controller.selected_parts or [])
        symptoms_count = len(self.controller.selected_symptoms or [])

        tk.Label(center,
                 text=f"Analyzing {symptoms_count} symptoms for {name}",
                 font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"]).pack(pady=(0, 30))

        # Progress bar (canvas-based)
        self.progress_canvas = tk.Canvas(center, width=400, height=20,
                                          bg=COLORS["bg_card"],
                                          highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 12))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 20, fill=COLORS["accent"], outline="")

        self.status_var = tk.StringVar(value="Connecting to AI...")
        tk.Label(center, textvariable=self.status_var,
                 font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"]).pack()

        # Spinning dots
        self.dots_var = tk.StringVar(value="●  ○  ○  ○  ○")
        tk.Label(center, textvariable=self.dots_var,
                 font=("Segoe UI", 18),
                 fg=COLORS["accent"],
                 bg=COLORS["bg_primary"]).pack(pady=(20, 0))

        # Analysis steps
        steps_frame = tk.Frame(center, bg=COLORS["bg_card"],
                                padx=24, pady=16, relief="flat")
        steps_frame.pack(pady=(24, 0), ipadx=10, ipady=4)

        self.step_labels = []
        steps = [
            "Reviewing patient information",
            "Cross-referencing symptoms",
            "Analyzing medical history",
            "Generating diagnosis",
            "Preparing recommendations",
        ]
        for step in steps:
            lbl = tk.Label(steps_frame, text=f"○  {step}",
                            font=FONTS["body"],
                            fg=COLORS["text_muted"],
                            bg=COLORS["bg_card"],
                            anchor="w")
            lbl.pack(fill="x", pady=2)
            self.step_labels.append(lbl)

    def start_analysis(self):
        """Called when screen is shown. Kicks off the API call and animation."""
        self._anim_step = 0
        self._animate()
        self._call_api()

    def _animate(self):
        """Animate the progress bar and status indicators."""
        TOTAL_STEPS = 50
        if self._anim_step > TOTAL_STEPS:
            return

        progress = min(self._anim_step / TOTAL_STEPS, 0.95)
        bar_width = int(400 * progress)
        self.progress_canvas.coords(self.progress_bar, 0, 0, bar_width, 20)

        # Dots animation
        dots_patterns = [
            "●  ○  ○  ○  ○",
            "○  ●  ○  ○  ○",
            "○  ○  ●  ○  ○",
            "○  ○  ○  ●  ○",
            "○  ○  ○  ○  ●",
        ]
        self.dots_var.set(dots_patterns[self._anim_step % 5])

        # Step labels
        step_thresholds = [5, 15, 25, 35, 45]
        statuses = [
            "Connecting to AI...",
            "Cross-referencing symptoms...",
            "Analyzing medical history...",
            "Generating diagnosis...",
            "Preparing recommendations...",
        ]
        for i, (threshold, lbl) in enumerate(zip(step_thresholds, self.step_labels)):
            if self._anim_step >= threshold:
                lbl.config(text=f"✓  {lbl.cget('text')[3:]}",
                            fg=COLORS["accent"])
                if i < len(statuses):
                    next_status = statuses[min(i + 1, len(statuses) - 1)]
                    self.status_var.set(next_status)

        self._anim_step += 1
        self._anim_after = self.after(120, self._animate)

    def _call_api(self):
        get_diagnosis(
            patient    = self.controller.patient_data,
            body_parts = self.controller.selected_parts,
            symptoms   = self.controller.selected_symptoms,
            followups  = self.controller.followup_answers,
            callback   = self._on_success,
            error_callback = self._on_error,
        )

    def _on_success(self, result: dict):
        if self._anim_after:
            self.after_cancel(self._anim_after)
        # Complete the progress bar
        self.progress_canvas.coords(self.progress_bar, 0, 0, 400, 20)
        self.status_var.set("Analysis complete!")
        for lbl in self.step_labels:
            lbl.config(fg=COLORS["accent"])
        self.controller.diagnosis_result = result
        self.after(800, lambda: self.controller.show_screen("diagnosis"))

    def _on_error(self, error_msg: str):
        if self._anim_after:
            self.after_cancel(self._anim_after)
        messagebox.showerror("Analysis Error", error_msg)
        self.controller.show_screen("followup")


class DiagnosisScreen(tk.Frame):
    """
    Screen 6 — Diagnosis Results
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller = controller

    def refresh(self):
        """Rebuild the screen with current diagnosis data."""
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        result = self.controller.diagnosis_result or {}
        patient = self.controller.patient_data

        tk.Frame(self, bg=COLORS["accent"], height=4).pack(fill="x")

        outer, _, inner = make_scrollable_frame(self)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=45, pady=24)

        # ── Header ─────────────────────────────────────────────────────────
        header = tk.Frame(inner, bg=COLORS["bg_primary"])
        header.pack(fill="x", pady=(0, 20))

        tk.Label(header, text="Consultation Results",
                 font=FONTS["title_lg"],
                 fg=COLORS["text_white"],
                 bg=COLORS["bg_primary"]).pack(side="left", anchor="w")

        # Action buttons top-right
        action_row = tk.Frame(header, bg=COLORS["bg_primary"])
        action_row.pack(side="right")
        StyledButton(action_row, "📄 Download Report", style="secondary",
                     command=self._download_report).pack(side="left", padx=(0, 8))
        StyledButton(action_row, "🔄 New Consultation", style="ghost",
                     command=self._restart).pack(side="left")

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 20))

        # ── Patient Summary Bar ────────────────────────────────────────────
        summary_bar = tk.Frame(inner, bg=COLORS["bg_secondary"], padx=20, pady=12)
        summary_bar.pack(fill="x", pady=(0, 20))

        for label, value in [
            ("Patient", patient.get("name", "N/A")),
            ("Age", f"{patient.get('age', 'N/A')} yrs"),
            ("Gender", patient.get("gender", "N/A")),
            ("Symptoms", str(len(self.controller.selected_symptoms or []))),
            ("Date", datetime.now().strftime("%d %b %Y")),
        ]:
            col = tk.Frame(summary_bar, bg=COLORS["bg_secondary"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=label, font=FONTS["small"],
                     fg=COLORS["text_muted"], bg=COLORS["bg_secondary"]).pack()
            tk.Label(col, text=value, font=FONTS["body_bold"],
                     fg=COLORS["text_white"], bg=COLORS["bg_secondary"]).pack()

        # ── Risk Level Banner ──────────────────────────────────────────────
        risk = result.get("risk_level", "Unknown").upper()
        risk_colors = {
            "LOW":      (COLORS["risk_low"],    "🟢", "#0a2e1f"),
            "MODERATE": (COLORS["risk_medium"], "🟡", "#2e2200"),
            "HIGH":     (COLORS["risk_high"],   "🔴", "#2e0a0a"),
            "CRITICAL": ("#ff00aa",             "🚨", "#2e0020"),
        }
        r_color, r_icon, r_bg = risk_colors.get(risk, (COLORS["info"], "ℹ️", COLORS["bg_card"]))

        risk_banner = tk.Frame(inner, bg=r_bg,
                                highlightthickness=2, highlightbackground=r_color,
                                padx=20, pady=14)
        risk_banner.pack(fill="x", pady=(0, 20))

        risk_left = tk.Frame(risk_banner, bg=r_bg)
        risk_left.pack(side="left")
        tk.Label(risk_left, text=r_icon, font=("Segoe UI Emoji", 28),
                 bg=r_bg).pack(side="left", padx=(0, 12))
        risk_text = tk.Frame(risk_left, bg=r_bg)
        risk_text.pack(side="left")
        tk.Label(risk_text, text=f"Risk Level: {risk}",
                 font=FONTS["title_sm"],
                 fg=r_color, bg=r_bg).pack(anchor="w")
        tk.Label(risk_text, text=result.get("risk_explanation", ""),
                 font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=r_bg,
                 wraplength=550, justify="left").pack(anchor="w")

        # Risk meter bar
        meter_frame = tk.Frame(risk_banner, bg=r_bg)
        meter_frame.pack(side="right")
        tk.Label(meter_frame, text="Risk Meter",
                 font=FONTS["small"], fg=COLORS["text_muted"],
                 bg=r_bg).pack()
        meter_canvas = tk.Canvas(meter_frame, width=120, height=12,
                                  bg=COLORS["bg_card"], highlightthickness=0)
        meter_canvas.pack()
        fill_map = {"LOW": 30, "MODERATE": 60, "HIGH": 85, "CRITICAL": 120}
        fill_px = fill_map.get(risk, 40)
        meter_canvas.create_rectangle(0, 0, fill_px, 12, fill=r_color, outline="")

        # ── Two-column layout ──────────────────────────────────────────────
        two_col = tk.Frame(inner, bg=COLORS["bg_primary"])
        two_col.pack(fill="x", pady=(0, 16))
        left_col  = tk.Frame(two_col, bg=COLORS["bg_primary"])
        right_col = tk.Frame(two_col, bg=COLORS["bg_primary"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right_col.pack(side="left", fill="both", expand=True)

        # ── Possible Conditions (left) ─────────────────────────────────────
        cond_card = Card(left_col, padx=18, pady=16)
        cond_card.pack(fill="x", pady=(0, 12))
        SectionHeader(cond_card, "Possible Conditions", icon="🔍",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 12))

        conditions = result.get("possible_conditions", [])
        prob_colors = {
            "High":     COLORS["danger"],
            "Moderate": COLORS["warning"],
            "Low":      COLORS["success"],
        }
        for cond in conditions:
            c_frame = tk.Frame(cond_card, bg=COLORS["bg_secondary"],
                                padx=14, pady=10)
            c_frame.pack(fill="x", pady=(0, 8))

            prob    = cond.get("probability", "N/A")
            p_color = prob_colors.get(prob, COLORS["info"])

            title_row = tk.Frame(c_frame, bg=COLORS["bg_secondary"])
            title_row.pack(fill="x")
            tk.Label(title_row, text=cond.get("name", "Unknown"),
                     font=FONTS["body_bold"],
                     fg=COLORS["text_white"],
                     bg=COLORS["bg_secondary"]).pack(side="left")

            prob_badge = tk.Label(title_row,
                                   text=f"  {prob}  ",
                                   font=FONTS["small"],
                                   fg="#000000", bg=p_color)
            prob_badge.pack(side="right")

            tk.Label(c_frame, text=cond.get("description", ""),
                     font=FONTS["small"],
                     fg=COLORS["text_secondary"],
                     bg=COLORS["bg_secondary"],
                     wraplength=310, justify="left", anchor="w").pack(fill="x", pady=(4, 0))

        # ── Immediate Actions (left bottom) ────────────────────────────────
        imm_card = Card(left_col, padx=18, pady=16)
        imm_card.pack(fill="x", pady=(0, 12))
        SectionHeader(imm_card, "Immediate Actions", icon="⚡",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 10))
        for action in result.get("immediate_actions", []):
            row = tk.Frame(imm_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="▶", fg=COLORS["accent"],
                     font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=action, font=FONTS["body"],
                     fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                     wraplength=300, justify="left", anchor="w").pack(side="left", fill="x")

        # ── Home Care (right) ──────────────────────────────────────────────
        home_card = Card(right_col, padx=18, pady=16)
        home_card.pack(fill="x", pady=(0, 12))
        SectionHeader(home_card, "Home Care", icon="🏠",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 10))
        for item in result.get("home_care", []):
            row = tk.Frame(home_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="•", fg=COLORS["accent"],
                     font=FONTS["title_md"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=item, font=FONTS["body"],
                     fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                     wraplength=300, justify="left", anchor="w").pack(side="left", fill="x")

        # ── Warning Signs (right) ──────────────────────────────────────────
        warn_card = Card(right_col, padx=18, pady=16,
                          bg=COLORS["bg_card"],
                          highlightbackground=COLORS["danger"])
        warn_card.pack(fill="x", pady=(0, 12))
        SectionHeader(warn_card, "⚠ Warning Signs", bg=COLORS["bg_card"]).pack(fill="x",
                                                                                  pady=(0, 10))
        for item in result.get("warning_signs", []):
            row = tk.Frame(warn_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="!", fg=COLORS["danger"],
                     font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=item, font=FONTS["body"],
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     wraplength=300, justify="left", anchor="w").pack(side="left", fill="x")

        # ── Tests & Lifestyle (full width) ─────────────────────────────────
        bottom_row = tk.Frame(inner, bg=COLORS["bg_primary"])
        bottom_row.pack(fill="x", pady=(0, 16))

        tests_card = Card(bottom_row, padx=18, pady=16)
        tests_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        SectionHeader(tests_card, "Recommended Tests", icon="🔬",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 10))
        for t in result.get("recommended_tests", []):
            row = tk.Frame(tests_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="🔬", font=("Segoe UI Emoji", 11),
                     bg=COLORS["bg_card"]).pack(side="left", padx=(0, 6))
            tk.Label(row, text=t, font=FONTS["body"],
                     fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                     wraplength=250, justify="left", anchor="w").pack(side="left")

        life_card = Card(bottom_row, padx=18, pady=16)
        life_card.pack(side="left", fill="both", expand=True)
        SectionHeader(life_card, "Lifestyle Advice", icon="✦",
                      bg=COLORS["bg_card"]).pack(fill="x", pady=(0, 10))
        for item in result.get("lifestyle_advice", []):
            row = tk.Frame(life_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="✦", fg=COLORS["accent"],
                     font=FONTS["body"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 6))
            tk.Label(row, text=item, font=FONTS["body"],
                     fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                     wraplength=260, justify="left", anchor="w").pack(side="left")

        # ── Doctor Note ────────────────────────────────────────────────────
        note = result.get("doctor_note", "")
        if note:
            note_card = tk.Frame(inner, bg=COLORS["bg_secondary"],
                                  padx=20, pady=16,
                                  highlightthickness=1,
                                  highlightbackground=COLORS["accent"])
            note_card.pack(fill="x", pady=(0, 16))
            tk.Label(note_card, text="💙  Note from your AI Doctor",
                     font=FONTS["title_sm"],
                     fg=COLORS["accent"],
                     bg=COLORS["bg_secondary"]).pack(anchor="w", pady=(0, 8))
            tk.Label(note_card, text=f'"{note}"',
                     font=("Segoe UI", 11, "italic"),
                     fg=COLORS["text_primary"],
                     bg=COLORS["bg_secondary"],
                     wraplength=780, justify="left").pack(anchor="w")

        # ── Disclaimer ─────────────────────────────────────────────────────
        disc = tk.Frame(inner, bg=COLORS["bg_card"], padx=16, pady=10)
        disc.pack(fill="x", pady=(0, 24))
        tk.Label(disc,
                 text="⚠️  This is an AI-generated preliminary assessment for informational purposes only. "
                       "Always consult a qualified healthcare professional for medical advice. "
                       "In emergencies, call emergency services immediately.",
                 font=FONTS["small"],
                 fg=COLORS["text_muted"],
                 bg=COLORS["bg_card"],
                 wraplength=800, justify="left").pack()

        # ── Bottom navigation ──────────────────────────────────────────────
        nav = tk.Frame(inner, bg=COLORS["bg_primary"])
        nav.pack(fill="x", pady=(0, 10))
        StyledButton(nav, "📄 Download Report", style="secondary",
                     command=self._download_report).pack(side="left", padx=(0, 8))
        StyledButton(nav, "🔄 Start New Consultation", style="primary",
                     command=self._restart).pack(side="right")

    def _download_report(self):
        try:
            filepath = save_report(
                patient   = self.controller.patient_data,
                body_parts= self.controller.selected_parts,
                symptoms  = self.controller.selected_symptoms,
                followups = self.controller.followup_answers,
                diagnosis = self.controller.diagnosis_result,
            )
            # Ask user where to save a copy
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile=os.path.basename(filepath),
                title="Save Medical Report",
            )
            if save_path:
                import shutil
                shutil.copy2(filepath, save_path)
                messagebox.showinfo("Report Saved",
                                     f"✅ Your medical report has been saved to:\n{save_path}")
            else:
                # Open the auto-saved one
                messagebox.showinfo("Report Saved",
                                     f"✅ Report saved to:\n{filepath}")
                os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save report:\n{e}")

    def _restart(self):
        self.controller.reset_data()
        self.controller.show_screen("welcome")


# ══════════════════════════════════════════════════════════════════════════════
#  NAVIGATION BAR
# ══════════════════════════════════════════════════════════════════════════════

class NavigationBar(tk.Frame):
    """Top navigation bar with step indicators."""

    STEPS = [
        ("welcome",      "Welcome",       "🏠"),
        ("registration", "Patient",       "👤"),
        ("body_part",    "Body Area",     "🫁"),
        ("symptoms",     "Symptoms",      "🩺"),
        ("followup",     "History",       "📋"),
        ("analyzing",    "Analyzing",     "🤖"),
        ("diagnosis",    "Results",       "✅"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_secondary"],
                          pady=10, **kwargs)
        self._step_labels = {}
        self._build()

    def _build(self):
        # Logo left
        logo_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        logo_frame.pack(side="left", padx=(16, 0))
        tk.Label(logo_frame, text="🏥",
                 font=("Segoe UI Emoji", 16),
                 fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"]).pack(side="left")
        tk.Label(logo_frame, text=" AnywhereDr",
                 font=("Segoe UI", 13, "bold"),
                 fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"]).pack(side="left")

        # Steps center
        steps_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        steps_frame.pack(side="left", expand=True)

        for screen_id, label, icon in self.STEPS:
            if screen_id in ("welcome", "analyzing"):
                continue  # Don't show in progress bar
            col = tk.Frame(steps_frame, bg=COLORS["bg_secondary"])
            col.pack(side="left", padx=8)
            lbl = tk.Label(col,
                            text=f"{icon} {label}",
                            font=FONTS["small"],
                            fg=COLORS["text_muted"],
                            bg=COLORS["bg_secondary"])
            lbl.pack()
            # Dot indicator
            dot = tk.Label(col, text="·",
                            font=("Segoe UI", 14),
                            fg=COLORS["text_muted"],
                            bg=COLORS["bg_secondary"])
            dot.pack()
            self._step_labels[screen_id] = (lbl, dot)

    def set_active(self, screen_id: str):
        ordered = ["registration", "body_part", "symptoms", "followup", "diagnosis"]
        try:
            active_idx = ordered.index(screen_id) if screen_id in ordered else -1
        except ValueError:
            active_idx = -1

        for sid, (lbl, dot) in self._step_labels.items():
            try:
                idx = ordered.index(sid)
            except ValueError:
                idx = -1

            if idx < active_idx:
                # Completed
                lbl.config(fg=COLORS["success"])
                dot.config(fg=COLORS["success"], text="✓")
            elif idx == active_idx:
                # Active
                lbl.config(fg=COLORS["accent"])
                dot.config(fg=COLORS["accent"], text="●")
            else:
                # Upcoming
                lbl.config(fg=COLORS["text_muted"])
                dot.config(fg=COLORS["text_muted"], text="·")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class AnywhereDrApp(tk.Tk):
    """
    Main application controller.
    Manages screen navigation and shared state.
    """

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — {APP_TAGLINE}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(bg=COLORS["bg_primary"])

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WINDOW_WIDTH)  // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # Custom title bar style
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # Configure ttk scrollbar style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                         background=COLORS["scrollbar_thumb"],
                         troughcolor=COLORS["scrollbar_bg"],
                         arrowcolor=COLORS["text_secondary"])

        # ── Shared state ──────────────────────────────────────────────────
        self.patient_data       = {}
        self.selected_parts     = []
        self.selected_symptoms  = []
        self.followup_answers   = {}
        self.diagnosis_result   = None

        # ── Navigation Bar ────────────────────────────────────────────────
        self.nav_bar = NavigationBar(self)
        self.nav_bar.pack(fill="x", side="top")

        # Thin separator
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

        # ── Screen container ──────────────────────────────────────────────
        self.container = tk.Frame(self, bg=COLORS["bg_primary"])
        self.container.pack(fill="both", expand=True)

        # ── Build all screens ─────────────────────────────────────────────
        self.screens = {}
        self._init_screens()

        # ── Show welcome ──────────────────────────────────────────────────
        self.current_screen = None
        self.show_screen("welcome")

    def _init_screens(self):
        self.screens["welcome"]      = WelcomeScreen(self.container, self)
        self.screens["registration"] = RegistrationScreen(self.container, self)
        self.screens["body_part"]    = BodyPartScreen(self.container, self)
        self.screens["symptoms"]     = SymptomScreen(self.container, self)
        self.screens["followup"]     = FollowUpScreen(self.container, self)
        self.screens["analyzing"]    = AnalyzingScreen(self.container, self)
        self.screens["diagnosis"]    = DiagnosisScreen(self.container, self)

        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_screen(self, name: str):
        """Switch to the named screen."""
        screen = self.screens.get(name)
        if screen is None:
            return

        # Run screen-specific preparation
        if name == "symptoms":
            self.screens["symptoms"].refresh()
        elif name == "analyzing":
            pass  # Will be triggered after raise
        elif name == "diagnosis":
            self.screens["diagnosis"].refresh()

        screen.lift()
        self.nav_bar.set_active(name)
        self.current_screen = name

        if name == "analyzing":
            self.screens["analyzing"].start_analysis()

    def reset_data(self):
        """Clear all session data for a new consultation."""
        self.patient_data      = {}
        self.selected_parts    = []
        self.selected_symptoms = []
        self.followup_answers  = {}
        self.diagnosis_result  = None

        # Rebuild stateful screens
        for name in ("registration", "body_part", "symptoms", "followup"):
            old = self.screens[name]
            old.destroy()

        self.screens["registration"] = RegistrationScreen(self.container, self)
        self.screens["body_part"]    = BodyPartScreen(self.container, self)
        self.screens["symptoms"]     = SymptomScreen(self.container, self)
        self.screens["followup"]     = FollowUpScreen(self.container, self)

        for name in ("registration", "body_part", "symptoms", "followup"):
            self.screens[name].place(relx=0, rely=0, relwidth=1, relheight=1)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    app = AnywhereDrApp()
    app.mainloop()


if __name__ == "__main__":
    main()
