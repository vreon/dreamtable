from pathlib import Path

import esper
from raylib.pyray import PyRay

from . import components as c
from . import processors as p
from .constants import PositionSpace, Tool

pkg_path = Path(__file__).parent


def run() -> None:
    pyray = PyRay()

    # pyray.set_config_flags(pyray.FLAG_WINDOW_RESIZABLE)
    pyray.init_window(800, 600, "Dream Table")
    pyray.set_target_fps(60)

    world = esper.World()
    world.context = c.WorldContext(
        cameras={PositionSpace.SCREEN: pyray.Camera2D((0, 0), (0, 0), 0, 3)},
        theme=c.Theme(
            font=pyray.load_font(str(pkg_path / "resources/fonts/alpha_beta.png"))
        ),
    )

    # Spawn initial entities
    world.create_entity(
        c.Name("Camera"),
        c.Camera(active=True, camera_2d=pyray.Camera2D((0, 0), (0, 0), 0, 4)),
    )
    world.create_entity(c.Name("Origin"), c.Position(), c.PositionMarker())
    world.create_entity(
        c.Name("Minor grid"),
        c.BackgroundGrid(world.context.theme.color_grid_minor),
        c.Extent(8, 8),
    )
    world.create_entity(
        c.Name("Major grid"),
        c.BackgroundGrid(world.context.theme.color_grid_major),
        c.Extent(32, 32),
    )

    # debug: a draggable to drag around
    world.create_entity(
        c.Name("Draggable"),
        c.Position(214, 2, space=PositionSpace.SCREEN),
        c.Extent(50, 12),
        c.DebugEntity(),
        c.Hoverable(),
        c.Draggable(),
        c.Selectable(),
    )

    # debug: a canvas with a preloaded palette image
    world.create_entity(
        c.Name("Sweetie 16"),
        c.Canvas(),
        c.Position(),
        c.Extent(),
        c.Image(filename=str(pkg_path / "resources/palettes/sweetie-16-8x.png")),
        c.Draggable(),
        c.Hoverable(),
        c.Selectable(),
        c.Deletable(),
    )

    # debug: tool buttons
    world.create_entity(
        c.Name("Move"),
        c.Button(),
        c.ToolSwitcher(Tool.MOVE),
        c.Pressable(),
        c.Position(2 + 8 * 0, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/hand.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Pencil"),
        c.Button(),
        c.ToolSwitcher(Tool.PENCIL),
        c.Pressable(),
        c.Position(2 + 8 * 1, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/pencil.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Dropper"),
        c.Button(),
        c.ToolSwitcher(Tool.DROPPER),
        c.Pressable(),
        c.Position(2 + 8 * 2, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/dropper.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Grid"),
        c.Button(),
        c.ToolSwitcher(Tool.GRID),
        c.Pressable(),
        c.Position(2 + 8 * 3, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/grid.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Cellref"),
        c.Button(),
        c.ToolSwitcher(Tool.CELLREF),
        c.Pressable(),
        c.Position(2 + 8 * 4, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/cellref.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Cellref Dropper"),
        c.Button(),
        c.ToolSwitcher(Tool.CELLREF_DROPPER),
        c.Pressable(),
        c.Position(2 + 8 * 5, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/cellref_dropper.png")),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Mystery Egg"),
        c.Button(),
        c.ToolSwitcher(Tool.EGG),
        c.Pressable(),
        c.Position(2 + 8 * 6, 2, space=PositionSpace.SCREEN),
        c.Extent(8, 8),
        c.Image(filename=str(pkg_path / "resources/icons/egg.png")),
        c.Hoverable(),
    )

    # Register controllers and renderers (flavors of processors)
    for processor in [
        # global state and input
        p.CameraContextController(),
        p.MouseController(),
        # controllers
        p.PencilToolController(),
        p.DropperToolController(),
        p.GridToolController(),
        p.EggToolController(),
        p.DragController(),
        p.HoverController(),
        p.PressController(),
        p.BoxSelectionController(),
        p.ImageController(),
        p.ToolSwitcherController(pyray),
        p.CanvasExportController(),
        p.CameraController(),
        p.MotionController(),
        p.WanderingController(),
        p.EggTimerController(),
        p.TinyFriendController(),
        # renderers (world)
        p.BackgroundGridRenderer(),
        p.PositionMarkerRenderer(),
        p.CanvasRenderer(),
        p.SpriteRegionRenderer(),
        p.DebugEntityRenderer(),
        # renderers (ui)
        p.BoxSelectionRenderer(),
        p.ButtonRenderer(),
        p.DropperToolRenderer(),
        p.PencilToolRenderer(),
        p.GridToolRenderer(),
        # cleanup
        p.SelectableDeleteController(),
        p.ImageDeleteController(),
        p.FinalDeleteController(),
    ]:
        world.add_processor(processor)

    while not pyray.window_should_close():
        pyray.begin_drawing()
        pyray.clear_background(world.context.theme.color_background)
        world.process(pyray)
        pyray.end_drawing()

    pyray.close_window()
