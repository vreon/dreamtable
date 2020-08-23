import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, Key, MouseButton

HOTKEYS = {
    Key.Q: Tool.MOVE,
    Key.W: Tool.PENCIL,
    Key.E: Tool.DROPPER,
    Key.R: Tool.GRID,
    Key.T: Tool.CELLREF,
    Key.Y: Tool.CELLREF_DROPPER,
    Key.U: Tool.EGG,
}


class ToolSwitcherController(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context

        # Update the current tool if we pressed a tool switcher
        for ent, (switcher, hover) in self.world.get_components(
            c.ToolSwitcher, c.Hoverable
        ):
            if hover.hovered and hal.is_mouse_button_pressed(MouseButton.LEFT):
                hal.clear_mouse_button_pressed(MouseButton.LEFT)
                context.tool = switcher.tool

        # Switch to a tool if we pressed its hotkey
        for key, tool in HOTKEYS.items():
            if hal.is_key_pressed(key):
                context.tool = tool

        # Tool-specific temporary overrides
        # todo hmmmm this is weird
        is_overriding = False
        if (
            context.tool == Tool.PENCIL or context.underlying_tool == Tool.PENCIL
        ) and hal.is_key_down(Key.LEFT_ALT):
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
