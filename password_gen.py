import secrets
import string
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk
from tkinter.constants import DISABLED, E, END, NORMAL, VERTICAL
from typing import Iterable, Collection, Protocol, Literal


TraceMode = Literal[
    'r',  # read
    'w',  # write
    'u',  # undefine
    'a',  # array
]


class TkTrace(Protocol):
    def __call__(self, name: str, index: str, mode: TraceMode): ...


class OptControl:
    NAMES = ('ascii_lowercase', 'ascii_uppercase', 'digits', 'punctuation')

    def __init__(self, parent: tk.Widget, name: str, trace: TkTrace) -> None:
        self.name = name
        self.var = tk.BooleanVar(parent, name=name, value=True)
        self.var.trace(mode='w', callback=trace)
        self.label = ttk.Label(parent, text=name)
        self.check = ttk.Checkbutton(parent, variable=self.var)

    @classmethod
    def make_all(cls, parent: tk.Widget, trace: TkTrace) -> Iterable['OptControl']:
        for name in cls.NAMES:
            yield cls(parent, name, trace)


class GUI:
    def __init__(self, parent: tk.Tk):
        self.root = tk.Frame(parent)
        self.root.pack()
        self.length = tk.IntVar(self.root, value=16)
        self.length.trace('w', self.opt_changed)
        self.opts = tuple(OptControl.make_all(self.root, self.opt_changed))
        self.password_text = self.create_widgets()
        self.style()
        self.opt_changed()

    @property
    def selected_opts(self) -> Iterable[str]:
        for opt in self.opts:
            if opt.var.get():
                yield opt.name

    def generate_password(self) -> None:
        # You can only insert to Text if the state is NORMAL
        self.password_text.config(state=NORMAL)
        self.password_text.delete('1.0', END)   # Clears out password_text
        self.password_text.insert(END, self.generator.gen_password())
        self.password_text.config(state=DISABLED)

    def opt_changed(self, *args) -> None:
        self.generator = PasswordGenerator(
            length=self.length.get(),
            opts=tuple(self.selected_opts),
        )

    def create_widgets(self) -> tk.Text:
        length_label = ttk.Label(self.root, text='Password length')
        length_label.grid(column=0, row=0, rowspan=4, sticky=E)

        generate_btn = ttk.Button(
            self.root, text='Generate password', command=self.generate_password)
        generate_btn.grid(column=0, row=4, columnspan=5, padx=4, pady=2)

        password_text = tk.Text(self.root, height=4, width=32, state=DISABLED)
        password_text.grid(column=0, row=6, columnspan=5, padx=4, pady=2)

        length_spinbox = ttk.Spinbox(
            self.root, from_=1, to=128, width=3, textvariable=self.length)
        length_spinbox.grid(column=1, row=0, rowspan=4, padx=4, pady=2)

        separator = ttk.Separator(self.root, orient=VERTICAL)
        separator.grid(column=2, row=0, rowspan=4, ipady=45)

        for row, opt in enumerate(self.opts):
            opt.label.grid(column=3, row=row, sticky=E, padx=4)
            opt.check.grid(column=4, row=row, padx=4, pady=2)

        self.root.grid(padx=10, pady=10)

        return password_text

    def style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use('clam')


@dataclass(frozen=True)
class PasswordGenerator:
    length: int
    opts: Collection[str]
    allowed_chars: str = field(init=False)

    def __post_init__(self):
        super().__setattr__('allowed_chars', ''.join(self._gen_allowed_chars()))

    def gen_password(self) -> str:
        return ''.join(self._gen_password_chars())

    def _gen_allowed_chars(self) -> Iterable[str]:
        for opt in self.opts:
            yield getattr(string, opt)

    def _gen_password_chars(self) -> Iterable[str]:
        for _ in range(self.length):
            yield secrets.choice(self.allowed_chars)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Password Generator')
    GUI(root)
    root.mainloop()