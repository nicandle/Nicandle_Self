import sys
import random
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

EXCEL_PATH = "cards.xlsx"
STAGES = ["设计", "开发", "测试"]  # 可根据你的实际阶段调整
EVENTS_PER_STAGE = 5

class ReignsExcelDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("流程评审王权Demo（Excel版）")
        self.resize(600, 350)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.stage_idx = 0
        self.score = 0
        self.cards = []
        self.card_idx = 0
        self.df = pd.read_excel(EXCEL_PATH)
        self.init_intro()

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def init_intro(self):
        self.clear_layout()
        label = QLabel("欢迎来到流程评审王权Excel版！\n每个阶段随机抽取5个事件卡牌，左右滑动做决策。")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        btn = QPushButton("开始游戏")
        btn.clicked.connect(self.next_stage)
        self.layout.addWidget(btn)

    def next_stage(self):
        self.clear_layout()
        if self.stage_idx < len(STAGES):
            stage = STAGES[self.stage_idx]
            label = QLabel(f"当前阶段：{stage}")
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label)
            # 随机抽取5个事件
            stage_cards = self.df[self.df["阶段"] == stage]
            if len(stage_cards) < EVENTS_PER_STAGE:
                QMessageBox.warning(self, "警告", f"阶段 {stage} 事件不足5个，请补充Excel表！")
                self.close()
                return
            self.cards = stage_cards.sample(EVENTS_PER_STAGE).to_dict("records")
            self.card_idx = 0
            btn = QPushButton("进入事件卡牌")
            btn.clicked.connect(self.next_card)
            self.layout.addWidget(btn)
        else:
            self.review_stage()

    def next_card(self):
        self.clear_layout()
        if self.card_idx < len(self.cards):
            card = self.cards[self.card_idx]
            label = QLabel(f"事件：{card['事件标题']}")
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label)

            hbox = QHBoxLayout()
            btn_left = QPushButton("左滑")
            btn_left.clicked.connect(lambda: self.choose(card, '左滑'))
            hbox.addWidget(btn_left)

            btn_right = QPushButton("右滑")
            btn_right.clicked.connect(lambda: self.choose(card, '右滑'))
            hbox.addWidget(btn_right)

            self.layout.addLayout(hbox)
        else:
            self.stage_idx += 1
            self.next_stage()

    def choose(self, card, direction):
        if direction == '左滑':
            desc = card['左滑描述']
            score = int(card['左滑分数'])
        else:
            desc = card['右滑描述']
            score = int(card['右滑分数'])
        self.score += score
        QMessageBox.information(self, "决策结果", f"{desc}\n当前评审分数：{self.score}")
        self.card_idx += 1
        self.next_card()

    def review_stage(self):
        self.clear_layout()
        label = QLabel("流程评审环节：")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        # 评审通过分数线
        if self.score >= 5:  # 可根据实际调整
            result = "评审通过！进入最终上线。"
            btn = QPushButton("最终上线")
            btn.clicked.connect(self.final_stage)
        else:
            result = "评审未通过，流程失败。"
            btn = QPushButton("查看失败原因")
            btn.clicked.connect(self.fail_stage)
        label2 = QLabel(result)
        label2.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label2)
        self.layout.addWidget(btn)

    def final_stage(self):
        self.clear_layout()
        label = QLabel("恭喜你，最终上线成功！\n可以选择玩一个MiniGame。")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        btn = QPushButton("进入MiniGame")
        btn.clicked.connect(self.mini_game)
        self.layout.addWidget(btn)

    def fail_stage(self):
        self.clear_layout()
        label = QLabel("很遗憾，流程评审失败。\n你可以选择重新开始。")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        btn = QPushButton("重新开始")
        btn.clicked.connect(self.restart_game)
        self.layout.addWidget(btn)

    def mini_game(self):
        self.clear_layout()
        label = QLabel("MiniGame：猜数字游戏\n请猜一个1-10之间的数字。")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        btn = QPushButton("开始猜数字")
        btn.clicked.connect(self.guess_number)
        self.layout.addWidget(btn)

    def guess_number(self):
        num = random.randint(1, 10)
        guess, ok = QMessageBox.getText(self, "猜数字", "输入你猜的数字（1-10）：")
        if ok:
            try:
                guess = int(guess)
                if guess == num:
                    QMessageBox.information(self, "结果", "恭喜你，猜对了！")
                else:
                    QMessageBox.information(self, "结果", f"很遗憾，正确答案是 {num}")
            except:
                QMessageBox.warning(self, "错误", "请输入有效数字！")
        self.restart_game()

    def restart_game(self):
        self.stage_idx = 0
        self.score = 0
        self.cards = []
        self.card_idx = 0
        self.init_intro()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ReignsExcelDemo()
    demo.show()
    sys.exit(app.exec_())