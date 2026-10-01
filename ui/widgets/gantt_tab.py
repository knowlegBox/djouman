import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics

class GanttWidget(QWidget):
    task_double_clicked = Signal(object)
    item_dates_changed = Signal(object, bool, object, datetime.datetime, datetime.datetime)

    def __init__(self):
        super().__init__()
        self.tasks = []
        # Commencer la vue Gantt 1 jour avant aujourd'hui pour bien voir le jour en cours
        self.start_date = datetime.date.today() - datetime.timedelta(days=1)
        self.days_to_show = 28 # 4 weeks
        
        self.row_height = 40
        self.subtask_row_height = 25
        self.header_height = 50
        self.col_width = 40
        self.left_margin = 200
        
        self.setMinimumSize(self.left_margin + self.days_to_show * self.col_width, 600)
        self.setMouseTracking(True)
        
        self.click_map = [] # List of (QRectF, item, is_subtask, parent_task)
        self.bar_map = [] # List of (QRectF, item, is_subtask, parent_task, start_dt, end_dt)
        
        # Drag state
        self.drag_mode = None # "move", "resize_left", "resize_right"
        self.drag_item = None
        self.drag_is_subtask = False
        self.drag_parent = None
        self.drag_start_pos = None
        self.drag_start_date = None
        self.drag_end_date = None
        self.temp_start_date = None
        self.temp_end_date = None

    def set_tasks(self, tasks):
        self.tasks = tasks
        self.update_geometry()
        self.update()

    def set_start_date(self, date):
        self.start_date = date
        self.update()

    def update_geometry(self):
        total_rows = 0
        for task in self.tasks:
            total_rows += 1
            if getattr(task, 'subtasks', None):
                total_rows += len(task.subtasks)
        
        needed_height = self.header_height + total_rows * self.row_height + 100
        self.setMinimumHeight(max(600, needed_height))

    def get_status_color(self, status):
        colors = {
            'pending': "#86948a",
            'in_progress': "#f39c12",
            'completed': "#4edea3",
            'cancelled': "#e74c3c",
            'blocked': "#e74c3c"
        }
        return colors.get(status, "#86948a")

    def get_item_dates(self, item, is_subtask, parent_task):
        if self.drag_item and self.drag_item.id == item.id and self.drag_is_subtask == is_subtask:
            return self.temp_start_date, self.temp_end_date
            
        start_d = getattr(item, 'start_date', None)
        end_d = getattr(item, 'end_date', None)
        
        if is_subtask and not start_d and parent_task:
            start_d = getattr(parent_task, 'start_date', None)
            end_d = getattr(parent_task, 'end_date', None)
            
        if not start_d:
            start_d = getattr(item, 'created_at', None)
            
        if not end_d and getattr(item, 'duration', 0) and start_d:
            end_d = start_d + datetime.timedelta(minutes=item.duration)
        elif not end_d:
            end_d = start_d
            
        return start_d, end_d

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor("#1a211d")
        text_color = QColor("#bbcabf")
        grid_color = QColor("#3c4a42")
        
        painter.fillRect(self.rect(), bg_color)
        
        painter.setPen(QPen(grid_color, 1))
        painter.drawLine(0, self.header_height, self.width(), self.header_height)
        painter.drawLine(self.left_margin, 0, self.left_margin, self.height())
        
        font = QFont("Inter", 9)
        painter.setFont(font)
        
        for i in range(self.days_to_show):
            current_date = self.start_date + datetime.timedelta(days=i)
            x = self.left_margin + i * self.col_width
            
            if current_date.weekday() >= 5:
                painter.fillRect(x, 0, self.col_width, self.height(), QColor("#242c27"))
                
            painter.setPen(QPen(grid_color, 1))
            painter.drawLine(x, 0, x, self.height())
            
            painter.setPen(QPen(text_color))
            day_str = current_date.strftime("%d\n%b")
            painter.drawText(QRectF(x, 0, self.col_width, self.header_height), Qt.AlignCenter, day_str)
            
            if current_date == datetime.date.today():
                painter.fillRect(x, self.header_height, self.col_width, self.height() - self.header_height, QColor(78, 222, 163, 30))
                painter.setPen(QPen(QColor("#4edea3"), 2))
                painter.drawLine(x, 0, x, self.height())
                painter.drawLine(x + self.col_width, 0, x + self.col_width, self.height())

        y = self.header_height
        self.click_map.clear()
        self.bar_map.clear()
        
        planned_tasks = []
        unplanned_tasks = []
        
        for task in self.tasks:
            if getattr(task, 'start_date', None) or getattr(task, 'created_at', None):
                planned_tasks.append(task)
            else:
                unplanned_tasks.append(task)
                
        for task in planned_tasks:
            self.draw_task_row(painter, task, y, False, None)
            y += self.row_height
            if getattr(task, 'subtasks', None):
                for subtask in task.subtasks:
                    self.draw_task_row(painter, subtask, y, True, task)
                    y += self.subtask_row_height

        if unplanned_tasks:
            y += 20
            painter.setPen(QPen(text_color))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(10, y + 20, "Non planifiées (sans date)")
            painter.drawLine(0, y + 30, self.width(), y + 30)
            y += 40
            font.setBold(False)
            painter.setFont(font)
            
            for task in unplanned_tasks:
                self.draw_task_row(painter, task, y, False, None, True)
                y += self.row_height
                if getattr(task, 'subtasks', None):
                    for subtask in task.subtasks:
                        self.draw_task_row(painter, subtask, y, True, task, True)
                        y += self.subtask_row_height

    def draw_task_row(self, painter, item, y, is_subtask, parent_task, is_unplanned=False):
        text_color = QColor("#bbcabf")
        painter.setPen(QPen(text_color))
        row_h = self.subtask_row_height if is_subtask else self.row_height
        
        title_x = 30 if is_subtask else 10
        title = item.title
        metrics = QFontMetrics(painter.font())
        elided_title = metrics.elidedText(title, Qt.ElideRight, self.left_margin - title_x - 10)
        
        if is_subtask:
            painter.setPen(QPen(QColor("#66756c")))
            
        painter.drawText(QRectF(title_x, y, self.left_margin - title_x - 10, row_h), Qt.AlignVCenter | Qt.AlignLeft, elided_title)
        
        self.click_map.append((QRectF(0, y, self.width(), row_h), item, is_subtask, parent_task))
        
        if not is_unplanned:
            start_d, end_d = self.get_item_dates(item, is_subtask, parent_task)
            
            if start_d:
                s_date = start_d.date() if isinstance(start_d, datetime.datetime) else start_d
                e_date = end_d.date() if isinstance(end_d, datetime.datetime) and end_d else s_date
                
                delta_start = (s_date - self.start_date).days
                delta_end = (e_date - self.start_date).days
                
                if delta_end >= 0 and delta_start < self.days_to_show:
                    x_start = self.left_margin + max(0, delta_start) * self.col_width
                    x_end = self.left_margin + min(self.days_to_show, delta_end + 1) * self.col_width
                    
                    # Store exact bounds even if outside view for dragging calculation
                    exact_x_start = self.left_margin + delta_start * self.col_width
                    exact_x_end = self.left_margin + (delta_end + 1) * self.col_width
                    
                    bar_w = x_end - x_start
                    if bar_w < 5: bar_w = self.col_width
                    
                    status = "completed" if (is_subtask and getattr(item, 'is_completed', False)) else getattr(item, 'status', 'pending')
                    color_hex = self.get_status_color(status)
                    
                    if is_subtask:
                        bar_h = 10
                        bar_y = y + (row_h - bar_h) / 2
                        color = QColor(color_hex)
                        color.setAlpha(150)
                    else:
                        bar_h = 24
                        bar_y = y + (row_h - bar_h) / 2
                        color = QColor(color_hex)
                    
                    bar_rect = QRectF(x_start, bar_y, bar_w, bar_h)
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(bar_rect, 4, 4)
                    
                    self.bar_map.append((QRectF(exact_x_start, bar_y, exact_x_end - exact_x_start, bar_h), item, is_subtask, parent_task, start_d, end_d))
                    
                    if not is_subtask and getattr(item, 'subtasks', None):
                        total = len(item.subtasks)
                        done = sum(1 for st in item.subtasks if st.is_completed)
                        if total > 0 and done > 0:
                            progress_w = bar_w * (done / total)
                            painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
                            painter.drawRoundedRect(QRectF(x_start, bar_y, progress_w, bar_h), 4, 4)

    def get_bar_at_pos(self, pos):
        for rect, item, is_subtask, parent, s_d, e_d in self.bar_map:
            # We use intersected rect for visible part
            visible_rect = rect.intersected(QRectF(self.left_margin, 0, self.width() - self.left_margin, self.height()))
            if visible_rect.contains(pos):
                return rect, item, is_subtask, parent, s_d, e_d
        return None, None, None, None, None, None

    def mouseMoveEvent(self, event):
        pos = event.position()
        
        if self.drag_mode:
            delta_x = pos.x() - self.drag_start_pos.x()
            delta_days = round(delta_x / self.col_width)
            
            if self.drag_mode == "move":
                self.temp_start_date = self.drag_start_date + datetime.timedelta(days=delta_days)
                self.temp_end_date = self.drag_end_date + datetime.timedelta(days=delta_days)
            elif self.drag_mode == "resize_left":
                new_start = self.drag_start_date + datetime.timedelta(days=delta_days)
                if new_start <= self.drag_end_date:
                    self.temp_start_date = new_start
            elif self.drag_mode == "resize_right":
                new_end = self.drag_end_date + datetime.timedelta(days=delta_days)
                if new_end >= self.drag_start_date:
                    self.temp_end_date = new_end
                    
            self.update()
            return
            
        rect, item, is_subtask, parent, s_d, e_d = self.get_bar_at_pos(pos)
        if rect:
            edge_width = 8
            if pos.x() <= rect.left() + edge_width:
                self.setCursor(Qt.SizeHorCursor)
            elif pos.x() >= rect.right() - edge_width:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position()
            rect, item, is_subtask, parent, s_d, e_d = self.get_bar_at_pos(pos)
            if rect and s_d and e_d:
                self.drag_item = item
                self.drag_is_subtask = is_subtask
                self.drag_parent = parent
                self.drag_start_pos = pos
                
                # Make sure they are datetime
                if not isinstance(s_d, datetime.datetime): s_d = datetime.datetime.combine(s_d, datetime.time.min)
                if not isinstance(e_d, datetime.datetime): e_d = datetime.datetime.combine(e_d, datetime.time.min)
                
                self.drag_start_date = s_d
                self.drag_end_date = e_d
                self.temp_start_date = s_d
                self.temp_end_date = e_d
                
                edge_width = 8
                if pos.x() <= rect.left() + edge_width:
                    self.drag_mode = "resize_left"
                elif pos.x() >= rect.right() - edge_width:
                    self.drag_mode = "resize_right"
                else:
                    self.drag_mode = "move"

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_mode:
            if self.temp_start_date != self.drag_start_date or self.temp_end_date != self.drag_end_date:
                self.item_dates_changed.emit(self.drag_item, self.drag_is_subtask, self.drag_parent, self.temp_start_date, self.temp_end_date)
            
            self.drag_mode = None
            self.drag_item = None
            self.update()

    def mouseDoubleClickEvent(self, event):
        pos = event.position()
        for rect, item, is_subtask, parent in self.click_map:
            if rect.contains(pos):
                # Always emit the parent task to edit
                target_task = parent if is_subtask else item
                self.task_double_clicked.emit(target_task)
                break

class GanttTab(QWidget):
    def __init__(self, task_service):
        super().__init__()
        self.task_service = task_service
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(15, 10, 15, 10)
        
        self.prev_btn = QPushButton("◀ Semaine préc.")
        self.today_btn = QPushButton("Aujourd'hui")
        self.next_btn = QPushButton("Semaine suiv. ▶")
        
        self.prev_btn.clicked.connect(self.go_prev)
        self.today_btn.clicked.connect(self.go_today)
        self.next_btn.clicked.connect(self.go_next)
        
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Inter", 12, QFont.Bold))
        
        toolbar.addWidget(self.prev_btn)
        toolbar.addWidget(self.today_btn)
        toolbar.addWidget(self.next_btn)
        toolbar.addSpacing(20)
        toolbar.addWidget(self.date_label)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.gantt_widget = GanttWidget()
        self.gantt_widget.item_dates_changed.connect(self.on_item_dates_changed)
        self.scroll_area.setWidget(self.gantt_widget)
        
        layout.addWidget(self.scroll_area)
        self.update_date_label()
        
    def on_item_dates_changed(self, item, is_subtask, parent, start_dt, end_dt):
        session = self.task_service.db_service.get_session()
        try:
            if is_subtask:
                from models.subtask import SubTask
                st = session.query(SubTask).filter(SubTask.id == item.id).first()
                if st:
                    st.start_date = start_dt
                    st.end_date = end_dt
                    st.duration = int((end_dt - start_dt).total_seconds() / 60)
                session.commit()
                # Update parent bounds
                self.task_service.update_parent_task_dates(parent.id)
            else:
                from models.task import Task
                t = session.query(Task).filter(Task.id == item.id).first()
                if t:
                    t.start_date = start_dt
                    t.end_date = end_dt
                    t.duration = int((end_dt - start_dt).total_seconds() / 60)
                session.commit()
                self.task_service.update_task(t.id)
                
            # Reload tasks from main window
            main_win = self.window()
            if hasattr(main_win, 'filter_tasks'):
                main_win.filter_tasks()
        except Exception as e:
            session.rollback()
            print(f"Erreur update dates gantt: {e}")
        finally:
            session.close()

    def go_prev(self):
        self.gantt_widget.set_start_date(self.gantt_widget.start_date - datetime.timedelta(days=7))
        self.update_date_label()
        
    def go_next(self):
        self.gantt_widget.set_start_date(self.gantt_widget.start_date + datetime.timedelta(days=7))
        self.update_date_label()
        
    def go_today(self):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
        self.gantt_widget.set_start_date(start)
        self.update_date_label()
        
    def update_date_label(self):
        start = self.gantt_widget.start_date
        end = start + datetime.timedelta(days=self.gantt_widget.days_to_show - 1)
        self.date_label.setText(f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}")
        
    def set_tasks(self, tasks):
        self.gantt_widget.set_tasks(tasks)
