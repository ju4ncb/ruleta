import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QGraphicsTextItem, QGraphicsObject, QLabel
from PyQt6.QtGui import QColor, QFont, QPainterPath, QPen, QBrush
from PyQt6.QtCore import QPoint, QPointF, QPropertyAnimation, QEasingCurve, Qt, QParallelAnimationGroup, QRectF, QAbstractAnimation
import numpy as np
        
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
COLOR_BACKGROUND = "#57625F"
COLOR_BACKGROUND_2 = "#45524D"
COLOR_BUTTON = "#6C8E85"
COLOR_DEFAULT_TEXT = "#FFFFFF"
BG_WIDTH = 600
BG_HEIGHT = 600
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SPINNING_WHEEL_RADIUS = 180

class AnimatedPathItem(QGraphicsObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = QPainterPath()
        self.pen = QPen()
        self.brush = QBrush()

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPath(self.path)

    def boundingRect(self):
        return self.path.boundingRect()

class spinning_wheel(QGraphicsView):
    def __init__(self, root : QWidget):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, 364, 384))
        self.setParent(root)
        self.setStyleSheet(f"border: 0px;background-color{COLOR_BACKGROUND}")
        self.setGeometry(BG_WIDTH//6, 50, BG_WIDTH*4//6, BG_HEIGHT*4//6)   
        self.scene.addEllipse(0, 0, SPINNING_WHEEL_RADIUS*2, SPINNING_WHEEL_RADIUS*2, QPen(QColor(COLOR_WHITE), 4), QColor(COLOR_BACKGROUND))     
        default_text = self.scene.addText('Add something!', QFont('Arial', 18))
        default_text.setDefaultTextColor(QColor(COLOR_WHITE))
        default_text.setPos(SPINNING_WHEEL_RADIUS - default_text.boundingRect().width() / 2, SPINNING_WHEEL_RADIUS - default_text.boundingRect().height() / 2)
        
        #Create pointer
        path = QPainterPath()
        path.moveTo(SPINNING_WHEEL_RADIUS, 20)
        path.lineTo(SPINNING_WHEEL_RADIUS - 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 0 - 15)
        path.lineTo(SPINNING_WHEEL_RADIUS + 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 20)
        
        #Winner point
        self.winner_angle = 270
        self.winner = None
        self.winner_rotation = 0
        
        self.scene.addPath(path, QPen(QColor(COLOR_WHITE), 4), QColor(COLOR_BACKGROUND_2))
        self.setScene(self.scene)
        
        #Data structures
        self.layers = []
        self.colors = ['#62124A', '#3E1262', '#121462', '#123B62', '#125062', '#126253', '#12622B', '#246212', '#4A6212', '#625D12', '#624612', '#622D12', '#62121F']
        self.winner_colors = ['#FF00B3', '#8E03FF', '#0006FF', '#0083FF', '#00C6FF', '#00FFCF', '#00FF50', '#39FF00', '#B3FF00', '#CACA19', '#FFA600', '#FF5600', '#FF0029']
        self.color_rotation = np.random.randint(0,len(self.colors) - 1)
        
        self.group = QParallelAnimationGroup()
        self.animations = []
                
    def create_default_scene(self, root : QWidget) -> None:
        self.layers = []
        self.color_rotation = np.random.randint(0,len(self.colors) - 1)
        self.scene = QGraphicsScene(parent = root)
        self.scene.setSceneRect(QRectF(0, 0, 364, 384))
        self.scene.addEllipse(0, 0, SPINNING_WHEEL_RADIUS*2, SPINNING_WHEEL_RADIUS*2, QPen(QColor(COLOR_WHITE), 4), QColor(COLOR_BACKGROUND))     
        default_text = self.scene.addText('Add something!', QFont('Arial', 18))
        default_text.setDefaultTextColor(QColor(COLOR_WHITE))
        default_text.setPos(SPINNING_WHEEL_RADIUS - default_text.boundingRect().width() / 2, SPINNING_WHEEL_RADIUS - default_text.boundingRect().height() / 2)
        path = QPainterPath()
        
        #Create pointer
        path.moveTo(SPINNING_WHEEL_RADIUS, 20)
        path.lineTo(SPINNING_WHEEL_RADIUS - 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 0 - 15)
        path.lineTo(SPINNING_WHEEL_RADIUS + 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 20)
        self.scene.addPath(path, QPen(QColor(COLOR_WHITE), 4), QColor(COLOR_BACKGROUND_2))
        self.setScene(self.scene)
        
        #Winner point
        self.winner_angle = 270
        self.winner = None
        self.winner_rotation = 0
        
        self.group = QParallelAnimationGroup()
        self.animations = []
        
    def get_center_point(self) -> QPoint:
        return self.geometry().center()
    
    def highlight_winner(self) -> None:
        theta = 360/len(self.layers)
        right = self.winner_rotation
        left = right + theta
        left = left
        min_angle = (90 - right)%360 + (left - 90)%360
        min_itr = 0
        for i in range(1,len(self.layers)):
            right += theta
            left = right + theta
            angle = (90 - right)%360 + (left - 90)%360
            if min_angle > angle:
                min_itr = i
                min_angle = angle
                
        self.layers[min_itr][4].brush = QColor(self.winner_colors[self.layers[min_itr][2]])
        self.winner = [self.layers[min_itr][4], self.layers[min_itr][2]]
        self.group.finished.disconnect(self.highlight_winner)
    
    def spin(self):
               
        #check if spinning wheel is already running    
        if self.group.state() == QAbstractAnimation.State.Running:
             return
        
        #reset winner color
        if self.winner != None:
            self.winner[0].brush = QColor(self.colors[self.winner[1]])
        
        #check if spinning wheel is empty
        if len(self.layers) == 0:
            return
        
        #get a random angle
        randnum = np.random.randint(0, 360)
        
        #set winner rotation        
        self.winner_rotation += randnum
                
        #set the end value of all animations
        for animation in self.animations:
            animation.setStartValue(animation.targetObject().rotation())
            animation.setEndValue(animation.targetObject().rotation() - (1440 + randnum))
            
        #start to rotate wooooooooooooooooooooooooooooooooooooooooooooooooooooo
        self.group.updateCurrentTime(0)
        self.group.start()
        self.group.finished.connect(self.highlight_winner)
        self.scene.update()
        
    def resize_font(self, font_num : int, text : QGraphicsTextItem, angle : float, text_pos : QPointF, mode : int) -> None:
        
        num_layers = len(self.layers) + 1
        theta = 2*np.pi/num_layers
        
        def text_is_out(corner_points : list, angle : float) -> bool:
            layer_path = QPainterPath()
            layer_path.moveTo(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)
            layer_path.arcTo(0, 0, SPINNING_WHEEL_RADIUS*2, SPINNING_WHEEL_RADIUS*2, (angle)*360/(2*np.pi), 360/num_layers)
            for point in corner_points:
                if not layer_path.contains(point):
                    return True
            return False
    
        def get_corner_points(text : QGraphicsTextItem) -> list:
            rect = text.boundingRect()
            x = text.x()
            y = text.y()
            width = rect.width()
            height = rect.height()
            
            if mode == 1:
                #get radius by pythagoreas theorem
                radius_1 = (abs(x - SPINNING_WHEEL_RADIUS)**2 + abs(y - SPINNING_WHEEL_RADIUS)**2)**(1/2)
                radius_2 = (abs(x - SPINNING_WHEEL_RADIUS)**2 + abs(y + height - SPINNING_WHEEL_RADIUS)**2)**(1/2)
                
                #get starting angles by trigonometry
                start_angle_p1 = 0 - np.arcsin(abs(x - SPINNING_WHEEL_RADIUS)/radius_1)
                start_angle_p2 = 0 - start_angle_p1
                start_angle_p3 = 0 - np.arcsin(abs(x - SPINNING_WHEEL_RADIUS)/radius_2)
                start_angle_p4 = 0 - start_angle_p3
                
                #get 4 points by polar coordinates and vector decomposition
                ay = SPINNING_WHEEL_RADIUS + radius_1 * np.sin(0 - (angle + theta/2 + start_angle_p1))
                ax = SPINNING_WHEEL_RADIUS + radius_1 * np.cos(0 - (angle + theta/2 + start_angle_p1))
                
                by = SPINNING_WHEEL_RADIUS + radius_1 * np.sin(0 - (angle + theta/2 + start_angle_p2))
                bx = SPINNING_WHEEL_RADIUS + radius_1 * np.cos(0 - (angle + theta/2 + start_angle_p2))
                
                cy = SPINNING_WHEEL_RADIUS + radius_2 * np.sin(0 - (angle + theta/2 + start_angle_p3))
                cx = SPINNING_WHEEL_RADIUS + radius_2 * np.cos(0 - (angle + theta/2 + start_angle_p3))
                
                dy = SPINNING_WHEEL_RADIUS + radius_2 * np.sin(0 - (angle + theta/2 + start_angle_p4))
                dx = SPINNING_WHEEL_RADIUS + radius_2 * np.cos(0 - (angle + theta/2 + start_angle_p4))

                return [QPointF(ax, ay), QPointF(bx, by), QPointF(cx, cy), QPointF(dx, dy)]
            else: 
                return [QPointF(x, y), QPointF(x + width, y), QPointF(x, y + height), QPointF(x + width, y + height)]
        
        corner_points = get_corner_points(text)
        
        if mode == 0:
            while text_is_out(corner_points, 0) and font_num >= 8:
                font_num -= 1
                text.setFont(QFont('Arial', font_num))
                text_pos = QPointF(SPINNING_WHEEL_RADIUS - text.boundingRect().width() / 2, SPINNING_WHEEL_RADIUS - text.boundingRect().height() / 2)
                text.setPos(text_pos)
                corner_points = get_corner_points(text)
        else:
            while text_is_out(corner_points, angle) and font_num >= 8:
                font_num -= 1
                text.setFont(QFont('Arial', font_num))
                text_pos = QPointF(SPINNING_WHEEL_RADIUS - text.boundingRect().width() / 2, SPINNING_WHEEL_RADIUS*2/9 - text.boundingRect().height()/2)
                text.setPos(text_pos)
                text.setRotation(0)
                text.setTransformOriginPoint(text.mapFromScene(QPointF(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)))
                text.setRotation(90 + (0 - (angle + theta/2) * 360 / (2*np.pi)))
                corner_points = get_corner_points(text)
    
    def create_multiple_layers(self, text : str) -> None:
        texts = text.split("\n")
        indexes = [i for i, t in enumerate(texts) if t.replace(' ', '') == '']
        for index in indexes:
            texts.pop(index)
        for t in texts:
            self.create_layer(t)        
    
    def create_layer(self, name : str) -> None:  
                
        #check if text is empty
        if len(name) == 0:
            return
        
        #check if spinning wheel is already running    
        if self.group.state() == QAbstractAnimation.State.Running:
            return
        
        #reset winner color
        if self.winner != None:
            self.winner[0].brush = QColor(self.colors[self.winner[1]])
            self.winner_rotation = 0
        
        #some default values
        font_num = 18
        num_layers = len(self.layers) + 1
        original_text = name
        center_point = QPointF(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)
        
        #theta is the angle in polar coordinates in radians
        theta = np.pi*2/num_layers
        angle = 0
        
        #check if all of the colors (in their order) in the colors list has been used
        if self.color_rotation == len(self.colors):
            self.color_rotation = 0
            
        if num_layers == 1:
            pen = QPen()
            pen.setStyle(Qt.PenStyle.NoPen)
            
            #Create the text
            text = self.scene.addText(name, QFont('Arial', font_num))
            text.setDefaultTextColor(QColor(COLOR_WHITE))
            text_pos = QPointF(SPINNING_WHEEL_RADIUS - text.boundingRect().width() / 2, SPINNING_WHEEL_RADIUS - text.boundingRect().height() / 2)
            text.setPos(text_pos)
                
            #Resize the font
            self.resize_font(font_num, text, 0, text.pos(), 0)
            
            #Assign the center point to the animation of the text
            text.setTransformOriginPoint(text.mapFromScene(center_point))
        else:
            pen = QColor(COLOR_WHITE)
            for layer in self.layers: #Update the past graphic items
                #Restore the items to their initial rotations
                layer[3].setRotation(layer[5][1])
                layer[4].setRotation(layer[5][0])
                
                #Create the PainterPath
                path = QPainterPath()
                path.moveTo(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)
                path.arcTo(0, 0, SPINNING_WHEEL_RADIUS*2, SPINNING_WHEEL_RADIUS*2, (angle)*360/(2*np.pi), 360/num_layers)
                
                #Set the PainterPath to the GraphicsPathItem
                layer[4].path = path
                layer[4].pen = pen
                
                #Update the text position
                text_pos = QPointF(SPINNING_WHEEL_RADIUS - layer[3].boundingRect().width()/2, SPINNING_WHEEL_RADIUS*2/9 - layer[3].boundingRect().height()/2)
                layer[3].setPos(text_pos)
                
                #Resize font
                if num_layers % 2 == 1:
                    self.resize_font(font_num, layer[3], angle + theta/2, layer[3].pos(), 1)
                else:
                    self.resize_font(font_num, layer[3], angle, layer[3].pos(), 1)
                
                #Set the animation center point of the text and assign it to the text
                layer[3].setTransformOriginPoint(layer[3].mapFromScene(center_point))
                layer[3].setRotation(90 + (0 - (angle + theta/2) * 360 / (2*np.pi)))
                
                angle += theta
                font_num = 18
                
            #Create the new text
            text = self.scene.addText(name, QFont('Arial', font_num))
            text.setDefaultTextColor(QColor(COLOR_WHITE))
            text_pos = QPointF(SPINNING_WHEEL_RADIUS - text.boundingRect().width()/2, SPINNING_WHEEL_RADIUS*2/9 - text.boundingRect().height()/2)
            text.setPos(text_pos)
            
            #Resize font
            if num_layers % 2 == 1:
                self.resize_font(font_num, text, angle + theta/2, text.pos(), 1)
            else:
                self.resize_font(font_num, text, angle, text.pos(), 1)
        
            #Assign the center point to the animation of the text
            text.setTransformOriginPoint(text.mapFromScene(center_point))
            text.setRotation(90 + (0 - (angle + theta/2) * 360 / (2*np.pi)))
            
        #Create the animation 1 and add it to the animation group
        animation_1 = QPropertyAnimation(text, b"rotation")
        self.animations.append(animation_1)
        animation_1.setDuration(4000)
        animation_1.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation_1.setObjectName(original_text)
        self.group.addAnimation(animation_1)
        
        #Create the ellipse slice
        path = QPainterPath()
        path.moveTo(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)
        path.arcTo(0, 0, SPINNING_WHEEL_RADIUS*2, SPINNING_WHEEL_RADIUS*2, (angle)*360/(2*np.pi), 360/num_layers)
        path.lineTo(np.cos(angle + theta)*SPINNING_WHEEL_RADIUS + SPINNING_WHEEL_RADIUS, np.sin(angle + theta)*SPINNING_WHEEL_RADIUS + SPINNING_WHEEL_RADIUS)
        path.lineTo(SPINNING_WHEEL_RADIUS, SPINNING_WHEEL_RADIUS)
    
        #Add the slice to the scene and transform its origin point
        item = AnimatedPathItem()
        item.pen = pen
        item.brush = QColor(self.colors[self.color_rotation])
        item.path = path
        self.scene.addItem(item)
        
        #Assign center point to the animation of the slice
        item.setTransformOriginPoint(item.mapFromScene(center_point))
        
        #Create the animation 2 and add it to the animation group
        animation_2 = QPropertyAnimation(item, b"rotation")
        self.animations.append(animation_2)
        animation_2.setDuration(4000)
        animation_2.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation_2.setObjectName(original_text + " path")
        self.group.addAnimation(animation_2)
        
        #Save the original states of the items
        initial_rotations = [item.rotation(), text.rotation()]
        
        text.setZValue(1)
        self.layers.append([name, original_text, self.color_rotation, text, item, initial_rotations])
        self.color_rotation += 1
        
        #Create the pointer
        path = QPainterPath()
        path.moveTo(SPINNING_WHEEL_RADIUS, 20)
        path.lineTo(SPINNING_WHEEL_RADIUS - 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 0 - 15)
        path.lineTo(SPINNING_WHEEL_RADIUS + 10, 0 - 20)
        path.lineTo(SPINNING_WHEEL_RADIUS, 20)
        self.scene.addPath(path, QPen(QColor(COLOR_WHITE), 4), QColor(COLOR_BACKGROUND_2))
        self.setScene(self.scene)
        
    def calculate_starting_angle(ang, theta):
        starting_angle = (ang - theta)*360/(2*np.pi)
        if starting_angle > 360:
            starting_angle = starting_angle - 360
           
class window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Spinning wheel")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"border:0px;background-color:{COLOR_BACKGROUND}")

        #Create main layout
        layout = QVBoxLayout(self)

        #Create the spinning wheel
        self.spinning_wheel_widget = QWidget(self)
        self.spinning_wheel_widget.setGeometry(0, 0, BG_WIDTH, SCREEN_HEIGHT)
        roul = spinning_wheel(self.spinning_wheel_widget)
        spinning_wheel_layout = QVBoxLayout(self.spinning_wheel_widget)
        spinning_wheel_layout.addWidget(roul)
        
        #Create spin button
        spin_button = QPushButton("Spin", self.spinning_wheel_widget)
        spin_button.setFont(QFont('Arial', 18))
        spin_button.setGeometry(0, 0, 100, 50)
        spin_button.setStyleSheet(f"border: 0px; color:{COLOR_DEFAULT_TEXT}; background-color:{COLOR_BUTTON};")
        spin_button.move(roul.get_center_point().x() - 50, 500)
        spin_button.pressed.connect(roul.spin)
        
        #Create options panel
        self.options_panel = QWidget(self)
        self.options_panel.setGeometry(BG_WIDTH, 0, SCREEN_WIDTH - BG_WIDTH, SCREEN_HEIGHT)
        self.options_panel.setStyleSheet(f"background-color:{COLOR_BACKGROUND_2}")
        
        #Create note
        add_item_note = QLabel(self.options_panel, text = "Add the items here", font = QFont('Arial', 12))
        add_item_note.move(90, 55)
        add_item_note.setStyleSheet(f"color:{COLOR_WHITE}")
        
        #Create add item text field
        add_item_text_field = QTextEdit(self.options_panel)
        add_item_text_field.setGeometry(10, 90, SCREEN_WIDTH - BG_WIDTH - 20, 340)
        add_item_text_field.setFont(QFont('Arial', 18))
        add_item_text_field.setStyleSheet(f"border: 0px; color:{COLOR_WHITE}; background-color:{COLOR_BUTTON};")
        path = QPainterPath()
        path.moveTo(10, 210 + add_item_text_field.height())
        path.lineTo(10 + add_item_text_field.width(), 210 + add_item_text_field.height())
        
        #Create add item button
        add_item_button = QPushButton("Add item(s)", self.options_panel)
        add_item_button.setFont(QFont('Arial', 18))
        add_item_button.setGeometry(75, 450, 150, 50)
        add_item_button.setStyleSheet(f"border: 0px; color:{COLOR_WHITE}; background-color:{COLOR_BUTTON};")
        add_item_button.pressed.connect(lambda : roul.create_multiple_layers(add_item_text_field.toPlainText()))
        
        #Create clear spinning wheel button
        clear_spinning_wheel_button = QPushButton("Clear wheel", self.options_panel)
        clear_spinning_wheel_button.setFont(QFont('Arial', 18))
        clear_spinning_wheel_button.setGeometry(75, 510, 150, 50)
        clear_spinning_wheel_button.setStyleSheet(f"border: 0px; color:{COLOR_WHITE}; background-color:{COLOR_BUTTON};")
        clear_spinning_wheel_button.pressed.connect(lambda : roul.create_default_scene(self.spinning_wheel_widget))
        
        #Add all widgets to main layout
        layout.addWidget(self.spinning_wheel_widget)
        layout.addWidget(self.options_panel)
        
        self.show()


app = QApplication(sys.argv)

main_window = window()

sys.exit(app.exec())