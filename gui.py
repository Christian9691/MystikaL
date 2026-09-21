"""GUI for PussyCat IDE.

tkinter-based desktop interface for code editing, execution, and output display.
"""

import tkinter as tk
from tkinter import ttk
from lexer import tokenize
from transpiler import transpile
from executor import execute
from constants import KEYWORD_MAP


class PussyCatIDE:
    """Main IDE window with split-panel layout."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PussyCat IDE")
        self.root.geometry("1200x800")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Keyword bar
        self.keyword_bar = tk.Frame(self.root, bg="#2d2d44", height=40)
        self.keyword_bar.pack(side=tk.TOP, fill=tk.X)
        
        # Main split pane
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=4, sashrelief=tk.SUNKEN)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left frame (editor)
        self.left_frame = tk.Frame(self.main_pane, bg="#1e1e2e")
        self.main_pane.add(self.left_frame, minsize=400)
        
        self.panel_label_left = tk.Label(self.left_frame, text="YOUR CODE", bg="#1e1e2e", fg="#e8d5b7", font=("Courier New", 10, "bold"))
        self.panel_label_left.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        self.editor_frame = tk.Frame(self.left_frame, bg="#1e1e2e")
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.line_numbers = tk.Text(self.editor_frame, width=4, state="disabled", bg="#1e1e2e", fg="#7a7a9a", font=("Courier New", 11), takefocus=0, highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor = tk.Text(self.editor_frame, bg="#1e1e2e", fg="#e8d5b7", insertbackground="#f4a261", font=("Courier New", 11), undo=True, wrap=tk.NONE, highlightthickness=0)
        self.editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Right frame (output)
        self.right_frame = tk.Frame(self.main_pane, bg="#1e1e2e")
        self.main_pane.add(self.right_frame, minsize=400)
        
        self.panel_label_right = tk.Label(self.right_frame, text="OUTPUT", bg="#1e1e2e", fg="#e8d5b7", font=("Courier New", 10, "bold"))
        self.panel_label_right.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        self.output = tk.Text(self.right_frame, state="disabled", bg="#1e1e2e", fg="#e8d5b7", font=("Courier New", 11), wrap=tk.WORD, highlightthickness=0)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#2d2d44", height=30)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="● ready", bg="#2d2d44", fg="#7a7a9a", font=("Courier New", 10))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind events
        self.editor.bind("<Tab>", self._on_tab)
        self.editor.bind("<Control-Return>", self._on_ctrl_enter)
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<<Modified>>", self._on_modified)
        
        # Initialize line numbers
        self._update_line_numbers()
        
        # Fill keyword bar
        self._fill_keyword_bar()
    
    def _fill_keyword_bar(self):
        """Fill keyword reference bar."""
        keyword_text = "  ".join(f"{k} → {v}" for k, v in KEYWORD_MAP.items())
        keyword_label = tk.Label(self.keyword_bar, text=keyword_text, bg="#2d2d44", fg="#c9b99a", font=("Courier New", 9))
        keyword_label.pack(side=tk.LEFT, padx=10)
    
    def _on_tab(self, event):
        """Handle Tab key - insert 4 spaces."""
        self.editor.insert(tk.INSERT, "    ")
        return "break"
    
    def _on_ctrl_enter(self, event):
        """Handle Ctrl+Enter - trigger run pipeline."""
        self.run_pipeline()
        return "break"
    
    def _on_key_release(self, event):
        """Handle key release - update line numbers."""
        self._update_line_numbers()
    
    def _on_modified(self, event):
        """Handle text modified event."""
        if self.editor.edit_modified():
            self._update_line_numbers()
            self.editor.edit_modified(False)
    
    def _update_line_numbers(self):
        """Update line number column."""
        line_count = int(self.editor.index("end-1c").split(".")[0])
        new_lines = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", new_lines)
        self.line_numbers.config(state="disabled")
    
    def run_pipeline(self):
        """Execute the full run pipeline: tokenize → transpile → execute."""
        self.update_status("running")
        
        source = self.editor.get("1.0", tk.END).strip()
        
        # Tokenize
        result = tokenize(source)
        if result.error:
            self.display_error(result.error)
            self.update_status("error")
            return
        
        # Transpile
        transpile_result = transpile(result.tokens)
        self.display_python(transpile_result.python)
        
        # Execute
        exec_result = execute(transpile_result.python, transpile_result.line_map)
        
        if exec_result.stdout:
            self.display_output(exec_result.stdout)
        
        if exec_result.error:
            self.display_error(exec_result.error)
            self.update_status("error")
        else:
            self.update_status("ok")
    
    def update_status(self, status: str):
        """Update status bar with current state."""
        status_colors = {
            "ready": "#7a7a9a",
            "running": "#f4a261",
            "ok": "#6bcb77",
            "error": "#ff6b6b"
        }
        status_texts = {
            "ready": "● ready",
            "running": "● running...",
            "ok": "● ok",
            "error": "● error"
        }
        self.status_label.config(fg=status_colors.get(status, "#7a7a9a"), text=status_texts.get(status, "● ready"))
    
    def display_python(self, python_code: str):
        """Display generated Python code in output pane."""
        self.output.config(state="normal")
        self.output.insert(tk.END, f"--- Generated Python ---\n{python_code}\n\n", "python_header")
        self.output.config(state="disabled")
    
    def display_output(self, output: str):
        """Display execution stdout in output pane."""
        self.output.config(state="normal")
        self.output.insert(tk.END, f"--- Output ---\n{output}\n\n", "output_header")
        self.output.config(state="disabled")
    
    def display_error(self, error: str):
        """Display error in output pane with color coding."""
        self.output.config(state="normal")
        self.output.insert(tk.END, f"--- Error ---\n{error}\n\n", "error_header")
        self.output.config(state="disabled")
    
    def clear(self):
        """Clear editor and output panels."""
        self.editor.delete("1.0", tk.END)
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")
        self.update_status("ready")


def main():
    """Entry point for the IDE."""
    root = tk.Tk()
    app = PussyCatIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
