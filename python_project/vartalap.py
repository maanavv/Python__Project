"""
==================================================
VARTALAP
Terminal-Based Social Networking Prototype
==================================================

Institution   : National Forensic Sciences University, Gandhinagar
School        : School of Cyber Security and Digital Forensics
Programme     : B.Tech–M.Tech in Computer Science and Engineering (Cyber Security)

Framework     : Textual (TUI Framework)
==================================================
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Header, Footer, Button, Input
from textual.screen import Screen


# ===================== BANNER =====================
class Banner(Static):
    def render(self):
        return (
            "╔════════════════════╗\n"
            "║     VARTALAP       ║\n"
            "║  CLI SOCIAL NET    ║\n"
            "╚════════════════════╝"
        )


# ===================== COMMENT SCREEN =====================
class CommentScreen(Screen):
    def __init__(self, post):
        super().__init__()
        self.post = post

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(f"COMMENT ON: {self.post['title']}", classes="title")
        self.input = Input(placeholder="Write a comment…")
        yield self.input
        yield Button("Submit", id="submit")
        yield Static("[ ESC to cancel ]", classes="hint")
        yield Footer()

    def on_mount(self):
        self.input.focus()

    def on_button_pressed(self, event):
        if event.button.id == "submit" and self.input.value:
            self.post["comments"].append(f"anon@vartalap: {self.input.value}")
            self.app.feed.render_feed()
            self.app.pop_screen()

    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()


# ===================== CHAT =====================
class ChatScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("SECURE CHAT", classes="title")

        yield Vertical(id="chat-log")

        yield Input(placeholder="Type message…", id="chat-input")
        yield Button("Send", id="send")

        yield Static("[ ESC to go back ]", classes="hint")
        yield Footer()

    def on_mount(self):
        self.refresh_chat()
        self.query_one("#chat-input", Input).focus()

    def refresh_chat(self):
        chat_log = self.query_one("#chat-log", Vertical)
        chat_log.remove_children()

        for msg in self.app.chat_messages:
            chat_log.mount(Static(msg, classes="comment"))

    def on_button_pressed(self, event):
        if event.button.id == "send":
            input_box = self.query_one("#chat-input", Input)
            if input_box.value.strip():
                self.app.chat_messages.append(f"you@vartalap: {input_box.value}")
                input_box.value = ""
                self.refresh_chat()

    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()



# ===================== PROFILE =====================
class ProfileScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("USER PROFILE", classes="title")
        yield Static("Username : anon@vartalap")
        yield Static("Reputation: 42")
        yield Static("Rank      : Prototype User")
        yield Static("[ ESC to return ]", classes="hint")
        yield Footer()

    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()


# ===================== CREATE POST =====================
class CreatePostScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("CREATE POST", classes="title")
        self.title_input = Input(placeholder="Title")
        self.body_input = Input(placeholder="Content")
        yield self.title_input
        yield self.body_input
        yield Button("Publish", id="publish")
        yield Static("[ ESC to cancel ]", classes="hint")
        yield Footer()

    def on_mount(self):
        self.title_input.focus()

    def on_button_pressed(self, event):
        if event.button.id == "publish":
            if self.title_input.value and self.body_input.value:
                self.app.posts.insert(0, {
                    "title": self.title_input.value,
                    "body": self.body_input.value,
                    "likes": 0,
                    "comments": []
                })
                self.app.feed.render_feed()
                self.app.pop_screen()

    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()


# ===================== POST CARD =====================
class PostCard(Vertical):
    def __init__(self, post):
        super().__init__()
        self.post = post

    def compose(self) -> ComposeResult:
        yield Static(self.post["title"], classes="post-title")
        yield Static(self.post["body"])
        self.stats = Static(f"♥ {self.post['likes']}  💬 {len(self.post['comments'])}")
        yield self.stats
        with Horizontal():
            yield Button("LIKE", id="like")
            yield Button("COMMENT", id="comment")

    def on_button_pressed(self, event):
        if event.button.id == "like":
            self.post["likes"] += 1
        elif event.button.id == "comment":
            self.app.push_screen(CommentScreen(self.post))
            return
        self.stats.update(f"♥ {self.post['likes']}  💬 {len(self.post['comments'])}")


# ===================== FEED =====================
class Feed(VerticalScroll):
    can_focus = True

    def clear_children(self):
        for c in list(self.children):
            c.remove()

    def render_feed(self):
        self.clear_children()
        self.mount(Static("PACKET STREAM :: HOME", classes="title"))
        for post in self.app.posts:
            self.mount(PostCard(post))
        self.mount(Static("[ TAB navigate | ENTER select ]", classes="hint"))

    def on_ready(self):
        self.render_feed()
        self.focus()


# ===================== LEFT PANEL =====================
class LeftPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Banner()
        yield Button("Home", id="home")
        yield Button("Create Post", id="create")
        yield Button("Chats", id="chats")
        yield Button("Profile", id="profile")


# ===================== MAIN APP =====================
class Vartalap(App):

    BINDINGS = [
        ("tab", "focus_next"),
        ("shift+tab", "focus_previous"),
        ("enter", "press"),
    ]

    CSS = """
    Screen { background: black; color: #00ffcc; }
    Button { border: heavy #00ffcc; background: black; color: #00ffcc; }
    *:focus { border: heavy #00ffaa; }
    LeftPanel { width: 28; border: solid #00ffcc; padding: 1; }
    Feed { width: 1fr; border: solid #00ffcc; padding: 1; }
    .title { text-style: bold; color: #00ffaa; }
    .post-title { text-style: bold; color: #00ffaa; }
    .comment { border: solid #00ffcc; padding: 1; margin-bottom: 1; }
    .hint { color: #777777; }
    """

    def on_mount(self):
        self.posts = [
            {
                "title": "GhostShell",
                "body": "Minimal CLI remote shell focusing on encrypted I/O.",
                "likes": 0,
                "comments": []
            },
            {
                "title": "CipherLog",
                "body": "Encrypted logging utility designed for forensic-safe audits.",
                "likes": 0,
                "comments": []
            }
        ]
        self.chat_messages = [
            "alice@node: You online?",
            "bob@node: New blueprint dropped."
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal():
            self.left = LeftPanel()
            self.feed = Feed()
            yield self.left
            yield self.feed
        yield Footer()

    def action_press(self):
        if isinstance(self.focused, Button):
            self.focused.press()

    def on_button_pressed(self, event):
        if event.button.id == "home":
            self.feed.render_feed()
        elif event.button.id == "create":
            self.push_screen(CreatePostScreen())
        elif event.button.id == "chats":
            self.push_screen(ChatScreen())
        elif event.button.id == "profile":
            self.push_screen(ProfileScreen())


# ===================== ENTRY =====================
if __name__ == "__main__":
    Vartalap().run()