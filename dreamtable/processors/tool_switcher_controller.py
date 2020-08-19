import esper
from raylib.pyray import PyRay

from .. import components as c
from ..constants import Tool


class ToolSwitcherController(esper.Processor):
    def __init__(self, pyray: PyRay) -> None:
        self.hotkeys = {
            pyray.KEY_Q: Tool.MOVE,
            pyray.KEY_W: Tool.PENCIL,
            pyray.KEY_E: Tool.DROPPER,
            pyray.KEY_R: Tool.GRID,
            pyray.KEY_T: Tool.CELLREF,
            pyray.KEY_Y: Tool.CELLREF_DROPPER,
            pyray.KEY_U: Tool.EGG,
        }

    def process(self, pyray: PyRay) -> None:
        context = self.world.context

        # Update the current tool if we pressed a tool switcher
        for ent, (switcher, press) in self.world.get_components(
            c.ToolSwitcher, c.Pressable
        ):
            if press.pressed:
                context.tool = switcher.tool

        # Switch to a tool if we pressed its hotkey
        for key, tool in self.hotkeys.items():
            if pyray.is_key_pressed(key):
                context.tool = tool

        # Tool-specific temporary overrides
        # todo hmmmm this is weird
        is_overriding = False
        if (
            context.tool == Tool.PENCIL or context.underlying_tool == Tool.PENCIL
        ) and pyray.is_key_down(pyray.KEY_LEFT_ALT):
            context.tool = Tool.DROPPER
            context.underlying_tool = Tool.PENCIL
            is_overriding = True

        if context.underlying_tool and not is_overriding:
            context.tool = context.underlying_tool
            context.underlying_tool = None

        # Update the lit state of any buttons that represent the currently
        # selected tool
        for ent, (switcher, btn) in self.world.get_components(c.ToolSwitcher, c.Button):
            btn.lit = context.tool == switcher.tool
