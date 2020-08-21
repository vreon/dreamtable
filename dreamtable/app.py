import esper

from dreamtable import components as c
from dreamtable import processors as p
from dreamtable.constants import PositionSpace, Tool
from dreamtable.hal import Camera
from dreamtable.hal.pyray import PyRayHAL
from dreamtable.geom import Vec2


def run() -> None:
    hal = PyRayHAL()
    hal.init_window(800, 600, "Dream Table")

    font = hal.load_font("res://fonts/alpha_beta.png")

    img_sweetie = hal.load_image("res://palettes/sweetie-16-8x.png")
    img_hand = hal.load_image("res://icons/hand.png")
    img_pencil = hal.load_image("res://icons/pencil.png")
    img_dropper = hal.load_image("res://icons/dropper.png")
    img_grid = hal.load_image("res://icons/grid.png")
    img_cellref = hal.load_image("res://icons/cellref.png")
    img_cellref_dropper = hal.load_image("res://icons/cellref_dropper.png")
    img_egg = hal.load_image("res://icons/egg.png")

    world = esper.World()
    world.context = c.WorldContext(
        cameras={PositionSpace.SCREEN: Camera(zoom=3)}, theme=c.Theme(font=font),
    )

    # Spawn initial entities
    world.create_entity(
        c.Name("Camera"), c.Camera(active=True, camera=Camera(zoom=4)),
    )
    world.create_entity(
        c.Name("Origin"), c.Position(), c.PositionMarker(),
    )
    world.create_entity(
        c.Name("Minor grid"),
        c.BackgroundGrid(world.context.theme.color_grid_minor),
        c.Extent(Vec2(8, 8)),
    )
    world.create_entity(
        c.Name("Major grid"),
        c.BackgroundGrid(world.context.theme.color_grid_major),
        c.Extent(Vec2(32, 32)),
    )

    # debug: a draggable to drag around (screen space)
    world.create_entity(
        c.Name("Draggable"),
        c.Position(Vec2(214, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(50, 12)),
        c.DebugEntity(),
        c.Hoverable(),
        c.Draggable(),
        c.Selectable(),
    )

    # debug: a draggable to drag around (world space)
    world.create_entity(
        c.Name("Draggable"),
        c.Position(Vec2(20, 20)),
        c.Extent(Vec2(50, 12)),
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
        c.Image(img_sweetie),
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
        c.Position(Vec2(2 + 8 * 0, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_hand),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Pencil"),
        c.Button(),
        c.ToolSwitcher(Tool.PENCIL),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 1, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_pencil),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Dropper"),
        c.Button(),
        c.ToolSwitcher(Tool.DROPPER),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 2, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_dropper),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Grid"),
        c.Button(),
        c.ToolSwitcher(Tool.GRID),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 3, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_grid),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Cellref"),
        c.Button(),
        c.ToolSwitcher(Tool.CELLREF),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 4, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_cellref),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Cellref Dropper"),
        c.Button(),
        c.ToolSwitcher(Tool.CELLREF_DROPPER),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 5, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_cellref_dropper),
        c.Hoverable(),
    )
    world.create_entity(
        c.Name("Mystery Egg"),
        c.Button(),
        c.ToolSwitcher(Tool.EGG),
        c.Pressable(),
        c.Position(Vec2(2 + 8 * 6, 2), space=PositionSpace.SCREEN),
        c.Extent(Vec2(8, 8)),
        c.Image(img_egg),
        c.Hoverable(),
    )

    # Register controllers and renderers (flavors of processors)
    for processor_class in [
        # global state and input
        p.CameraContextController,
        p.MouseController,
        # controllers
        # p.PencilToolController,
        # p.DropperToolController,
        # p.GridToolController,
        # p.EggToolController,
        p.DragController,
        p.HoverController,
        p.PressController,
        p.BoxSelectionController,
        p.ImageController,
        p.ToolSwitcherController,
        # p.CanvasExportController,
        p.CameraController,
        p.MotionController,
        # p.WanderingController,
        # p.EggTimerController,
        # p.TinyFriendController,
        # renderers (world)
        p.BackgroundGridRenderer,
        p.PositionMarkerRenderer,
        # p.CanvasRenderer,
        p.SpriteRegionRenderer,
        p.DebugEntityRenderer,
        # renderers (ui)
        p.BoxSelectionRenderer,
        p.ButtonRenderer,
        # p.DropperToolRenderer,
        # p.PencilToolRenderer,
        # p.GridToolRenderer,
        # cleanup
        # p.SelectableDeleteController,
        p.ImageDeleteController,
        p.FinalDeleteController,
    ]:
        world.add_processor(processor_class())

    hal.run(world)
