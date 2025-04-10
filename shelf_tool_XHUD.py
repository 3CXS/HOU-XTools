from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QIcon, QKeyEvent
from PySide2.QtCore import Qt
import pyautogui
import time

if not hasattr(hou.session, "XTools"):
    hou.session.XTools = None  

class XTools(QtWidgets.QWidget):
    def __init__(self):

        super(XTools, self).__init__()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.setMouseTracking(True)

        Bt_1 = (32, 20)
        Bt_2 = (24, 20)
        Bt_3 = (56, 17)
        Icon_1 = (20, 20)
        
        self._drag_active = False
        self._drag_offset = QtCore.QPoint()

        cursor_pos = QtGui.QCursor.pos()
        offset_x, offset_y = 20, -90
        self.move(cursor_pos.x() + offset_x, cursor_pos.y() + offset_y)

        # LAYOUT
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        self.show()

        # LEFT BAR
        leftbar = QtWidgets.QVBoxLayout()
        leftbar.setSpacing(0)
        layout.addLayout(leftbar)

        # SELECT ONLY BUTTONS
        sub = QtWidgets.QVBoxLayout()
        sub.setSpacing(0)
        leftbar.addLayout(sub)

        self.spacer = QtWidgets.QLabel("", self)
        self.spacer.setFixedHeight(20)
        self.spacer.setFixedWidth(20)
        sub.addWidget(self.spacer)

        self.grow_btn = QtWidgets.QPushButton("")
        self.grow_btn.setFixedSize(20, 20)
        self.grow_btn.setIconSize(QtCore.QSize(16, 16))
        self.grow_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/add.svg"))
        self.grow_btn.setStyleSheet(self.set_bt_style2())
        self.grow_btn.clicked.connect(lambda: self.grow_selection())
        sub.addWidget(self.grow_btn)

        self.shrink_btn = QtWidgets.QPushButton("")
        self.shrink_btn.setFixedSize(20, 20)
        self.shrink_btn.setIconSize(QtCore.QSize(16, 16))
        self.shrink_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/remove.svg"))
        self.shrink_btn.setStyleSheet(self.set_bt_style2())
        self.shrink_btn.clicked.connect(lambda: self.shrink_selection())
        sub.addWidget(self.shrink_btn)

        # EDIT ONLY BUTTONS

        self.spacer = QtWidgets.QLabel("", self)
        self.spacer.setFixedHeight(70)
        self.spacer.setFixedWidth(20)
        sub.addWidget(self.spacer)

        self.tweak_btn = QtWidgets.QPushButton("TW")
        self.tweak_btn.setFixedSize(20, Bt_1[1])
        self.tweak_btn.setStyleSheet(self.set_bt_style2())
        self.tweak_btn.setCheckable(True)
        self.tweak_btn.clicked.connect(self.send_tweak_shortcut)
        sub.addWidget(self.tweak_btn)

        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(False)

        self.slide_btn = QtWidgets.QPushButton("S")
        self.slide_btn.setFixedSize(20, Bt_1[1])
        self.slide_btn.setStyleSheet(self.set_bt_style2())
        self.slide_btn.setCheckable(True)
        self.slide_btn.clicked.connect(self.send_slide_shortcut)
        button_group.addButton(self.slide_btn, 0)
        sub.addWidget(self.slide_btn)
        
        self.peak_btn = QtWidgets.QPushButton("P")
        self.peak_btn.setFixedSize(20, Bt_1[1])
        self.peak_btn.setStyleSheet(self.set_bt_style2())
        self.peak_btn.setCheckable(True)
        self.peak_btn.clicked.connect(self.send_peak_shortcut)
        button_group.addButton(self.peak_btn, 1)
        sub.addWidget(self.peak_btn)

        leftbar.addStretch(1)

        self.select_only_buttons = [self.grow_btn, self.shrink_btn]
        #self.update_select_mode_buttons()
        self.edit_only_buttons = [self.tweak_btn, self.slide_btn, self.peak_btn]
        #self.update_edit_mode_buttons()

        # MAIN LAYOUT
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(main_layout)

        # HEADER
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(0)
        main_layout.addLayout(header)

        # DRAG AREA 
        self.drag_area = QtWidgets.QLabel("X-TOOLS", self)
        self.drag_area.setFixedHeight(16)
        self.drag_area.setFixedWidth(50)
        self.drag_area.setStyleSheet("background-color: rgba(70, 70, 70, 255); color: white; font-size: 10px; padding: 1px; border-radius: 4px;")
        header.addWidget(self.drag_area)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        header.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 20)
        btn.setIcon(QIcon(hou.ui.createQtIcon("VIEW_wireframe.svg")))
        btn.setIconSize(QtCore.QSize(17, 17)) 
        btn.setStyleSheet("QPushButton { background-color: none; border: none}")
        btn.clicked.connect(lambda: self.shading_mode(hou.glShadingType.Wire, hou.glShadingType.WireGhost))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 20)
        btn.setIcon(QIcon(hou.ui.createQtIcon("VIEW_flat_wireframe.svg")))
        btn.setIconSize(QtCore.QSize(16, 16)) 
        btn.setStyleSheet("QPushButton { background-color: none; border: none}")   
        btn.clicked.connect(lambda: self.shading_mode(hou.glShadingType.Flat, hou.glShadingType.FlatWire))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 20)
        btn.setIcon(QIcon(hou.ui.createQtIcon("VIEW_matcap_wireframe.svg")))
        btn.setIconSize(QtCore.QSize(16, 16)) 
        btn.setStyleSheet("QPushButton { background-color: none; border: none}")
        btn.clicked.connect(lambda: self.shading_mode(hou.glShadingType.MatCap, hou.glShadingType.MatCapWire))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("SMH")
        btn.setFixedSize(24, 16)
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shading_mode(hou.glShadingType.Smooth, hou.glShadingType.SmoothWire))
        sub.addWidget(btn)

        sub.insertSpacing(0, 10)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 16)
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/ghost_enabled.svg"))
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setStyleSheet("QPushButton { background-color: none; border: none}")
        btn.clicked.connect(self.toggle_ghosting_templated)
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 16)
        btn.setIcon(QIcon(hou.ui.createQtIcon("VIEW_wireframe_bbox.svg")))
        btn.setIconSize(QtCore.QSize(16, 16)) 
        btn.setStyleSheet("QPushButton { background-color: none; border: none}")
        btn.clicked.connect(self.shading_templated)
        sub.addWidget(btn)

        content_group = QtWidgets.QGroupBox()
        content_group.setStyleSheet("""QGroupBox {border: none; background-color: rgba(50, 50, 50, 00);  border-radius: 5px;}""")
        content = QtWidgets.QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        # TOP /////////////////////////////////////////////////////////////

        # 1 ROW ////////        
        top_group = QtWidgets.QGroupBox()
        top_group.setStyleSheet("""QGroupBox {border: none; background-color: rgba(50, 50, 50, 0);  border-radius: 5px;}""")

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(4)
        top.setContentsMargins(0, 4, 0, 4)
        
        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        top.addLayout(sub)

        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(True)

        self.point_select_btn = QtWidgets.QPushButton("")
        self.point_select_btn.setFixedSize(Bt_2[0], Bt_2[1])
        self.point_select_btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        self.point_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/vertex_select.svg"))
        self.point_select_btn.setStyleSheet(self.set_bt_style(mode=1))
        self.point_select_btn.setCheckable(True)
        self.point_select_btn.clicked.connect(lambda: self.set_component_mode(self.point_select_btn, hou.geometryType.Points))
        button_group.addButton(self.point_select_btn, 0)
        sub.addWidget(self.point_select_btn)
        
        self.edge_select_btn = QtWidgets.QPushButton("")
        self.edge_select_btn.setFixedSize(Bt_2[0], Bt_2[1])
        self.edge_select_btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        self.edge_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/edge_select.svg"))
        self.edge_select_btn.setStyleSheet(self.set_bt_style(mode=3))
        self.edge_select_btn.setCheckable(True)
        self.edge_select_btn.clicked.connect(lambda: self.set_component_mode(self.edge_select_btn, hou.geometryType.Edges))
        button_group.addButton(self.edge_select_btn, 1)
        sub.addWidget(self.edge_select_btn)
        
        self.prim_select_btn = QtWidgets.QPushButton("")
        self.prim_select_btn.setFixedSize(Bt_2[0], Bt_2[1])
        self.prim_select_btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        self.prim_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/face_select.svg"))
        self.prim_select_btn.setStyleSheet(self.set_bt_style(mode=2))
        self.prim_select_btn.setCheckable(True)
        self.prim_select_btn.clicked.connect(lambda: self.set_component_mode(self.prim_select_btn, hou.geometryType.Primitives))
        button_group.addButton(self.prim_select_btn, 2)
        sub.addWidget(self.prim_select_btn)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        top.addLayout(sub)
        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(True)

        self.box_select_btn = QtWidgets.QPushButton("")
        self.box_select_btn.setFixedSize(20, 20)
        self.box_select_btn.setIconSize(QtCore.QSize(16, 16)) 
        self.box_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/boxSelect.svg"))
        self.box_select_btn.setStyleSheet(self.set_bt_style(mode=1))
        self.box_select_btn.setCheckable(True)
        self.box_select_btn.clicked.connect(lambda: self.set_pick_mode(self.box_select_btn, hou.pickStyle.Box))
        button_group.addButton(self.box_select_btn, 0)
        sub.addWidget(self.box_select_btn)

        self.lasso_select_btn = QtWidgets.QPushButton("")
        self.lasso_select_btn.setFixedSize(20, 20)
        self.lasso_select_btn.setIconSize(QtCore.QSize(16, 16)) 
        self.lasso_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/lassoSelect.svg"))
        self.lasso_select_btn.setStyleSheet(self.set_bt_style(mode=3))
        self.lasso_select_btn.setCheckable(True)
        self.lasso_select_btn.clicked.connect(lambda: self.set_pick_mode(self.lasso_select_btn, hou.pickStyle.Lasso))
        button_group.addButton(self.lasso_select_btn, 1)
        sub.addWidget(self.lasso_select_btn)

        self.laser_select_btn = QtWidgets.QPushButton("")
        self.laser_select_btn.setFixedSize(20, 20)
        self.laser_select_btn.setIconSize(QtCore.QSize(20, 20)) 
        self.laser_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/laserSelect.svg"))
        self.laser_select_btn.setStyleSheet(self.set_bt_style(mode=3))
        self.laser_select_btn.setCheckable(True)
        self.laser_select_btn.clicked.connect(lambda: self.set_pick_mode(self.laser_select_btn, hou.pickStyle.Laser))
        button_group.addButton(self.laser_select_btn, 3)
        sub.addWidget(self.laser_select_btn)

        self.brush_select_btn = QtWidgets.QPushButton("")
        self.brush_select_btn.setFixedSize(20, 20)
        self.brush_select_btn.setIconSize(QtCore.QSize(16, 16)) 
        self.brush_select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/brushSelect.svg"))
        self.brush_select_btn.setStyleSheet(self.set_bt_style(mode=2))
        self.brush_select_btn.setCheckable(True)
        self.brush_select_btn.clicked.connect(lambda: self.set_pick_mode(self.brush_select_btn, hou.pickStyle.Brush))
        button_group.addButton(self.brush_select_btn, 2)
        sub.addWidget(self.brush_select_btn)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        top.addLayout(sub)

        select_vis_btn = QtWidgets.QPushButton("BG")
        select_vis_btn.setFixedSize(20, 20)
        select_vis_btn.setStyleSheet(self.set_bt_style2())
        select_vis_btn.clicked.connect(self.cycle_viewport_bg)
        sub.addWidget(select_vis_btn)

        top_group.setLayout(top)
        content.addWidget(top_group)

        # 2 ROW ////////
        top_group = QtWidgets.QGroupBox()
        top_group.setStyleSheet("""QGroupBox {border: none; background-color: rgba(50, 50, 50, 0);  border-radius: 5px;}""")
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(4)
        top.setContentsMargins(0, 0, 0, 4)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        top.addLayout(sub)

        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(True)

        self.select_btn = QtWidgets.QPushButton("")
        self.select_btn.setFixedSize(Bt_2[0], Bt_2[1])
        self.select_btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        self.select_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/restrict_select_off.svg"))
        self.select_btn.setStyleSheet(self.set_bt_style(mode=1))
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self.activate_select_tool)
        button_group.addButton(self.select_btn, 0)
        sub.addWidget(self.select_btn)
        self.toggle_select_menu()

        self.edit_btn = QtWidgets.QPushButton("EDIT")
        self.edit_btn.setFixedSize(Bt_1[0], Bt_1[1])
        self.edit_btn.setStyleSheet(self.set_bt_style(mode=2))
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(self.edit_tool)
        button_group.addButton(self.edit_btn, 1)
        sub.addWidget(self.edit_btn)
        self.toggle_edit_menu()

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        top.addLayout(sub)

        select_vis_btn = QtWidgets.QPushButton("")
        select_vis_btn.setFixedSize(20, 20)
        select_vis_btn.setIconSize(QtCore.QSize(16, 16))
        select_vis_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/hide_off.svg"))
        select_vis_btn.setCheckable(True)      
        select_vis_btn.setStyleSheet(self.set_bt_style2())
        select_vis_btn.clicked.connect(lambda: self.select_vis(select_vis_btn))
        sub.addWidget(select_vis_btn)

        select_grp_btn = QtWidgets.QPushButton("")
        select_grp_btn.setFixedSize(20, 20)
        select_grp_btn.setIconSize(QtCore.QSize(16, 16))
        select_grp_btn.setIcon(QIcon(hou.ui.createQtIcon("TOOLS_select_facegroups.svg")))
        select_grp_btn.setCheckable(True)
        select_grp_btn.setStyleSheet(self.set_bt_style2())
        select_grp_btn.clicked.connect(lambda: self.select_grp(select_grp_btn))
        sub.addWidget(select_grp_btn)

        mode_btn = QtWidgets.QPushButton("M")
        mode_btn.setFixedSize(Bt_2[0], Bt_2[1])
        mode_btn.setStyleSheet(self.set_bt_style())
        mode_btn.clicked.connect(self.toggle_selection_mode)
        top.addWidget(mode_btn)

        geo_btn = QtWidgets.QPushButton("GEO")
        geo_btn.setFixedSize(Bt_2[0], Bt_2[1])
        geo_btn.setStyleSheet(self.set_bt_style(color="black"))
        geo_btn.clicked.connect(self.create_geo)
        top.addWidget(geo_btn)

        top.addStretch(1)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setIcon(QIcon(hou.ui.createQtIcon("BUTTONS_materials_unassigned.svg")))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(XTools.home_view)
        top.addWidget(btn)

        top_group.setLayout(top)
        content.addWidget(top_group)   

        # MID /////////////////////////////////////////////////////////////
        mid_group = QtWidgets.QGroupBox()
        mid_group.setStyleSheet("""QGroupBox 
                                    {border: none; 
                                     background-color: rgba(100, 100, 100, 100); 
                                     border-radius: 4px;}""")
        mid = QtWidgets.QHBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(4, 8, 4, 8)
        mid_group.setLayout(mid)
        content.addWidget(mid_group)

        # 1 COL ////////
        col = QtWidgets.QVBoxLayout()

        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)
        
        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/LoopCut.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_edgeloop"))
        sub.addWidget(btn)
      
        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/PolySplit.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_polysplit::2.0"))
        sub.addWidget(btn)

        col.insertSpacing(5, 8)

        btn = QtWidgets.QPushButton("EXTR")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_polyextrude::2.0"))
        col.addWidget(btn)
        
        btn = QtWidgets.QPushButton("BEVL")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(color="rgb(0, 180, 250)"))
        btn.clicked.connect(lambda: self.shelftool("sop_polybevel::3.0"))
        col.addWidget(btn)

        col.insertSpacing(5, 8)

        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/con_trackto.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_pointweld"))
        sub.addWidget(btn)
        
        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/snap_midpoint.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_edgecollapse"))
        sub.addWidget(btn)   

        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/object_data.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_polyfill"))
        sub.addWidget(btn)

        self.fuse_btn = QtWidgets.QPushButton("FS")
        self.fuse_btn.setFixedSize(24, 20)
        self.fuse_btn.setStyleSheet(self.set_bt_style())
        self.fuse_btn.clicked.connect(lambda: self.create_sop("fuse::2.0", "fuse"))
        sub.addWidget(self.fuse_btn)
        
        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/no_curve.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_polybridge"))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/stylus_pressure.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_polydraw"))
        sub.addWidget(btn)        

        mid.addLayout(col)

        # 2 COL ////////
        col = QtWidgets.QVBoxLayout()  
        
        btn = QtWidgets.QPushButton("SUBD")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("subdivide", "subdivide"))
        col.addWidget(btn)

        btn = QtWidgets.QPushButton("BOOL")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("boolean::2.0", "bool"))
        col.addWidget(btn)
        
        btn = QtWidgets.QPushButton("SOLID")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("labs::thicken::1.0", "solidify"))
        col.addWidget(btn)
        col.addStretch(1)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("R")
        btn.setFixedSize(16, Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(mode=1))
        btn.clicked.connect(lambda: self.create_sop("reverse", "reverse"))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("S")
        btn.setFixedSize(16, Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(mode=2))
        btn.clicked.connect(lambda: self.create_sop("smooth", "smooth"))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("MIR")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("mirror", "Mirror"))
        col.addWidget(btn)

        btn = QtWidgets.QPushButton("SYM")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("cxs::sym", "SYM"))
        col.addWidget(btn)

        mid.addLayout(col)

        # 3 COL ////////
        col = QtWidgets.QVBoxLayout()

        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 20)
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/mesh_plane.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(self.grid)
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 20)
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/mesh_circle.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("circle", "circle", prim=1))
        sub.addWidget(btn)

        sub = QtWidgets.QHBoxLayout()
        col.addLayout(sub)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, Bt_1[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/file_3d.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("box", "box"))
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, Bt_1[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/mesh_cylinder.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("tube", "tube"))
        sub.addWidget(btn)
                                 
        btn = QtWidgets.QPushButton("CRV")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("curve::2.0", "CRV"))
        col.addWidget(btn) 
        
        col.addStretch(1)
        
        btn = QtWidgets.QPushButton("LATCE")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_lattice"))
        col.addWidget(btn)
        
        btn = QtWidgets.QPushButton("RMSH")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(self.quadremesh)
        col.addWidget(btn)

        btn = QtWidgets.QPushButton("TOPO")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.shelftool("sop_topobuild"))
        col.addWidget(btn)
        mid.addLayout(col)

        # 4 COL ////////
        col = QtWidgets.QVBoxLayout()

        btn_grp= QtWidgets.QPushButton("GRP")
        btn_grp.setFixedSize(Bt_2[0], Bt_2[1])
        btn_grp.setStyleSheet(self.set_bt_style())
        btn_grp.clicked.connect(lambda: self.create_sop("groupcreate", "GRP"))
        col.addWidget(btn_grp)
        
        btn_grp_bnd = QtWidgets.QPushButton("BND")
        btn_grp_bnd.setFixedSize(Bt_2[0], Bt_2[1])
        btn_grp_bnd.setStyleSheet(self.set_bt_style())
        btn_grp_bnd.clicked.connect(lambda: self.group_bnd())
        col.addWidget(btn_grp_bnd)

        btn_grp_angle = QtWidgets.QPushButton("ANG")
        btn_grp_angle.setFixedSize(Bt_2[0], Bt_2[1])
        btn_grp_angle.setStyleSheet(self.set_bt_style())
        btn_grp_angle.clicked.connect(self.group_angle)
        col.addWidget(btn_grp_angle)

        col.addStretch(1)
        
        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(Bt_2[0], Bt_2[1])
        btn.setIconSize(QtCore.QSize(Icon_1[0], Icon_1[1]))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/empty_data.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("null", "null"))
        col.addWidget(btn)

        btn_mrg = QtWidgets.QPushButton("MRG")
        btn_mrg.setFixedSize(Bt_2[0], Bt_2[1])
        btn_mrg.setStyleSheet(self.set_bt_style())
        btn_mrg.clicked.connect(lambda: self.create_sop("merge", "merge"))
        col.addWidget(btn_mrg) 

        self.menu_btn = QtWidgets.QPushButton(">>")
        self.menu_btn.setFixedSize(Bt_2[0], Bt_2[1])
        self.menu_btn.setCheckable(True)
        #self.menu_btn.setChecked(False)
        self.menu_btn.setStyleSheet(self.set_bt_style())
        self.menu_btn.clicked.connect(self.toggle_menu)
        #self.menu_btn.installEventFilter(self)
        col.addWidget(self.menu_btn)

        mid.addLayout(col)

        # LOW /////////////////////////////////////////////////////////////
        low_group = QtWidgets.QGroupBox()
        low_group.setStyleSheet("""QGroupBox {border: none; background-color: rgba(50, 50, 50, 0)}""")
        low = QtWidgets.QHBoxLayout()
        low.setSpacing(4)        
        low.setContentsMargins(0, 4, 0, 0)

        low_group.setLayout(low)
        content.addWidget(low_group)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        low.addLayout(sub)

        btn = QtWidgets.QPushButton("COG")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(mode=1))
        btn.clicked.connect(self.cog)
        sub.addWidget(btn)
        
        btn = QtWidgets.QPushButton("CNT")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(mode=3))
        btn.clicked.connect(self.center)
        sub.addWidget(btn)
        
        btn = QtWidgets.QPushButton("FLR")
        btn.setFixedSize(Bt_1[0], Bt_1[1])
        btn.setStyleSheet(self.set_bt_style(mode=2))
        btn.clicked.connect(self.floor)
        sub.addWidget(btn)
              
        content_group.setLayout(content)

        main_layout.addWidget(content_group)

        # FOOTER /////////////////////////////////////////////////////////////
        footer_group = QtWidgets.QGroupBox()
        footer_group.setStyleSheet("""QGroupBox {border: none; background-color: rgba(50, 50, 50, 0);  border-radius: 5px;}""")
        footer = QtWidgets.QHBoxLayout()
        footer.setSpacing(0)        
        footer.setContentsMargins(0, 4, 0, 0)

        footer_group.setLayout(footer)
        main_layout.addWidget(footer_group)

        sub = QtWidgets.QHBoxLayout()
        sub.setSpacing(0)
        footer.addLayout(sub)
        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(True)

        self.multi_snap_btn = QtWidgets.QPushButton("")
        self.multi_snap_btn.setFixedSize(20, 16)
        self.multi_snap_btn.setIconSize(QtCore.QSize(16, 16)) 
        self.multi_snap_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/snap_off.svg"))
        self.multi_snap_btn.setCheckable(True)
        self.multi_snap_btn.clicked.connect(lambda: self.set_snap_mode(self.multi_snap_btn, hou.snappingMode.Multi))
        button_group.addButton(self.multi_snap_btn, 0)
        sub.addWidget(self.multi_snap_btn)

        self.grid_snap_btn = QtWidgets.QPushButton("")
        self.grid_snap_btn.setFixedSize(20, 16)
        self.grid_snap_btn.setIconSize(QtCore.QSize(17, 17)) 
        self.grid_snap_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/grid.svg"))
        self.grid_snap_btn.setCheckable(True)
        self.grid_snap_btn.clicked.connect(lambda: self.set_snap_mode(self.grid_snap_btn, hou.snappingMode.Grid))
        button_group.addButton(self.grid_snap_btn, 1)
        sub.addWidget(self.grid_snap_btn)

        self.prim_snap_btn = QtWidgets.QPushButton("")
        self.prim_snap_btn.setFixedSize(20, 16)
        self.prim_snap_btn.setIconSize(QtCore.QSize(17, 17)) 
        self.prim_snap_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/snap_face.svg"))
        self.prim_snap_btn.setCheckable(True)
        self.prim_snap_btn.clicked.connect(lambda: self.set_snap_mode(self.prim_snap_btn, hou.snappingMode.Prim))
        button_group.addButton(self.prim_snap_btn, 2)
        sub.addWidget(self.prim_snap_btn)

        self.point_snap_btn = QtWidgets.QPushButton("")
        self.point_snap_btn.setFixedSize(20, 16)
        self.point_snap_btn.setIconSize(QtCore.QSize(17, 17)) 
        self.point_snap_btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/snap_face_center.svg"))
        self.point_snap_btn.setCheckable(True)
        self.point_snap_btn.clicked.connect(lambda: self.set_snap_mode(self.point_snap_btn, hou.snappingMode.Point))
        button_group.addButton(self.point_snap_btn, 3)
        sub.addWidget(self.point_snap_btn)

        self.current_active_button = None

        self.update_snap_style()

        sub.insertSpacing(5, 20)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 16)
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/Measure.svg"))
        btn.setStyleSheet(self.set_bt_style())
        btn.clicked.connect(lambda: self.create_sop("admin_measure_dist", "Measure"))
        sub.addWidget(btn)
        sub.addStretch(1)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(20, 16)
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/pause.svg"))
        btn.setCheckable(True)
        btn.setStyleSheet(self.set_bt_style2())
        btn.clicked.connect(self.toggle_update_mode)
        sub.addWidget(btn)

        btn = QtWidgets.QPushButton("")
        btn.setFixedSize(16, 16)
        btn.setIconSize(QtCore.QSize(16, 16))
        #btn.setIcon(QIcon(hou.ui.createQtIcon("BUTTONS_cook.svg")))
        btn.setIcon(QIcon("M:/ARTWORK/02_DEV/XTOOLS/icons/file_refresh.svg"))
        btn.setStyleSheet(self.set_bt_style2())
        btn.clicked.connect(self.trigger_update)
        sub.addWidget(btn)

        main_layout.addStretch(1)

        # RIGHT MENU /////////////////////////////////////////////////////////////
        menu_nodes = QtWidgets.QVBoxLayout()
        menu_nodes.setSpacing(0)
        menu_nodes.setContentsMargins(4, 4, 4, 4)
        layout.addLayout(menu_nodes)

        right = QtWidgets.QHBoxLayout()
        right.setSpacing(4)
        menu_nodes.addLayout(right)

        # 1 COL ////////
        col = QtWidgets.QVBoxLayout()
        right.addLayout(col)

        col.insertSpacing(10, 51)

        sub = QtWidgets.QVBoxLayout()
        sub.setSpacing(0)
        col.addLayout(sub)

        self.btn_01 = QtWidgets.QPushButton("FILE")
        self.btn_01.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_01.setStyleSheet(self.set_bt_style3(color="yellow"))
        self.btn_01.clicked.connect(lambda: self.create_sop("file", "file"))
        sub.addWidget(self.btn_01)

        self.btn_02 = QtWidgets.QPushButton("FCACHE")
        self.btn_02.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_02.setStyleSheet(self.set_bt_style3(color="yellow"))
        self.btn_02.clicked.connect(lambda: self.create_sop("filecache::2.0", "filecache"))
        sub.addWidget(self.btn_02)

        sub.insertSpacing(10, 10)

        self.btn_03 = QtWidgets.QPushButton("SPHERE")
        self.btn_03.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_03.setStyleSheet(self.set_bt_style3())
        self.btn_03.clicked.connect(lambda: self.create_sop("sphere", "sphere"))
        sub.addWidget(self.btn_03)
        
        self.btn_04 = QtWidgets.QPushButton("TETRA")
        self.btn_04.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_04.setStyleSheet(self.set_bt_style3())
        self.btn_04.clicked.connect(lambda: self.create_sop("platonic", "platonic", prim=1))
        sub.addWidget(self.btn_04)

        self.btn_05 = QtWidgets.QPushButton("ADD")
        self.btn_05.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_05.setStyleSheet(self.set_bt_style3())
        self.btn_05.clicked.connect(lambda: self.create_sop("add", "add"))
        sub.addWidget(self.btn_05)

        self.btn_06 = QtWidgets.QPushButton("REDUCE")
        self.btn_06.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_06.setStyleSheet(self.set_bt_style3(color="rgb(200, 20, 20)"))
        self.btn_06.clicked.connect(lambda: self.create_sop("polyreduce::2.0", "polyreduce"))
        sub.addWidget(self.btn_06)

        self.btn_07 = QtWidgets.QPushButton("CONVERT")
        self.btn_07.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_07.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_07.clicked.connect(lambda: self.create_sop("convert", "convert"))
        sub.addWidget(self.btn_07)

        self.btn_10 = QtWidgets.QPushButton("SWEEP")
        self.btn_10.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_10.setStyleSheet(self.set_bt_style3(color="rgb(250, 0, 250)"))
        self.btn_10.clicked.connect(lambda: self.create_sop("sweep::2.0", "sweep"))
        sub.addWidget(self.btn_10)

        self.btn_11 = QtWidgets.QPushButton("SKIN")
        self.btn_11.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_11.setStyleSheet(self.set_bt_style3(color="rgb(250, 0, 250)"))
        self.btn_11.clicked.connect(lambda: self.create_sop("skin", "skin"))
        sub.addWidget(self.btn_11)

        self.btn_12 = QtWidgets.QPushButton("CPY-PNT")
        self.btn_12.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_12.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_12.clicked.connect(lambda: self.create_sop("(copytopoints::2.0", "copytopoints"))
        sub.addWidget(self.btn_12)

        self.btn_13 = QtWidgets.QPushButton("CPY-CRV")
        self.btn_13.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_13.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_13.clicked.connect(lambda: self.create_sop("copytocurves", "copytocurves"))
        sub.addWidget(self.btn_13)

        self.btn_14 = QtWidgets.QPushButton("KNIFE")
        self.btn_14.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_14.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_14.clicked.connect(lambda: self.create_sop("knife", "knife"))
        sub.addWidget(self.btn_14)

        self.btn_15 = QtWidgets.QPushButton("BEND")
        self.btn_15.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_15.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_15.clicked.connect(lambda: self.create_sop("bend", "bend"))
        sub.addWidget(self.btn_15)

        col.addStretch(1)

        # 2 COL ////////
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(0)
        right.addLayout(col)

        sub = QtWidgets.QVBoxLayout()
        sub.setSpacing(0)
        col.addLayout(sub)

        sub.insertSpacing(10, 17)

        self.btn_20 = QtWidgets.QPushButton("VDB")
        self.btn_20.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_20.setStyleSheet(self.set_bt_style3(color="rgb(200, 20, 20)"))
        self.btn_20.clicked.connect(lambda: self.create_sop("vdbfrompolygons", "vdbfrompolygons"))
        sub.addWidget(self.btn_20)

        self.btn_21 = QtWidgets.QPushButton("RESHAPE")
        self.btn_21.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_21.setStyleSheet(self.set_bt_style3(color="rgb(200, 20, 20)"))
        self.btn_21.clicked.connect(lambda: self.create_sop("vdbreshapesdf", "vdbreshapesdf"))
        sub.addWidget(self.btn_21)

        self.btn_22 = QtWidgets.QPushButton("VDBSMTH")
        self.btn_22.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_22.setStyleSheet(self.set_bt_style3(color="rgb(200, 20, 20)"))
        self.btn_22.clicked.connect(lambda: self.create_sop("vdbsmoothsdf", "vdbsmoothsdf"))
        sub.addWidget(self.btn_22)

        self.btn_23 = QtWidgets.QPushButton("VDBCONV")
        self.btn_23.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_23.setStyleSheet(self.set_bt_style3(color="rgb(200, 20, 20)"))
        self.btn_23.clicked.connect(lambda: self.create_sop("convertvdb", "convertvdb"))
        sub.addWidget(self.btn_23)

        sub.insertSpacing(10, 10)

        self.btn_24 = QtWidgets.QPushButton("VOP")
        self.btn_24.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_24.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_24.clicked.connect(lambda: self.create_sop("attribvop", "vop"))
        sub.addWidget(self.btn_24)

        self.btn_25 = QtWidgets.QPushButton("ATTCREATE")
        self.btn_25.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_25.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_25.clicked.connect(lambda: self.create_sop("attribcreate::2.0", "attribcreate"))
        sub.addWidget(self.btn_25)

        self.btn_26 = QtWidgets.QPushButton("POLYFRAME")
        self.btn_26.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_26.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_26.clicked.connect(lambda: self.create_sop("polyframe", "polyframe"))
        sub.addWidget(self.btn_26)

        self.btn_27 = QtWidgets.QPushButton("NORMAL")
        self.btn_27.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_27.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_27.clicked.connect(lambda: self.create_sop("normal", "normal"))
        sub.addWidget(self.btn_27)

        self.btn_28 = QtWidgets.QPushButton("SORT")
        self.btn_28.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_28.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_28.clicked.connect(lambda: self.create_sop("labs::sort::1.0", "sort"))
        sub.addWidget(self.btn_28)

        self.btn_29 = QtWidgets.QPushButton("ATT DEL")
        self.btn_29.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_29.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_29.clicked.connect(lambda: self.create_sop("attribdelete", "attribdelete"))
        sub.addWidget(self.btn_29)

        self.btn_30 = QtWidgets.QPushButton("GRP DEL")
        self.btn_30.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_30.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_30.clicked.connect(lambda: self.create_sop("groupdelete", "groupdelete"))
        sub.addWidget(self.btn_30)

        self.btn_31 = QtWidgets.QPushButton("COLOR")
        self.btn_31.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_31.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 150)"))
        self.btn_31.clicked.connect(lambda: self.create_sop("color", "color"))
        sub.addWidget(self.btn_31)

        self.btn_32 = QtWidgets.QPushButton("AMBOCC")
        self.btn_32.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_32.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 150)"))
        self.btn_32.clicked.connect(lambda: self.create_sop("maskbyfeature", "maskbyfeature"))
        sub.addWidget(self.btn_32)

        self.btn_33 = QtWidgets.QPushButton("CURVATURE")
        self.btn_33.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_33.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 150)"))
        self.btn_33.clicked.connect(lambda: self.create_sop("labs::measure_curvature::3.0", "curvature"))
        sub.addWidget(self.btn_33)

        self.btn_34 = QtWidgets.QPushButton("ADJUST")
        self.btn_34.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_34.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 150)"))
        self.btn_34.clicked.connect(lambda: self.create_sop("attribadjustcolor", "attribadjustcolor"))
        sub.addWidget(self.btn_34)

        self.btn_35 = QtWidgets.QPushButton("BORDER DIST")
        self.btn_35.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_35.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 150)"))
        self.btn_35.clicked.connect(lambda: self.create_sop("labs::distance_from_border", "distance_from_border"))
        sub.addWidget(self.btn_35)

        col.addStretch(1)

        # 3 COL ////////
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(0)
        right.addLayout(col)

        sub = QtWidgets.QVBoxLayout()
        sub.setSpacing(0)
        col.addLayout(sub)

        sub.insertSpacing(10, 34)

        self.btn_42 = QtWidgets.QPushButton("DECALS")
        self.btn_42.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_42.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 250)"))
        self.btn_42.clicked.connect(lambda: self.create_sop("labs::decal_projector", "decal_projector"))
        sub.addWidget(self.btn_42)

        self.btn_43 = QtWidgets.QPushButton("BOXCUTTER")
        self.btn_43.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_43.setStyleSheet(self.set_bt_style3(color="rgb(0, 250, 250)"))
        self.btn_43.clicked.connect(lambda: self.create_sop("labs::boxcutter::1.0", "boxcutter"))
        sub.addWidget(self.btn_43)

        self.btn_44 = QtWidgets.QPushButton("VIS_MAT")
        self.btn_44.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_44.setStyleSheet(self.set_bt_style3())
        self.btn_44.clicked.connect(lambda: self.create_sop("cc_mat", "cc_mat"))
        sub.addWidget(self.btn_44)

        sub.insertSpacing(10, 10)

        self.btn_45 = QtWidgets.QPushButton("UV UNFOLD")
        self.btn_45.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_45.setStyleSheet(self.set_bt_style3())
        self.btn_45.clicked.connect(lambda: self.create_sop("uvflatten::3.0", "uvflatten"))
        sub.addWidget(self.btn_45)

        self.btn_46 = QtWidgets.QPushButton("UV LAYOUT")
        self.btn_46.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_46.setStyleSheet(self.set_bt_style3())
        self.btn_46.clicked.connect(lambda: self.create_sop("uvlayout::3.0", "uvlayout"))
        sub.addWidget(self.btn_46)

        self.btn_47 = QtWidgets.QPushButton("UV VIS")
        self.btn_47.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_47.setStyleSheet(self.set_bt_style3())
        self.btn_47.clicked.connect(lambda: self.create_sop("labs::visualize_uvs::1.1", "visualize_uvs"))
        sub.addWidget(self.btn_47)

        self.btn_48 = QtWidgets.QPushButton("AUTO UV")
        self.btn_48.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_48.setStyleSheet(self.set_bt_style3())
        self.btn_48.clicked.connect(lambda: self.create_sop("labs::autouv", "autouv"))
        sub.addWidget(self.btn_48)

        self.btn_49 = QtWidgets.QPushButton("UV UNDIST")
        self.btn_49.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_49.setStyleSheet(self.set_bt_style3())
        self.btn_49.clicked.connect(lambda: self.create_sop("labs::remove_uv_distortion::1.0", "remove_uv_distortion"))
        sub.addWidget(self.btn_49)

        self.btn_50 = QtWidgets.QPushButton("BAKE MAP")
        self.btn_50.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_50.setStyleSheet(self.set_bt_style3(color="blue"))
        self.btn_50.clicked.connect(lambda: self.create_sop("labs::maps_baker::5.0", "maps_baker"))
        sub.addWidget(self.btn_50)

        self.btn_52 = QtWidgets.QPushButton("GRP PAINT")
        self.btn_52.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_52.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_52.clicked.connect(lambda: self.create_sop("grouppaint", "grouppaint"))
        sub.addWidget(self.btn_52)

        self.btn_53 = QtWidgets.QPushButton("PROMOTE")
        self.btn_53.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_53.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_53.clicked.connect(lambda: self.create_sop("grouppromote", "grouppromote"))
        sub.addWidget(self.btn_53)

        self.btn_54 = QtWidgets.QPushButton("COMBINE")
        self.btn_54.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_54.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_54.clicked.connect(lambda: self.create_sop("groupcombine", "groupcombine"))
        sub.addWidget(self.btn_54)

        self.btn_55 = QtWidgets.QPushButton("EXPR")
        self.btn_55.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_55.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_55.clicked.connect(lambda: self.create_sop("groupexpression", "groupexpression"))
        sub.addWidget(self.btn_55)

        self.btn_56 = QtWidgets.QPushButton("ATT")
        self.btn_56.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_56.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_56.clicked.connect(lambda: self.create_sop("labs::group_by_attribute::1.0", "group_by_attribute"))
        sub.addWidget(self.btn_56)

        self.btn_57 = QtWidgets.QPushButton("RANGE")
        self.btn_57.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_57.setStyleSheet(self.set_bt_style3(color="rgb(250, 200, 100)"))
        self.btn_57.clicked.connect(lambda: self.create_sop("grouprange", "grouprange"))
        sub.addWidget(self.btn_57)

        col.addStretch(1)

        # 4 COL ////////
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(0)
        right.addLayout(col)

        sub = QtWidgets.QVBoxLayout()
        sub.setSpacing(0)
        col.addLayout(sub)

        sub.insertSpacing(10, 17)

        self.btn_61 = QtWidgets.QPushButton("DISPLACE")
        self.btn_61.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_61.setStyleSheet(self.set_bt_style3())
        self.btn_61.clicked.connect(lambda: self.create_sop("labs::triplanar_displace", "triplanar_displace"))
        sub.addWidget(self.btn_61)

        self.btn_62 = QtWidgets.QPushButton("BORDER")
        self.btn_62.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_62.setStyleSheet(self.set_bt_style3())
        self.btn_62.clicked.connect(lambda: self.create_sop("labs::extract_borders", "extract_borders"))
        sub.addWidget(self.btn_62)

        self.btn_60 = QtWidgets.QPushButton("RND EDG")
        self.btn_60.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_60.setStyleSheet(self.set_bt_style3())
        self.btn_60.clicked.connect(lambda: self.create_sop("circlefromedges", "circlefromedges"))
        sub.addWidget(self.btn_60)

        self.btn_65 = QtWidgets.QPushButton("SHARPEN")
        self.btn_65.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_65.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_65.clicked.connect(lambda: self.create_sop("labs::mesh_sharpen", "mesh_sharpen"))
        sub.addWidget(self.btn_65)

        sub.insertSpacing(10, 10)

        self.btn_08 = QtWidgets.QPushButton("PEAK")
        self.btn_08.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_08.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_08.clicked.connect(lambda: self.create_sop("peak", "peak"))
        sub.addWidget(self.btn_08)

        self.btn_09 = QtWidgets.QPushButton("RAY")
        self.btn_09.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_09.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_09.clicked.connect(lambda: self.create_sop("ray", "ray"))
        sub.addWidget(self.btn_09)

        self.btn_63 = QtWidgets.QPushButton("RESAMPLE")
        self.btn_63.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_63.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_63.clicked.connect(lambda: self.create_sop("resample", "resample"))
        sub.addWidget(self.btn_63)

        self.btn_64 = QtWidgets.QPushButton("CRV-SMPL")
        self.btn_64.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_64.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_64.clicked.connect(lambda: self.create_sop("labs::curve_resample_by_density::1.0", "curve_resample"))
        sub.addWidget(self.btn_64)

        self.btn_66 = QtWidgets.QPushButton("DIVIDE")
        self.btn_66.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_66.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_66.clicked.connect(lambda: self.create_sop("divide", "divide"))
        sub.addWidget(self.btn_66)

        self.btn_67 = QtWidgets.QPushButton("FLAT EDG")
        self.btn_67.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_67.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_67.clicked.connect(lambda: self.create_sop("labs::dissolve_flat_edges::1.0", "dis_flat_edges"))
        sub.addWidget(self.btn_67)

        self.btn_68 = QtWidgets.QPushButton("SMALL PRTS")
        self.btn_68.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_68.setStyleSheet(self.set_bt_style3(color="white"))
        self.btn_68.clicked.connect(lambda: self.create_sop("labs::delete_small_parts", "delete_small_parts"))
        sub.addWidget(self.btn_68)

        self.btn_69 = QtWidgets.QPushButton("MATERIAL")
        self.btn_69.setFixedSize(Bt_3[0], Bt_3[1])
        self.btn_69.setStyleSheet(self.set_bt_style3())
        self.btn_69.clicked.connect(lambda: self.create_sop("labs::quickmaterial::2.2", "quickmaterial"))
        sub.addWidget(self.btn_69)

        col.addStretch(1)

        right.addStretch(1)

        self.menu_nodes = [self.btn_01, self.btn_02, self.btn_03, self.btn_04, self.btn_05, self.btn_06, self.btn_07,self.btn_08,
                          self.btn_09, self.btn_10, self.btn_11, self.btn_12, self.btn_13, self.btn_14, self.btn_15,
                          self.btn_20, self.btn_21, self.btn_22, self.btn_23, self.btn_24, self.btn_25, self.btn_26, self.btn_27,
                          self.btn_28, self.btn_29, self.btn_30, self.btn_31, self.btn_32, self.btn_33, self.btn_34, self.btn_35,
                          self.btn_42, self.btn_43, self.btn_44, self.btn_45, self.btn_46, self.btn_47, self.btn_48,
                          self.btn_49, self.btn_50,               self.btn_52, self.btn_53, self.btn_54, self.btn_55, self.btn_56, self.btn_57,
                          self.btn_60, self.btn_61, self.btn_62, self.btn_63, self.btn_64, self.btn_65, self.btn_66, self.btn_67, self.btn_68,
                          self.btn_69,
                         ] 
                         
        self.toggle_menu()

        #self.close_threshold = 80

        #self.setMouseTracking(True)

        #self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(self.check_mouse_distance)
        #self.timer.timeout.connect(self.update_select_mode_button(self.select_btn))
        #self.timer.timeout.connect(self.update_edit_mode_button(self.edit_btn))
        #self.timer.timeout.connect(self.update_edit_mode_buttons)
        #self.timer.timeout.connect(self.update_select_mode_buttons)
        #self.timer.start(500) 

        layout.addStretch(1)

        self.setLayout(layout)

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # FUNCTIONS /////////////////////////////////

    # UI ////////////////////////////////////////

    def toggle_menu(self):
        showmenu = self.menu_btn.isChecked()
        for btn in self.menu_nodes:
            btn.setVisible(showmenu)

    def eventFilter(self, obj, event):
        if obj == self.menu_btn:
            if event.type() == QtCore.QEvent.Enter:
                if not self.menu_btn.isChecked(): 
                    #self.menu_btn.setChecked(True)
                    for btn in self.menu_nodes:
                        btn.setVisible(True)
        return super().eventFilter(obj, event)

    def check_mouse_distance(self):
        if not self.menu_btn.isChecked() and any(btn.isVisible() for btn in self.menu_nodes):
            cursor_pos = QtGui.QCursor.pos()
            menu_rect = self.menu_btn.mapToGlobal(self.menu_btn.rect().topLeft())
            submenu_rect = self.calculate_menu_rect()

            closest_x = min(max(cursor_pos.x(), submenu_rect.left()), submenu_rect.right())
            closest_y = min(max(cursor_pos.y(), submenu_rect.top()), submenu_rect.bottom())
            distance = ((cursor_pos.x() - closest_x) ** 2 + (cursor_pos.y() - closest_y) ** 2) ** 0.5

            if distance > self.close_threshold:
                for btn in self.menu_nodes:
                    btn.setVisible(False)

    def calculate_menu_rect(self):
        if not self.menu_nodes:
            return QtCore.QRect()

        global_rects = [btn.geometry() for btn in self.menu_nodes if btn.isVisible()]
        if not global_rects:
            return QtCore.QRect()

        global_rects = [btn.mapToGlobal(QtCore.QPoint(0, 0)) for btn in self.menu_nodes if btn.isVisible()]
        min_x = min(pt.x() for pt in global_rects)
        min_y = min(pt.y() for pt in global_rects)
        max_x = max(pt.x() + self.menu_nodes[0].width() for pt in global_rects)
        max_y = max(pt.y() + self.menu_nodes[0].height() for pt in global_rects)

        return QtCore.QRect(min_x, min_y, max_x - min_x, max_y - min_y)

    def set_bt_style(self, mode=0, color="white"):
        border_radius = "border-radius: 4px;"

        if mode == 1:
            border_radius = "border-top-left-radius: 4px; border-bottom-left-radius: 4px;"
        elif mode == 2:
            border_radius = "border-top-right-radius: 4px; border-bottom-right-radius: 4px;"
        elif mode == 3:
            border_radius = "border-radius: 0px;"

        return f"""
            QPushButton {{
                background-color: rgba(100, 100, 100, 200);
                color: {color}; 
                border: 1px solid rgba(50, 50, 50, 150);
                {border_radius};
                padding: 0px;
                font-size: 10px;
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 50, 200, 100);
            }}
            QPushButton:checked {{
                background-color: rgba(0, 50, 200, 100);
            }}
        """

    def set_bt_style2 (self):
        return f"""
            QPushButton {{
                background-color: rgba(100, 100, 100, 5);
                color: white; 
                font-size: 10px;
                border: 1px solid rgba(100, 100, 100, 0);
                border-radius: 4px;
                padding: 0px;
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 100, 200, 100);
            }}
            QPushButton:checked {{
                background-color: rgba(0, 100, 200, 100);
            }}
        """
    def set_bt_style3 (self, color="white"):
        return f"""
            QPushButton {{
                background-color: rgba(130, 130, 130, 150);
                color: {color}; 
                font-size: 10px;
                border: 1px solid rgba(50, 50, 50, 150);
                border-radius: 6px;
                padding: 0px;
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 100, 200, 150);
            }}
            QPushButton:checked {{
                background-color: rgba(0, 100, 200, 150);
            }}
            QPushButton:hover {{
                background-color: rgba(50, 100, 150, 150);
            }}
        """
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.drag_area.underMouse():
            self._drag_active = True
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            new_position = event.globalPos() - self._drag_offset
            self.move(new_position)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = False

    def closeEvent(self, event):
        hou.session.XTools = None
        #event.accept()


    # HOUDINI ////////////////////////////////////////

    # MODE ////////

    def toggle_selection_mode(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return      
        current_mode = scene_viewer.selectionMode()
        if current_mode == hou.selectionMode.Object:
            new_mode = hou.selectionMode.Geometry
        else:
            new_mode = hou.selectionMode.Object  
        scene_viewer.setSelectionMode(new_mode)

    def toggle_update_mode(self):
        desktop = hou.ui.curDesktop()
        scene_viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        if scene_viewer:
            current_mode = hou.updateModeSetting()
            auto_mode = hou.updateMode.AutoUpdate
            manual_mode = hou.updateMode.Manual

            if current_mode == auto_mode:
                hou.updateMode.Manual
                hou.setUpdateMode(hou.updateMode.Manual)
            else:
                hou.updateMode.AutoUpdate
                hou.setUpdateMode(hou.updateMode.AutoUpdate)

    def trigger_update(self):
        desktop = hou.ui.curDesktop()
        scene_viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        if scene_viewer:
            hou.ui.triggerUpdate()

    # SELECTION ////////

    def is_select_mode(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            active_tool = scene_viewer.currentState()
            return active_tool in ["select"]
        return False

    def update_select_mode_buttons(self):
        select_active = self.is_select_mode()
        for btn in self.select_only_buttons:
            btn.setVisible(select_active)

    def update_select_mode_button(self, button):
        if self.is_select_mode():
            button.setChecked(True)
        else:
            button.setChecked(False)

    def toggle_select_menu(self):
        select_active = self.select_btn.isChecked()
        for btn in self.select_only_buttons:
            btn.setVisible(select_active)


    def activate_select_tool(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            scene_viewer.setCurrentState("select")
            #self.update_edit_mode_buttons()
            select_active = self.select_btn.isChecked()
            for btn in self.select_only_buttons:
                btn.setVisible(select_active)
            for btn in self.edit_only_buttons:
                btn.setVisible(False)

    def set_pick_mode(self, button, mode):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        scene_viewer.setPickStyle(mode)

    def set_component_mode(self, button, mode):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        scene_viewer.setPickGeometryType(mode)

    def grow_selection(self, uv_connectivity=False):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        geo_selection = scene_viewer.currentGeometrySelection()
        if not geo_selection:
            return
        geo_selection.growSelection()

    def shrink_selection(self, uv_connectivity=False):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        geo_selection = scene_viewer.currentGeometrySelection()
        if not geo_selection:
            return
        geo_selection.shrinkSelection()

    def select_vis(self, button):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        current_mode = scene_viewer.isPickingVisibleGeometry()

        if button.isChecked():
            scene_viewer.setPickingVisibleGeometry(True)
        else:
            scene_viewer.setPickingVisibleGeometry(False)

    def select_grp(self, button):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        current_mode = scene_viewer.isGroupPicking()

        if button.isChecked():
            scene_viewer.setGroupPicking(True)
        else:
            scene_viewer.setGroupPicking(False)

    # EDIT ////////

    def is_edit_mode(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            active_tool = scene_viewer.currentState()
            return active_tool in ["edit", "view"]
        return False

    def toggle_edit_menu(self):
        edit_active = self.edit_btn.isChecked()
        for btn in self.edit_only_buttons:
            btn.setVisible(edit_active)

    def edit_tool(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        current_path = network_editor.pwd()

        if current_path.childTypeCategory() == hou.objNodeTypeCategory():
            selected_nodes = hou.selectedNodes()
            if not selected_nodes:
                return
            for node in selected_nodes:
                if node.childTypeCategory() == hou.sopNodeTypeCategory():
                    network_editor.setPwd(node)
                    break
        scene_viewer.setCurrentState("edit")

        edit_active = self.edit_btn.isChecked()
        for btn in self.edit_only_buttons:
            btn.setVisible(edit_active)
        for btn in self.select_only_buttons:
            btn.setVisible(False)

    def send_tweak_shortcut(self):
        desktop = hou.ui.curDesktop()
        scene_viewer_panes = [pane for pane in desktop.paneTabs() if isinstance(pane, hou.SceneViewer)]
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

        if not scene_viewer.currentState()=="edit":
            return
        if scene_viewer_panes:
            scene_viewer = scene_viewer_panes[0]
            scene_viewer.setIsCurrentTab()
            pyautogui.click(x=800, y=40)
            pyautogui.hotkey('shift', 't')

    def send_slide_shortcut(self, button):
        desktop = hou.ui.curDesktop()
        scene_viewer_panes = [pane for pane in desktop.paneTabs() if isinstance(pane, hou.SceneViewer)]

        sender = self.sender()
        buttons = [self.slide_btn, self.peak_btn]

        if sender.isChecked():  
            for btn in buttons:
                if btn != sender:
                    btn.setChecked(False)
        if scene_viewer_panes:
            scene_viewer = scene_viewer_panes[0]
            scene_viewer.setIsCurrentTab()
            pyautogui.click(x=800, y=40)
            pyautogui.hotkey('l')

    def send_peak_shortcut(self):
        desktop = hou.ui.curDesktop()
        scene_viewer_panes = [pane for pane in desktop.paneTabs() if isinstance(pane, hou.SceneViewer)]

        sender = self.sender()
        buttons = [self.slide_btn, self.peak_btn]

        if sender.isChecked():  
            for btn in buttons:
                if btn != sender:
                    btn.setChecked(False)

        if scene_viewer_panes:
            scene_viewer = scene_viewer_panes[0]
            scene_viewer.setIsCurrentTab()
            pyautogui.click(x=800, y=40)
            pyautogui.hotkey('h')


    # SNAPPING ////////

    def set_snap_mode(self, button, mode):
        """Toggles the Houdini snap mode based on button state."""
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not scene_viewer:
            return

        current_mode = scene_viewer.snappingMode()
        
        if button.isChecked():
            if current_mode == mode:
                scene_viewer.setSnappingMode(hou.snappingMode.Off)
                self.current_active_button = None
            else:
                scene_viewer.setSnappingMode(mode)
                self.current_active_button = button
        else:
            scene_viewer.setSnappingMode(hou.snappingMode.Off)

        self.update_snap_style()

    def update_snap_style(self):

        def get_style(active, mode=0):
            border_radius = "border-radius: 4px;"

            if mode == 1:
                border_radius = "border-top-left-radius: 4px; border-bottom-left-radius: 4px;"
            elif mode == 2:
                border_radius = "border-top-right-radius: 4px; border-bottom-right-radius: 4px;"
            elif mode == 3:
                border_radius = "border-radius: 0px;"
            if active:
                return f"""
                    QPushButton {{
                        background-color: rgba(200, 0, 0, 150);
                        color: white; 
                        border: 1px solid rgba(50, 50, 50, 150);
                        {border_radius}
                        padding: 8px;
                    }}
                """
            else:
                return f"""
                    QPushButton {{
                        background-color: rgba(100, 100, 100, 200); 
                        color: white; 
                        border: 1px solid rgba(50, 50, 50, 150);
                        {border_radius}
                        padding: 8px;
                    }}
                """

        self.multi_snap_btn.setStyleSheet(get_style(self.current_active_button == self.multi_snap_btn, mode=1))
        self.grid_snap_btn.setStyleSheet(get_style(self.current_active_button == self.grid_snap_btn, mode=3))
        self.prim_snap_btn.setStyleSheet(get_style(self.current_active_button == self.prim_snap_btn, mode=3))
        self.point_snap_btn.setStyleSheet(get_style(self.current_active_button == self.point_snap_btn, mode=2))


    # VIEWPORT ////////
    
    def get_viewport(self):
        return hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

    def home_view(self):
        viewport = XTools.get_viewport(self)
        if viewport:
            viewport.curViewport().home()

    def shading_mode(self, mode1, mode2):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            viewport = scene_viewer.curViewport()
            settings = viewport.settings() 
            network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            if network_editor:
                current_context = network_editor.pwd()
                if current_context.childTypeCategory() == hou.objNodeTypeCategory():
                    mode = 0
                elif current_context.childTypeCategory() == hou.sopNodeTypeCategory():
                    mode = 1
                else:
                    mode = 0
            else:
                mode = 0

            if mode == 0:
                current_mode = settings.displaySet(hou.displaySetType.SceneObject).shadedMode()
            else:
                current_mode = settings.displaySet(hou.displaySetType.DisplayModel).shadedMode()

            if current_mode == mode1:
                new_mode = mode2
            else:
                new_mode = mode1

            if mode == 0:
                settings.displaySet(hou.displaySetType.SceneObject).setShadedMode(new_mode)
            else:
                settings.displaySet(hou.displaySetType.DisplayModel).setShadedMode(new_mode)

    def shading_templated(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            viewport = scene_viewer.curViewport()
            settings = viewport.settings() 

            current_mode = settings.displaySet(hou.displaySetType.TemplateModel).shadedMode()

        shading_modes = [
            hou.glShadingType.Wire,
            hou.glShadingType.FlatWire,
            hou.glShadingType.Flat,
        ]
        current_mode = settings.displaySet(hou.displaySetType.TemplateModel).shadedMode()
        next_mode = shading_modes[(shading_modes.index(current_mode) + 1) % len(shading_modes)]
        settings.displaySet(hou.displaySetType.TemplateModel).setShadedMode(next_mode)

    def toggle_ghosting_templated(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            viewport = scene_viewer.curViewport()
            settings = viewport.settings()    
            current_state = settings.displaySet(hou.displaySetType.TemplateModel).isUsingGhostedLook()
    
            new_state = not current_state
            settings.displaySet(hou.displaySetType.TemplateModel).useGhostedLook(new_state)

    def toggle_ortho_grid(self): 
        # does not work..
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            viewport = scene_viewer.curViewport()
            settings = viewport.settings()
            grid_visible = settings.displayOrthoGrid()
            settings.setDisplayOrthoGrid(not grid_visible)

    def cycle_viewport_bg(self):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        
        if scene_viewer:
            viewport = scene_viewer.curViewport()
            settings = viewport.settings()

            current_scheme = settings.colorScheme()

            schemes = [
                hou.viewportColorScheme.Dark,
                hou.viewportColorScheme.Grey,
                hou.viewportColorScheme.Light,
                #hou.viewportColorScheme.DarkGrey
            ]

            next_index = (schemes.index(current_scheme) + 1) % len(schemes)
            new_scheme = schemes[next_index]

            settings.setColorScheme(new_scheme)


    # SHELFTOOLS ////////

    def shelftool(self, tool):
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if scene_viewer:
            scene_viewer.runShelfTool(tool) 

    # OBJ ////////

    def create_geo(*args):
        obj_context = hou.node("/obj")
        geo_node = obj_context.createNode("geo", "GEO") 
        geo_node.moveToGoodPosition()
        geo_node.setSelected(True, clear_all_selected=True) 
        return geo_node

    # SOP ////////

    def create_sop(self, sop, label, prim=0):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        node = None

        if selected_nodes:
            parent = selected_nodes[0].parent()
            node = parent.createNode(sop, label)
            if prim == 0:
                node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            node.setPosition((pos_x, pos_y - 0.8))
        else:
            node = parent.createNode(sop, label)
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                node.setPosition((pos_x, pos_y - 0.8))

        node.setDisplayFlag(True)
        node.setRenderFlag(True)

        hou.clearAllSelected()  
        node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(node) 

    def quadremesh(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            node = parent.createNode("labs::exoside_quadremesher::1.0", "RMSH")
            node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            node.setPosition((pos_x, pos_y - 0.8))
        else:
            node = parent.createNode("labs::exoside_quadremesher::1.0", "RMSH")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                node.setPosition((pos_x, pos_y - 0.8))

        # Set custom parameters
        node.parm("bAutoCook").set(False)

        node.setSelected(True, clear_all_selected=True)

        node.setDisplayFlag(True)
        node.setRenderFlag(True)

        hou.clearAllSelected()  
        node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(node) 

    def group_bnd(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            node = parent.createNode("groupcreate", "GRP")
            node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            node.setPosition((pos_x, pos_y - 0.8))
        else:
            node = parent.createNode("groupcreate", "GRP")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                node.setPosition((pos_x, pos_y - 0.8))

        # Set custom parameters
        node.setParms({"grouptype": "edge"})
        node.parm("groupname").set("bnd")
        node.parm("groupbase").set(False)
        node.parm("groupedges").set(True)
        node.parm("unshared").set(True)
        node.setSelected(True, clear_all_selected=True)

        node.setDisplayFlag(True)
        node.setRenderFlag(True)

        hou.clearAllSelected()  
        node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(node) 

    def group_angle(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            node = parent.createNode("groupcreate", "GRP")
            node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            node.setPosition((pos_x, pos_y - 0.8))
        else:
            node = parent.createNode("groupcreate", "GRP")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                node.setPosition((pos_x, pos_y - 0.8))

        # Set custom parameters
        node.setParms({"grouptype": "edge"})
        node.parm("groupname").set("bev")
        node.parm("groupbase").set(False)
        node.parm("groupedges").set(True)
        node.parm("dominedgeangle").set(True)
        node.setSelected(True, clear_all_selected=True)

        node.setDisplayFlag(True)
        node.setRenderFlag(True)

        hou.clearAllSelected()  
        node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(node) 

    def grid(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            node = parent.createNode("grid", "grid")
            #node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            node.setPosition((pos_x, pos_y - 0.8))
        else:
            node = parent.createNode("grid", "grid")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                node.setPosition((pos_x, pos_y - 0.8))
    
        # Set custom parameters
        node.parm("orient").set(0)
        node.parm("rows").set(2)
        node.parm("cols").set(2)

        node.setDisplayFlag(True)
        node.setRenderFlag(True)

        hou.clearAllSelected()  
        node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(node)        

    # TRANFORM
    def cog(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        transform_node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            transform_node = parent.createNode("xform", "COG")
            transform_node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            transform_node.setPosition((pos_x, pos_y - 0.8))
        else:
            transform_node = parent.createNode("xform", "COG")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                transform_node.setPosition((pos_x, pos_y - 0.8))
    
        # Set custom parameters
        transform_node.parmTuple("t").set((0.0, 0.0, 0.0))
        transform_node.parmTuple("r").set((0.0, 0.0, 0.0))
        transform_node.parm("scale").set(1)
        
        transform_node.parm("px").setExpression("$CEX")
        transform_node.parm("py").setExpression("$CEY")
        transform_node.parm("pz").setExpression("$CEZ")
    
        transform_node.setDisplayFlag(True)
        transform_node.setRenderFlag(True)

        hou.clearAllSelected()  
        transform_node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(transform_node)

    def center(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return
            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        transform_node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            transform_node = parent.createNode("xform", "CENTER")
            transform_node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            transform_node.setPosition((pos_x, pos_y - 0.8))
        else:
            transform_node = parent.createNode("xform", "CENTER")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                transform_node.setPosition((pos_x, pos_y - 0.8))
    
        # Set custom parameters
        transform_node.parmTuple("t").set((0.0, 0.0, 0.0))
        transform_node.parmTuple("r").set((0.0, 0.0, 0.0))
        transform_node.parm("scale").set(1)
        
        transform_node.parm("px").setExpression("$CEX")
        transform_node.parm("py").setExpression("$CEY")
        transform_node.parm("pz").setExpression("$CEZ")
        
        transform_node.parm("prexform_tx").setExpression("-$CEX")
        transform_node.parm("prexform_ty").setExpression("-$CEY")
        transform_node.parm("prexform_tz").setExpression("-$CEZ")
    
        transform_node.setDisplayFlag(True)
        transform_node.setRenderFlag(True)

        hou.clearAllSelected()  
        transform_node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(transform_node)
        
    def floor(self):
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if not network_editor:
            hou.ui.displayMessage("No active Network Editor found.", title="Error")
            return            
        parent = network_editor.pwd()
        selected_nodes = hou.selectedNodes()
        transform_node = None
    
        if selected_nodes:
            parent = selected_nodes[0].parent()
            transform_node = parent.createNode("xform", "FLOOR")
            transform_node.setInput(0, selected_nodes[0])
            pos_x, pos_y = selected_nodes[0].position()
            transform_node.setPosition((pos_x, pos_y - 0.8))
        else:
            transform_node = parent.createNode("xform", "FLOOR")
            last_node = parent.children()[-2] if len(parent.children()) > 1 else None
            if last_node:
                pos_x, pos_y = last_node.position()
                transform_node.setPosition((pos_x, pos_y - 0.8))
    
        # Set custom parameters
        transform_node.parmTuple("t").set((0.0, 0.0, 0.0))
        transform_node.parmTuple("r").set((0.0, 0.0, 0.0))
        transform_node.parm("scale").set(1)
        
        transform_node.parm("px").setExpression("$CEX")
        transform_node.parm("py").setExpression("$CEY")
        transform_node.parm("pz").setExpression("$ZMIN")
        
        transform_node.parm("prexform_tx").setExpression("-$CEX")
        transform_node.parm("prexform_ty").setExpression("-$CEY")
        transform_node.parm("prexform_tz").setExpression("-$ZMIN")
    
        transform_node.setDisplayFlag(True)
        transform_node.setRenderFlag(True)

        hou.clearAllSelected()  
        transform_node.setSelected(True, clear_all_selected=False)

        network_editor.setCurrentNode(transform_node)

#/////////////////////////////////////////////////////////////////////////////////////////


def toggle_hud():
    if hou.session.XTools is None:
        hou.session.XTools = XTools()  # Open HUD
    else:
        hou.session.XTools.close()  # Close existing HUD
        hou.session.XTools = None  # Reset session variable

toggle_hud()

# END OF SCRIPT ///////////////////////////////////////////////////////////////CXS/2025//
